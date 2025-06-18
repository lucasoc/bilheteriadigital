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
        rds = carregar_rds()
        vagas = rds.get("vagas", {})
        now = int(time.time())

        # Inicializa lista se não existir
        if req.cargoId not in reservas:
            reservas[req.cargoId] = []

        # Remove reservas expiradas
        reservas[req.cargoId] = [
            r for r in reservas[req.cargoId]
            if r["expirationTime"] > now
        ]

        if vagas.get(req.cargoId, 0) <= len(reservas[req.cargoId]):
            return {
                "sucesso": False,
                "expiradoAnteriormente": False,
                "motivo": "Todas as vagas estão reservadas ou preenchidas"
            }

        expiration_time = now + 60
        reservas[req.cargoId].append({
            "usuarioId": req.usuarioId,
            "expirationTime": expiration_time
        })

        salvar_reservas(reservas)

        return {
            "sucesso": True,
            "expiradoAnteriormente": False,
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
        vagas = rds.get("vagas", {})
        now = int(time.time())

        ocupados = []

        for cargo_id, total_vagas in vagas.items():
            reservas_ativas = [
                r for r in reservas.get(cargo_id, [])
                if r["expirationTime"] > now
            ]
            if len(reservas_ativas) >= total_vagas:
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
    vagas = rds.get("vagas", {})

    if vagas.get(req.cargoId, 0) <= 0:
        raise HTTPException(
            status_code=400,
            detail=f"Não há mais vagas disponíveis para {req.cargoId}"
        )

    # Verificação e baixa no estoque
    for nome, quantidade in req.produtos.items():
        if nome not in estoque or estoque[nome] < quantidade:
            raise HTTPException(
                status_code=400,
                detail=f"Produto '{nome}' não tem quantidade suficiente."
            )
        estoque[nome] -= quantidade

    # Reduz uma vaga
    vagas[req.cargoId] -= 1

    # Remove reserva do usuário
    reservas = carregar_reservas()
    if req.cargoId in reservas:
        reservas[req.cargoId] = [
            r for r in reservas[req.cargoId]
            if r["usuarioId"] != req.usuarioId
        ]
    salvar_reservas(reservas)

    # Salva a compra
    compras.append({
        "usuarioId": req.usuarioId,
        "cargoId": req.cargoId,
        "produtos": req.produtos
    })

    salvar_rds({
        "estoque": estoque,
        "compras": compras,
        "vagas": vagas
    })

    return {"success": True}
