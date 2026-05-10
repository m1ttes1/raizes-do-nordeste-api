"""
Ponto de entrada da aplicação FastAPI — Raízes do Nordeste.

O Swagger (/docs) e o ReDoc (/redoc) são gerados automaticamente
pelo FastAPI a partir dos schemas Pydantic, atendendo ao RNF04.
"""
from fastapi import FastAPI

from api.routers import usuarios

app = FastAPI(
    title="Raízes do Nordeste API",
    description=(
        "Sistema de gestão de pedidos, estoque e fidelização da Raízes do Nordeste. "
        "Suporta pedidos multicanal: APP, TOTEM, BALCAO, PICKUP e WEB."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.include_router(usuarios.router)


@app.get("/", tags=["health"], summary="Health check")
def health_check():
    return {"status": "ok", "service": "Raízes do Nordeste API", "version": "1.0.0"}
