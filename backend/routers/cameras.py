from fastapi import APIRouter, HTTPException
from typing import Dict, List
import uuid

from schemas.camera import CameraCreate, CameraResponse, CameraUpdate

router = APIRouter(prefix="/api/cameras", tags=["cameras"])

# Armazenamento em memória das câmeras (em produção, usar banco de dados)
cameras_db: Dict[str, CameraResponse] = {}


@router.get("/", response_model=List[CameraResponse])
async def list_cameras():
    """Lista todas as câmeras cadastradas."""
    return list(cameras_db.values())


@router.get("/{camera_id}", response_model=CameraResponse)
async def get_camera(camera_id: str):
    """Obtém uma câmera específica pelo ID."""
    if camera_id not in cameras_db:
        raise HTTPException(status_code=404, detail="Câmera não encontrada")
    return cameras_db[camera_id]


@router.post("/", response_model=CameraResponse, status_code=201)
async def create_camera(camera: CameraCreate):
    """Cria uma nova câmera."""
    # Verificar se já existe uma câmera com o mesmo nome
    for existing_camera in cameras_db.values():
        if existing_camera.name.lower() == camera.name.lower():
            raise HTTPException(
                status_code=400,
                detail=f"Já existe uma câmera com o nome '{camera.name}'"
            )
    
    # Criar nova câmera
    camera_id = str(uuid.uuid4())
    new_camera = CameraResponse(
        id=camera_id,
        name=camera.name,
        url=camera.url,
        fps=camera.fps,
        active=True
    )
    
    cameras_db[camera_id] = new_camera
    return new_camera


@router.put("/{camera_id}", response_model=CameraResponse)
async def update_camera(camera_id: str, camera_update: CameraUpdate):
    """Atualiza uma câmera existente."""
    if camera_id not in cameras_db:
        raise HTTPException(status_code=404, detail="Câmera não encontrada")
    
    existing_camera = cameras_db[camera_id]
    
    # Verificar nome duplicado se estiver atualizando o nome
    if camera_update.name and camera_update.name.lower() != existing_camera.name.lower():
        for cam in cameras_db.values():
            if cam.id != camera_id and cam.name.lower() == camera_update.name.lower():
                raise HTTPException(
                    status_code=400,
                    detail=f"Já existe uma câmera com o nome '{camera_update.name}'"
                )
    
    # Atualizar campos
    update_data = camera_update.model_dump(exclude_unset=True)
    updated_camera = CameraResponse(
        id=existing_camera.id,
        name=update_data.get("name", existing_camera.name),
        url=update_data.get("url", existing_camera.url),
        fps=update_data.get("fps", existing_camera.fps),
        active=update_data.get("active", existing_camera.active)
    )
    
    cameras_db[camera_id] = updated_camera
    return updated_camera


@router.delete("/{camera_id}")
async def delete_camera(camera_id: str):
    """Remove uma câmera."""
    if camera_id not in cameras_db:
        raise HTTPException(status_code=404, detail="Câmera não encontrada")
    
    del cameras_db[camera_id]
    return {"message": "Câmera removida com sucesso"}


@router.get("/names/list", response_model=List[str])
async def list_camera_names():
    """Lista apenas os nomes das câmeras cadastradas."""
    return [camera.name for camera in cameras_db.values()]

