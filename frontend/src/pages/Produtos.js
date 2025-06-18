import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import authFetch from "../utils/authFetch";

function Produtos() {
  const location = useLocation();
  const navigate = useNavigate();
  const { cargo, expirationTime, usuarioId, pedidoId } = location.state || {};

  const [produtos, setProdutos] = useState({});
  const [selecionados, setSelecionados] = useState({});
  const [tempoRestante, setTempoRestante] = useState(0);

  useEffect(() => {
    const agora = Math.floor(Date.now() / 1000);
    const tempo = expirationTime ? expirationTime - agora : 0;
    setTempoRestante(tempo > 0 ? tempo : 0);

    const intervalo = setInterval(() => {
      setTempoRestante((prev) => {
        if (prev <= 1) {
          clearInterval(intervalo);
          alert("Sua reserva expirou. Retornando à tela inicial.");
          navigate("/Home", { state: { usuarioId: usuarioId } });
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(intervalo);
  }, [expirationTime, navigate]);

  useEffect(() => {
    const intervaloVerificacao = setInterval(async () => {
      try {
        const response = await authFetch(`http://localhost:8000/consulta-reserva?usuarioId=${usuarioId}&pedidoId=${pedidoId}&cargoId=${cargo}`);
  
        const data = await response.json();
  
        if (!data.reservaValida) {
          clearInterval(intervaloVerificacao);
          alert("Sua reserva expirou ou foi invalidada. Redirecionando...");
          navigate("/Home", { state: { usuarioId: usuarioId } });
        }
      } catch (error) {
        console.error("Erro ao consultar reserva:", error);
      }
    }, 10000); // 10 segundos
  
    return () => clearInterval(intervaloVerificacao);
  }, [usuarioId, pedidoId, cargo, navigate]);

  useEffect(() => {
    const carregarProdutos = async () => {
      const response = await authFetch("http://localhost:8000/consulta-produtos");
      const data = await response.json();
      setProdutos(data);
    };
    carregarProdutos();
  }, []);

  const alterarQuantidade = (nome, delta) => {
    setSelecionados((prev) => {
      const atual = prev[nome] || 0;
      const novo = Math.max(0, atual + delta);
      return { ...prev, [nome]: novo };
    });
  };

  const finalizar = async () => {
    try {
      const response = await authFetch("http://localhost:8000/finaliza-compra", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          usuarioId,
          cargoId: cargo,
          pedidoId: pedidoId,
          produtos: selecionados,
        }),
      });
      const data = await response.json();
      if (data.success) {
        alert("Inscrição finalizada com sucesso!");
        navigate("/Home", { state: { usuarioId: usuarioId } });
      } else {
        alert("Erro ao finalizar.");
      }
    } catch (error) {
      alert("Falha ao enviar inscrição.");
    }
  };

  const formatarTempo = (segundos) => {
    const min = Math.floor(segundos / 60).toString().padStart(2, "0");
    const seg = (segundos % 60).toString().padStart(2, "0");
    return `${min}:${seg}`;
  };

  return (
    <div
      style={{
        backgroundColor: "#001E4C",
        minHeight: "100vh",
        padding: "2rem",
        color: "#FFF",
        fontFamily: "'Segoe UI', sans-serif",
      }}
    >
      <h1
        style={{
          color: "#FF6A13",
          fontSize: "2.5rem",
          textAlign: "center",
          marginBottom: "1rem",
        }}
      >
        Escolha de Produtos Adicionais
      </h1>

      <p
        style={{
          textAlign: "center",
          fontSize: "1.2rem",
          fontWeight: "bold",
          color: "#FF6A13",
          marginBottom: "2rem",
        }}
      >
        Tempo restante para finalizar: {formatarTempo(tempoRestante)}
      </p>

      <div
        style={{
          maxWidth: "900px",
          margin: "0 auto",
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
          gap: "1.5rem",
        }}
      >
        {Object.entries(produtos).map(([nome, qtdDisponivel]) => (
          <div
            key={nome}
            style={{
              backgroundColor: "#FFF",
              color: "#001E4C",
              padding: "1.2rem",
              borderRadius: "16px",
              boxShadow: "0 4px 16px rgba(0, 0, 0, 0.2)",
            }}
          >
            <h3 style={{ marginBottom: "0.5rem" }}>{nome}</h3>
            <p style={{ marginBottom: "0.5rem" }}>
              Disponível: {qtdDisponivel}
            </p>

            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <button
                onClick={() => alterarQuantidade(nome, -1)}
                style={{
                  backgroundColor: "#FF6A13",
                  border: "none",
                  borderRadius: "8px",
                  padding: "0.3rem 0.8rem",
                  color: "#FFF",
                  cursor: "pointer",
                }}
              >
                -
              </button>
              <span style={{ fontSize: "1.2rem" }}>{selecionados[nome] || 0}</span>
              <button
                onClick={() => alterarQuantidade(nome, 1)}
                style={{
                  backgroundColor: "#FF6A13",
                  border: "none",
                  borderRadius: "8px",
                  padding: "0.3rem 0.8rem",
                  color: "#FFF",
                  cursor: "pointer",
                }}
                disabled={(selecionados[nome] || 0) >= qtdDisponivel}
              >
                +
              </button>
            </div>
          </div>
        ))}
      </div>

      <div style={{ textAlign: "center", marginTop: "3rem" }}>
        <button
          onClick={finalizar}
          style={{
            backgroundColor: "#FF6A13",
            color: "#FFF",
            border: "none",
            padding: "1rem 2.5rem",
            borderRadius: "12px",
            fontSize: "1.2rem",
            fontWeight: "bold",
            cursor: "pointer",
            boxShadow: "0 4px 10px rgba(0, 0, 0, 0.2)",
          }}
        >
          Finalizar Inscrição
        </button>
      </div>
    </div>
  );
}

export default Produtos;
