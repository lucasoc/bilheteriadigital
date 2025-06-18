import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [erro, setErro] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setErro("");

    try {
      const response = await fetch("http://localhost:8000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (response.ok && data.access_token) {
        localStorage.setItem("token", data.access_token);
        navigate("/Home", { state: { usuarioId: username } });
      } else {
        setErro("Usuário ou senha inválidos.");
      }
    } catch (err) {
      setErro("Erro ao tentar fazer login.");
    }
  };

  return (
    <div
      style={{
        backgroundColor: "#002d62",
        minHeight: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <div
        style={{
          backgroundColor: "#fff",
          padding: "2rem",
          borderRadius: "1rem",
          boxShadow: "0 4px 16px rgba(0,0,0,0.2)",
          width: "100%",
          maxWidth: "400px",
        }}
      >
        <div style={{ textAlign: "center", marginBottom: "1.5rem" }}>
          <div
            style={{
              backgroundColor: "#ff7a00",
              color: "white",
              fontSize: "1.8rem",
              fontWeight: "bold",
              padding: "1rem",
              borderRadius: "0.75rem",
              display: "inline-block",
            }}
          >
            Case SR
          </div>
        </div>

        <form onSubmit={handleLogin}>
          <div style={{ marginBottom: "1rem" }}>
            <label style={{ fontWeight: "600" }}>Usuário</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              style={{
                width: "100%",
                padding: "0.5rem",
                marginTop: "0.25rem",
                borderRadius: "0.5rem",
                border: "1px solid #ccc",
              }}
            />
          </div>

          <div style={{ marginBottom: "1rem" }}>
            <label style={{ fontWeight: "600" }}>Senha</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              style={{
                width: "100%",
                padding: "0.5rem",
                marginTop: "0.25rem",
                borderRadius: "0.5rem",
                border: "1px solid #ccc",
              }}
            />
          </div>

          {erro && (
            <p style={{ color: "red", textAlign: "center", marginBottom: "1rem" }}>
              {erro}
            </p>
          )}

          <button
            type="submit"
            style={{
              width: "100%",
              padding: "0.75rem",
              backgroundColor: "#ff7a00",
              color: "white",
              fontWeight: "bold",
              border: "none",
              borderRadius: "0.5rem",
              cursor: "pointer",
            }}
          >
            Entrar
          </button>
        </form>
      </div>
    </div>
  );
}

export default Login;
