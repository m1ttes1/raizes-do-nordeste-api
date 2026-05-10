from fastapi import FastAPI

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


@app.get("/", tags=["health"], summary="Health check")
def health_check():
    return {"status": "ok", "service": "Raízes do Nordeste API", "version": "1.0.0"}
