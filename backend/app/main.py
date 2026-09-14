from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.atendimentos import router as atendimentos_router
from app.api.auth import router as auth_router
from app.api.clientes import router as clientes_router
from app.api.pedidos import router as pedidos_router


app = FastAPI(
    title="SmartFlow AI",
    description="Central de atendimento inteligente com IA",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(atendimentos_router)
app.include_router(auth_router)
app.include_router(clientes_router)
app.include_router(pedidos_router)


@app.get("/")
def home():
    return {
        "status": "online",
        "app": "SmartFlow AI",
    }
