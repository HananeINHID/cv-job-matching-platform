import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import API from "../services/api";

function LoginPage() {
  const [email, setEmail]       = useState("");
  const [password, setPassword] = useState("");
  const [erreur, setErreur]     = useState("");
  const [darkMode, setDarkMode] = useState(false);

  const navigate = useNavigate();

  // Détecte le mode système au démarrage
  useEffect(() => {
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    setDarkMode(prefersDark);
  }, []);

  const handleLogin = async () => {
    setErreur("");
    if (!email || !password) {
      setErreur("Veuillez remplir tous les champs.");
      return;
    }
    try {
      const response = await API.post("/token/", {
        username: email,
        password: password,
      });
      localStorage.setItem("token", response.data.access);
      localStorage.setItem("refresh_token", response.data.refresh);
      navigate("/dashboard");
    } catch (error) {
      setErreur("Nom d'utilisateur ou mot de passe incorrect.");
    }
  };

  const dm = darkMode;

  return (
    <div style={{
      minHeight: "100vh",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      background: dm
        ? "linear-gradient(135deg, #0f0c29, #302b63, #24243e)"
        : "linear-gradient(135deg, #e0c3fc, #8ec5fc, #d4fc79)",
      transition: "background 0.5s ease",
      padding: "1rem",
    }}>

      {/* Bouton dark/light mode */}
      <button
        onClick={() => setDarkMode(!dm)}
        style={{
          position: "fixed",
          top: "20px",
          right: "20px",
          width: "44px",
          height: "44px",
          borderRadius: "50%",
          border: "none",
          backgroundColor: dm ? "rgba(255,255,255,0.15)" : "rgba(0,0,0,0.15)",
          fontSize: "20px",
          cursor: "pointer",
          backdropFilter: "blur(10px)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        {dm ? "☀️" : "🌙"}
      </button>

      {/* Carte principale */}
      <div style={{
        backgroundColor: dm ? "rgba(255,255,255,0.07)" : "rgba(255,255,255,0.75)",
        backdropFilter: "blur(20px)",
        padding: "2.5rem",
        borderRadius: "24px",
        border: dm ? "1px solid rgba(255,255,255,0.15)" : "1px solid rgba(255,255,255,0.6)",
        width: "100%",
        maxWidth: "420px",
        boxShadow: dm
          ? "0 25px 50px rgba(0,0,0,0.5)"
          : "0 25px 50px rgba(100,100,200,0.2)",
      }}>

        {/* Logo / Titre */}
        <div style={{ textAlign: "center", marginBottom: "2rem" }}>
          <div style={{
            width: "60px",
            height: "60px",
            borderRadius: "16px",
            background: "linear-gradient(135deg, #667eea, #764ba2)",
            margin: "0 auto 1rem",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: "28px",
          }}>
            📄
          </div>
          <h1 style={{
            fontSize: "26px",
            fontWeight: "700",
            background: "linear-gradient(135deg, #667eea, #764ba2)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            margin: 0,
          }}>
            CV Matching
          </h1>
          <p style={{
            fontSize: "14px",
            color: dm ? "rgba(255,255,255,0.5)" : "#888",
            marginTop: "6px",
          }}>
            Connectez-vous à votre compte
          </p>
        </div>

        {/* Message erreur */}
        {erreur && (
          <div style={{
            backgroundColor: dm ? "rgba(220,50,50,0.2)" : "#FCEBEB",
            border: "1px solid rgba(220,50,50,0.3)",
            color: dm ? "#ff8080" : "#A32D2D",
            padding: "12px",
            borderRadius: "12px",
            fontSize: "13px",
            marginBottom: "20px",
            textAlign: "center",
          }}>
            {erreur}
          </div>
        )}

        {/* Champ username */}
        <div style={{ marginBottom: "16px" }}>
          <label style={{
            display: "block",
            fontSize: "13px",
            fontWeight: "500",
            marginBottom: "8px",
            color: dm ? "rgba(255,255,255,0.7)" : "#444",
          }}>
            Nom d'utilisateur
          </label>
          <input
            type="text"
            placeholder="votre_username"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleLogin()}
            style={{
              width: "100%",
              padding: "12px 16px",
              borderRadius: "12px",
              border: dm
                ? "1px solid rgba(255,255,255,0.15)"
                : "1px solid rgba(102,126,234,0.3)",
              backgroundColor: dm ? "rgba(255,255,255,0.08)" : "rgba(255,255,255,0.8)",
              color: dm ? "white" : "#333",
              fontSize: "14px",
              boxSizing: "border-box",
              outline: "none",
            }}
          />
        </div>

        {/* Champ mot de passe */}
        <div style={{ marginBottom: "24px" }}>
          <label style={{
            display: "block",
            fontSize: "13px",
            fontWeight: "500",
            marginBottom: "8px",
            color: dm ? "rgba(255,255,255,0.7)" : "#444",
          }}>
            Mot de passe
          </label>
          <input
            type="password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleLogin()}
            style={{
              width: "100%",
              padding: "12px 16px",
              borderRadius: "12px",
              border: dm
                ? "1px solid rgba(255,255,255,0.15)"
                : "1px solid rgba(102,126,234,0.3)",
              backgroundColor: dm ? "rgba(255,255,255,0.08)" : "rgba(255,255,255,0.8)",
              color: dm ? "white" : "#333",
              fontSize: "14px",
              boxSizing: "border-box",
              outline: "none",
            }}
          />
        </div>

        {/* Bouton connexion */}
        <button
          onClick={handleLogin}
          style={{
            width: "100%",
            padding: "14px",
            background: "linear-gradient(135deg, #667eea, #764ba2)",
            color: "white",
            border: "none",
            borderRadius: "12px",
            fontSize: "15px",
            fontWeight: "600",
            cursor: "pointer",
            letterSpacing: "0.5px",
            transition: "opacity 0.2s",
          }}
          onMouseEnter={(e) => e.target.style.opacity = "0.9"}
          onMouseLeave={(e) => e.target.style.opacity = "1"}
        >
          Se connecter →
        </button>

        {/* Lien inscription */}
        <p style={{
          textAlign: "center",
          fontSize: "13px",
          marginTop: "20px",
          color: dm ? "rgba(255,255,255,0.5)" : "#888",
        }}>
          Pas encore de compte ?{" "}
          <Link to="/register" style={{
            color: "#667eea",
            textDecoration: "none",
            fontWeight: "600",
          }}>
            S'inscrire
          </Link>
        </p>

      </div>
    </div>
  );
}

export default LoginPage;