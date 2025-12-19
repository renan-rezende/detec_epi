import cv2
import numpy as np
from ultralytics import YOLO
from typing import Tuple, List, Dict
import threading
import os


class EPIDetector:
    """
    Detector de EPIs usando YOLOv8 com modelo customizado.
    Classes detectadas:
        0: helmet (Capacete)
        1: gloves (Luvas)
        2: vest (Colete)
        3: boots (Botas)
        4: goggles (Óculos)
        5: none (Nenhum EPI)
        6: Person (Pessoa)
        7: no_helmet (Sem Capacete)
        8: no_goggle (Sem Óculos)
        9: no_gloves (Sem Luvas)
        10: no_boots (Sem Botas)
    """
    
    # Mapeamento das classes do modelo para exibição
    CLASS_CONFIG = {
        0: {"name": "Capacete", "color": (0, 255, 0), "is_epi": True, "is_violation": False},
        1: {"name": "Luvas", "color": (0, 255, 255), "is_epi": True, "is_violation": False},
        2: {"name": "Colete", "color": (255, 165, 0), "is_epi": True, "is_violation": False},
        3: {"name": "Botas", "color": (255, 0, 255), "is_epi": True, "is_violation": False},
        4: {"name": "Óculos", "color": (128, 255, 0), "is_epi": True, "is_violation": False},
        5: {"name": "Sem EPI", "color": (0, 0, 255), "is_epi": False, "is_violation": True},
        6: {"name": "Pessoa", "color": (255, 128, 0), "is_epi": False, "is_violation": False},
        7: {"name": "Sem Capacete", "color": (0, 0, 255), "is_epi": False, "is_violation": True},
        8: {"name": "Sem Óculos", "color": (0, 0, 200), "is_epi": False, "is_violation": True},
        9: {"name": "Sem Luvas", "color": (0, 0, 180), "is_epi": False, "is_violation": True},
        10: {"name": "Sem Botas", "color": (0, 0, 160), "is_epi": False, "is_violation": True},
    }
    
    def __init__(self, model_path: str = None):
        """
        Inicializa o detector com o modelo YOLOv8 de EPI.
        
        Args:
            model_path: Caminho para o modelo. Se None, usa o modelo padrão de EPI.
        """
        self.lock = threading.Lock()
        
        # Usar modelo de EPI na pasta models
        if model_path is None:
            model_path = os.path.join(os.path.dirname(__file__), "model_EPI.pt")
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modelo não encontrado: {model_path}")
        
        self.model = YOLO(model_path)
        print(f"✅ Modelo de EPI carregado: {model_path}")
        
        # Verificar classes do modelo
        if hasattr(self.model, 'names'):
            print(f"📋 Classes do modelo: {self.model.names}")
    
    def get_class_info(self, class_id: int) -> Dict:
        """Obtém informações da classe pelo ID."""
        return self.CLASS_CONFIG.get(class_id, {
            "name": f"Classe {class_id}",
            "color": (128, 128, 128),
            "is_epi": False,
            "is_violation": False
        })
    
    def detect(self, frame: np.ndarray, confidence: float = 0.5) -> Tuple[np.ndarray, List[Dict]]:
        """
        Detecta EPIs em um frame.
        
        Args:
            frame: Frame de vídeo (BGR)
            confidence: Limiar de confiança para detecções
            
        Returns:
            Tuple contendo o frame anotado e lista de detecções
        """
        with self.lock:
            # Realizar detecção
            results = self.model(frame, conf=confidence, verbose=False)
            
            detections = []
            annotated_frame = frame.copy()
            
            for result in results:
                boxes = result.boxes
                
                if boxes is not None:
                    for box in boxes:
                        # Extrair coordenadas
                        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                        conf = float(box.conf[0])
                        cls_id = int(box.cls[0])
                        
                        # Obter informações da classe
                        class_info = self.get_class_info(cls_id)
                        
                        # Adicionar à lista de detecções
                        detections.append({
                            "class": class_info["name"],
                            "class_id": cls_id,
                            "confidence": conf,
                            "bbox": [x1, y1, x2, y2],
                            "is_epi": class_info["is_epi"],
                            "is_violation": class_info["is_violation"]
                        })
                        
                        # Cor e espessura baseada no tipo
                        color = class_info["color"]
                        thickness = 3 if class_info["is_violation"] else 2
                        
                        # Desenhar bounding box
                        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, thickness)
                        
                        # Desenhar label
                        label = f"{class_info['name']}: {conf:.0%}"
                        label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                        
                        # Background do label
                        label_y = max(y1 - 10, label_size[1] + 10)
                        cv2.rectangle(
                            annotated_frame,
                            (x1, label_y - label_size[1] - 5),
                            (x1 + label_size[0] + 5, label_y + 5),
                            color,
                            -1
                        )
                        
                        # Texto do label
                        cv2.putText(
                            annotated_frame,
                            label,
                            (x1 + 2, label_y),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (255, 255, 255),
                            2
                        )
            
            return annotated_frame, detections
    
    def detect_with_epi_check(self, frame: np.ndarray, confidence: float = 0.5) -> Tuple[np.ndarray, List[Dict], List[str]]:
        """
        Detecta EPIs e gera alertas para violações de segurança.
        
        Args:
            frame: Frame de vídeo (BGR)
            confidence: Limiar de confiança
            
        Returns:
            Tuple com frame anotado, detecções e lista de alertas
        """
        annotated_frame, detections = self.detect(frame, confidence)
        alerts = []
        
        # Contar violações por tipo
        violations = {
            "Sem Capacete": 0,
            "Sem Óculos": 0,
            "Sem Luvas": 0,
            "Sem Botas": 0,
            "Sem EPI": 0,
        }
        
        for d in detections:
            if d["is_violation"] and d["class"] in violations:
                violations[d["class"]] += 1
        
        # Gerar alertas para cada tipo de violação
        for violation_type, count in violations.items():
            if count > 0:
                alerts.append(f"⚠️ {count}x {violation_type}")
        
        # Contar EPIs detectados
        epis = {}
        for d in detections:
            if d["is_epi"]:
                epis[d["class"]] = epis.get(d["class"], 0) + 1
        
        # Desenhar painel de status no frame
        self._draw_status_panel(annotated_frame, detections, alerts)
        
        return annotated_frame, detections, alerts
    
    def _draw_status_panel(self, frame: np.ndarray, detections: List[Dict], alerts: List[str]):
        """Desenha painel de status no frame."""
        h, w = frame.shape[:2]
        
        # Contar EPIs e violações
        epi_count = sum(1 for d in detections if d["is_epi"])
        violation_count = sum(1 for d in detections if d["is_violation"])
        person_count = sum(1 for d in detections if d["class"] == "Pessoa")
        
        # Painel superior esquerdo - Alertas
        if alerts:
            panel_height = 30 + len(alerts) * 25
            cv2.rectangle(frame, (5, 5), (300, panel_height), (0, 0, 0), -1)
            cv2.rectangle(frame, (5, 5), (300, panel_height), (0, 0, 255), 2)
            
            cv2.putText(frame, "ALERTAS DE SEGURANCA", (10, 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            
            y_pos = 50
            for alert in alerts:
                cv2.putText(frame, alert, (15, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                y_pos += 25
        
        # Painel inferior - Resumo
        panel_y = h - 60
        cv2.rectangle(frame, (5, panel_y), (350, h - 5), (0, 0, 0), -1)
        cv2.rectangle(frame, (5, panel_y), (350, h - 5), (255, 255, 255), 1)
        
        # Status geral
        status_color = (0, 255, 0) if violation_count == 0 else (0, 0, 255)
        status_text = "OK" if violation_count == 0 else f"{violation_count} VIOLACOES"
        
        cv2.putText(frame, f"Pessoas: {person_count}", (15, panel_y + 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, f"EPIs: {epi_count}", (130, panel_y + 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.putText(frame, f"Status: {status_text}", (15, panel_y + 45),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, status_color, 2)


# Singleton do detector para reutilização
_detector_instance = None


def get_detector() -> EPIDetector:
    """Retorna instância singleton do detector."""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = EPIDetector()
    return _detector_instance


def reset_detector():
    """Reseta o detector para recarregar com novo modelo."""
    global _detector_instance
    _detector_instance = None
