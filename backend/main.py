from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import time
import os

app = FastAPI()

# CORS para permitir chamadas do frontend React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ajuste para seu domínio em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ReservaRequest(BaseModel):
    cargoId: str
    usuarioId: str

class FinalizaCompraRequest(BaseModel):
    usuarioId: str
    cargoId: str
    produtos: dict

# Simulação de banco de dados (arquivo local)
DYNAMODB = "dynamodb.json"
RDS_FILE = "rds.json"

def carregar_reservas():
    if not os.path.exists(DYNAMODB):
        return {}
    with open(DYNAMODB, "r") as f:
        return json.load(f)

def salvar_reservas(reservas):
    with open(DYNAMODB, "w") as f:
        json.dump(reservas, f)

def carregar_rds():
    if not os.path.exists(RDS_FILE):
        return {"estoque": {}, "compras": []}
    with open(RDS_FILE, "r") as f:
        return json.load(f)

def salvar_rds(data):
    with open(RDS_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.post("/reserva")
async def lambdaCriaReserva(req: ReservaRequest):
    try:
        reservas = carregar_reservas()
        now = int(time.time())
        expirado = False
        print(req)
        if req.cargoId in reservas:
            if reservas[req.cargoId]["expirationTime"] > now:
                return {
            "success": False,
            "expiradoAnteriormente": expirado,
            "expirationTime": expiration_time
        }
            else:
                expirado = True

        expiration_time = now + 60
        reservas[req.cargoId] = {
            "usuarioId": req.usuarioId,
            "expirationTime": expiration_time
        }

        salvar_reservas(reservas)

        return {
            "sucesso": True,
            "expiradoAnteriormente": expirado,
            "expirationTime": expiration_time
        }

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Erro interno")

@app.get("/consulta-bilhete")
async def lambdaConsultaBilhete():
    try:
        reservas = carregar_reservas()
        rds = carregar_rds()
        compras = rds.get("compras", [])
        now = int(time.time())

        ocupados = []

        for cargo_id, dados in reservas.items():
            if dados["expirationTime"] > now:
                ocupados.append(cargo_id)

        return {"ocupados": ocupados}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Erro ao consultar reservas")

@app.get("/consulta-produtos")
async def lambdaConsultaProdutos():
    rds = carregar_rds()
    return rds.get("estoque", {})

@app.post("/finaliza-compra")
async def lambdaFinalizaCompra(req: FinalizaCompraRequest):
    rds = carregar_rds()
    estoque = rds.get("estoque", {})
    compras = rds.get("compras", [])

    # Verificação de estoque
    for nome, quantidade in req.produtos.items():
        if nome not in estoque or estoque[nome] < quantidade:
            raise HTTPException(
                status_code=400,
                detail=f"Produto '{nome}' não tem quantidade suficiente."
            )
        estoque[nome] -= quantidade

    # Adiciona compra ao histórico
    compras.append({
        "usuarioId": req.usuarioId,
        "cargoId": req.cargoId,
        "produtos": req.produtos
    })

    # Salva alterações
    salvar_rds({
        "estoque": estoque,
        "compras": compras
    })

    return {"success": True}