from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from routers import cameras, stream

# Criar aplicação FastAPI
app = FastAPI(
    title="Sistema de Detecção de EPIs",
    description="API para detecção de Equipamentos de Proteção Individual usando YOLOv8",
    version="1.0.0"
)

# Configurar CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(cameras.router)
app.include_router(stream.router)


@app.get("/")
async def root():
    """Endpoint raiz da API."""
    return {
        "message": "Sistema de Detecção de EPIs",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Verifica se a API está funcionando."""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

