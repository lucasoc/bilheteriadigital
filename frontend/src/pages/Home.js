import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const opcoes = [
  { id: "junior", cargo: "Cargo Junior", cor: "#FFFFFF", texto: "#333" },
  { id: "pleno", cargo: "Cargo Pleno", cor: "#FFD700", texto: "#000" },
  { id: "senior", cargo: "Cargo Senior", cor: "#1E90FF", texto: "#FFF" },
  { id: "coordenador", cargo: "Cargo Coordenador", cor: "#000000", texto: "#FFF" },
];

function Home() {
  const navigate = useNavigate();
  const [ocupados, setOcupados] = useState([]);

  useEffect(() => {
    async function carregarOcupados() {
      try {
        const res = await fetch("http://localhost:8000/consulta-bilhete");
        const data = await res.json();
        setOcupados(data.ocupados || []);
      } catch (error) {
        console.error("Erro ao consultar cargos ocupados:", error);
      }
    }
    carregarOcupados();
  }, []);

  const reservarCargo = async (cargoId) => {
    if (ocupados.includes(cargoId)) return;
    
    try {
      const usuarioId = "lucas"
      const response = await fetch("http://localhost:8000/reserva", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          cargoId,
          usuarioId
        }),
      });
      const data = await response.json();
      if (data.sucesso) {
        navigate("/produtos", { state: { cargo: cargoId, expirationTime: data.expirationTime, usuarioId: usuarioId } });
      } else {
        alert("Esse cargo já está reservado!");
        window.location.reload();
      }
    } catch (error) {
      alert("Erro ao tentar reservar. Tente novamente.");
      window.location.reload();
    }
  };

  return (
    <div
      style={{
        backgroundColor: "#001E4C",
        minHeight: "100vh",
        textAlign: "center",
        padding: "2rem",
        fontFamily: "'Segoe UI', sans-serif",
      }}
    >
      <h1 style={{ color: "#FF6A13", fontSize: "2.8rem", marginBottom: "3rem" }}>
        Inscrição para processo seletivo
      </h1>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: "1.5rem",
          maxWidth: "900px",
          margin: "0 auto",
        }}
      >
        {opcoes.map((opcao) => {
          const reservado = ocupados.includes(opcao.id);
          return (
            <div
              key={opcao.id}
              style={{
                backgroundColor: reservado ? "#888" : opcao.cor,
                color: reservado ? "#ddd" : opcao.texto,
                padding: "1.5rem",
                borderRadius: "16px",
                fontWeight: "600",
                fontSize: "1.2rem",
                boxShadow: "0 4px 20px rgba(0, 0, 0, 0.2)",
                cursor: reservado ? "not-allowed" : "pointer",
                opacity: reservado ? 0.6 : 1,
              }}
              onClick={() => !reservado && reservarCargo(opcao.id)}
            >
              {opcao.cargo}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default Home;
