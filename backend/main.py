import json
import time
import os
from uuid import uuid4 as uuid
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from passlib.hash import bcrypt

from auth import criar_token, lambdaAuthorizer

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

class ConsultaReservaRequest(BaseModel):
    usuarioId: str
    pedidoId: str
    cargoId: str

class FinalizaCompraRequest(BaseModel):
    usuarioId: str
    cargoId: str
    pedidoId: str
    produtos: dict

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str

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
        return {"estoque": {}, "compras": [], "vagas": {}, "users": {}}
    with open(RDS_FILE, "r") as f:
        return json.load(f)

def salvar_rds(data):
    with open(RDS_FILE, "w") as f:
        json.dump(data, f, indent=2)


@app.post("/login", response_model=TokenResponse)
async def lambdaLogin(req: LoginRequest):
    rds = carregar_rds()
    usuarios = rds.get("users", {})
    
    user = usuarios.get(req.username)

    if not user or not bcrypt.verify(req.password, user["password"]):
        raise HTTPException(status_code=401, detail="Usuário ou senha inválidos")

    token = criar_token({"sub": req.username})
    return {"access_token": token}


@app.post("/reserva")
async def lambdaCriaReserva(req: ReservaRequest, payload=Depends(lambdaAuthorizer)):
    print(req)
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
        
        pedidoId = str(uuid())
        expiration_time = now + 60
        reservas[req.cargoId].append({
            "usuarioId": req.usuarioId,
            "expirationTime": expiration_time,
            "pedidoId": pedidoId
        })

        salvar_reservas(reservas)
        res = {
            "sucesso": True,
            "expiradoAnteriormente": False,
            "expirationTime": expiration_time,
            "pedidoId": pedidoId
        }
        print(res)

        return res

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Erro interno")


@app.get("/consulta-reserva")
async def lambdaConsultarReserva(usuarioId: str = Query(...), pedidoId: str = Query(...), cargoId: str = Query(...), payload=Depends(lambdaAuthorizer)):
    if not usuarioId or not pedidoId or not cargoId:
        raise HTTPException(status_code=400, detail="Os parametros usuarioId, pedidoId e cargoId sao obrigatorios")
    print(f"Usuarioid: {usuarioId}, pedidoId: {pedidoId}, cargoId: {cargoId}")
    reservas = carregar_reservas()
    now = int(time.time())

    cargo_reservas = reservas.get(cargoId, [])
    for r in cargo_reservas:
        if r["usuarioId"] == usuarioId and r["pedidoId"] == pedidoId:
            if r["expirationTime"] > now:
                res = {
                    "reservaValida": True,
                    "expirationTime": r["expirationTime"]
                }
                print(res)

                return res
            else:
                res = {
                    "reservaValida": False,
                    "expirado": True
                }
                print(res)

                return res

    res = {
        "reservaValida": False,
        "motivo": "Reserva não encontrada"
    }
    print(res)

    return res


@app.get("/consulta-bilhete")
async def lambdaConsultaBilhete(payload=Depends(lambdaAuthorizer)):
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

        res = {"ocupados": ocupados}
        print(res)

        return res
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Erro ao consultar reservas")


@app.get("/consulta-produtos")
async def lambdaConsultaProdutos(payload=Depends(lambdaAuthorizer)):
    rds = carregar_rds()
    res = rds.get("estoque", {})
    print(res)

    return res


@app.post("/finaliza-compra")
async def lambdaFinalizaCompra(req: FinalizaCompraRequest, payload=Depends(lambdaAuthorizer)):
    print(req)
    rds = carregar_rds()
    estoque = rds.get("estoque", {})
    compras = rds.get("compras", [])
    vagas = rds.get("vagas", {})
    users = rds.get("users", {})

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
            if r["pedidoId"] != req.pedidoId
        ]
    salvar_reservas(reservas)

    # Salva a compra
    compras.append({
        "usuarioId": req.usuarioId,
        "cargoId": req.cargoId,
        "pedidoId": req.pedidoId,
        "produtos": req.produtos,
        "statusPagamento": ""
    })

    salvar_rds({
        "estoque": estoque,
        "compras": compras,
        "vagas": vagas,
        "users": users
    })
    res = {"success": True}
    print(res)
    return res


@app.get("/conclui-pedido")
async def lambdaConcluiPedido(pedidoId: str = Query(...), statusId: str = Query(...)):
    if not pedidoId or not statusId:
        raise HTTPException(status_code=400, detail="Os parametros pedidoId e statusId sao obrigatorios")
    print(f"PedidoId: {pedidoId}, statusId: {statusId}")
    rds = carregar_rds()
    estoque = rds.get("estoque", {})
    compras = rds.get("compras", [])
    vagas = rds.get("vagas", {})
    users = rds.get("users", {})


    for compra in compras:
        if compra["pedidoId"] == pedidoId:
            compra["statusPagamento"] = statusId

            if statusId == "false":
                vagas[compra["cargoId"]] += 1
                for nome in compra["produtos"]:
                    estoque[nome] += compra["produtos"][nome]

    salvar_rds({
        "estoque": estoque,
        "compras": compras,
        "vagas": vagas,
        "users": users
    })

    res = {"success": True}
    print(res)
    
    return res
