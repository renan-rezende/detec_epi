from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import cv2
import time
from typing import Dict, Generator, List
import threading

from models.detector import get_detector
from routers.cameras import cameras_db

router = APIRouter(prefix="/api/stream", tags=["stream"])

# Armazenar VideoCapture ativos
active_streams: Dict[str, cv2.VideoCapture] = {}
stream_locks: Dict[str, threading.Lock] = {}

# Armazenar alertas/detecções por câmera para exibição na interface
camera_alerts: Dict[str, Dict] = {}
alerts_lock = threading.Lock()


def parse_video_source(url: str):
    """Converte a URL para o formato correto (int para webcam, string para outros)."""
    # Se for um número, é uma webcam
    if url.isdigit():
        return int(url)
    return url


def get_video_capture(camera_id: str, url: str) -> cv2.VideoCapture:
    """Obtém ou cria um VideoCapture para a câmera."""
    if camera_id not in active_streams or not active_streams[camera_id].isOpened():
        source = parse_video_source(url)
        print(f"Tentando abrir fonte de vídeo: {source} (tipo: {type(source).__name__})")
        
        cap = cv2.VideoCapture(source)
        
        if not cap.isOpened():
            error_msg = f"Não foi possível abrir o stream: '{url}'"
            if isinstance(source, int):
                error_msg += f" - Verifique se a webcam {source} está conectada"
            elif url.startswith("rtsp://"):
                error_msg += " - Verifique se o stream RTSP está acessível"
            elif url.startswith("http"):
                error_msg += " - Verifique se a URL está correta e acessível"
            else:
                error_msg += " - Verifique se o arquivo existe no caminho especificado"
            raise Exception(error_msg)
        
        print(f"Stream aberto com sucesso: {url}")
        active_streams[camera_id] = cap
        stream_locks[camera_id] = threading.Lock()
    return active_streams[camera_id]


def generate_frames(camera_id: str) -> Generator[bytes, None, None]:
    """Gera frames processados com detecção de EPIs."""
    if camera_id not in cameras_db:
        print(f"Câmera {camera_id} não encontrada no banco de dados")
        return
    
    camera = cameras_db[camera_id]
    
    try:
        detector = get_detector()
    except Exception as e:
        print(f"Erro ao carregar detector: {e}")
        return
    
    try:
        cap = get_video_capture(camera_id, camera.url)
    except Exception as e:
        print(f"Erro ao abrir stream: {e}")
        return
    
    # Calcular intervalo entre frames baseado no FPS desejado
    frame_interval = 1.0 / camera.fps if camera.fps > 0 else 1.0 / 5
    last_frame_time = 0
    
    while True:
        current_time = time.time()
        
        # Verificar se a câmera ainda existe e está ativa
        if camera_id not in cameras_db:
            break
        
        camera = cameras_db[camera_id]
        if not camera.active:
            time.sleep(0.1)
            continue
        
        # Controlar FPS
        if current_time - last_frame_time < frame_interval:
            time.sleep(0.01)
            continue
        
        # Capturar frame
        with stream_locks.get(camera_id, threading.Lock()):
            ret, frame = cap.read()
        
        if not ret:
            # Tentar reconectar
            print(f"Frame não recebido da câmera {camera.name}, tentando reconectar...")
            cap.release()
            try:
                source = parse_video_source(camera.url)
                cap = cv2.VideoCapture(source)
                if not cap.isOpened():
                    print(f"Falha ao reconectar à câmera {camera.name}")
                    time.sleep(2)
                    continue
                active_streams[camera_id] = cap
                print(f"Reconectado à câmera {camera.name}")
                time.sleep(1)
                continue
            except Exception as e:
                print(f"Erro ao reconectar: {e}")
                break
        
        # Redimensionar para performance
        frame = cv2.resize(frame, (640, 480))
        
        # Detectar EPIs
        try:
            annotated_frame, detections, alerts = detector.detect_with_epi_check(frame)
            
            # Armazenar alertas para consulta via API
            with alerts_lock:
                # Filtrar violações (classes 5, 7-10: Sem EPI, Sem Capacete, Sem Óculos, Sem Luvas, Sem Botas)
                violations = [d for d in detections if d.get("class_id") in [5, 7, 8, 9, 10] or d.get("is_violation", False)]
                
                # Debug: Mostrar detecções a cada 30 frames
                if int(current_time * 10) % 30 == 0 and detections:
                    print(f"🔍 Detecções: {len(detections)} | Violações: {len(violations)} | Classes: {[d.get('class_id') for d in detections]}")
                
                camera_alerts[camera_id] = {
                    "timestamp": current_time,
                    "alerts": alerts,
                    "violations": violations,
                    "has_violations": len(violations) > 0,
                    "person_count": sum(1 for d in detections if d.get("class_id") == 6),
                    "epi_count": sum(1 for d in detections if d.get("is_epi", False))
                }
        except Exception as e:
            print(f"Erro na detecção: {e}")
            annotated_frame = frame
        
        # Adicionar informações da câmera
        cv2.putText(
            annotated_frame,
            f"Camera: {camera.name} | FPS: {camera.fps}",
            (10, annotated_frame.shape[0] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1
        )
        
        # Codificar frame como JPEG
        ret, buffer = cv2.imencode('.jpg', annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if not ret:
            continue
        
        frame_bytes = buffer.tobytes()
        
        # Enviar frame no formato MJPEG
        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
        )
        
        last_frame_time = current_time


@router.get("/{camera_id}")
async def stream_camera(camera_id: str):
    """Stream de vídeo com detecções para uma câmera específica."""
    if camera_id not in cameras_db:
        raise HTTPException(status_code=404, detail="Câmera não encontrada")
    
    return StreamingResponse(
        generate_frames(camera_id),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@router.post("/{camera_id}/stop")
async def stop_stream(camera_id: str):
    """Para o stream de uma câmera."""
    if camera_id in active_streams:
        active_streams[camera_id].release()
        del active_streams[camera_id]
        if camera_id in stream_locks:
            del stream_locks[camera_id]
    return {"message": "Stream parado"}


@router.get("/{camera_id}/status")
async def stream_status(camera_id: str):
    """Verifica o status do stream de uma câmera."""
    if camera_id not in cameras_db:
        raise HTTPException(status_code=404, detail="Câmera não encontrada")
    
    is_streaming = camera_id in active_streams and active_streams[camera_id].isOpened()
    return {
        "camera_id": camera_id,
        "streaming": is_streaming,
        "active": cameras_db[camera_id].active
    }


@router.get("/{camera_id}/alerts")
async def get_camera_alerts(camera_id: str):
    """Retorna os alertas de violações detectadas em tempo real para uma câmera."""
    if camera_id not in cameras_db:
        raise HTTPException(status_code=404, detail="Câmera não encontrada")
    
    with alerts_lock:
        alerts_data = camera_alerts.get(camera_id, {
            "timestamp": 0,
            "alerts": [],
            "violations": [],
            "has_violations": False,
            "person_count": 0,
            "epi_count": 0
        })
    
    return {
        "camera_id": camera_id,
        **alerts_data
    }

