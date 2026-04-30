import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import API from "../services/api";

function LoginPage() {
  const [email, setEmail]       = useState("");
  const [password, setPassword] = useState("");
  const [erreur, setErreur]     = useState("");
  const [darkMode, setDarkMode] = useState(false);

  const navigate = useNavigate();

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

  // ── Palette "Croissance et Dynamisme" ──
  const couleurs = {
    // Fond
    pageBg:      darkMode ? "#0D1B2A"         : "#F0F4F8",
    // Carte
    cardBg:      darkMode ? "#1A2B3C"         : "#FFFFFF",
    cardBorder:  darkMode ? "#1E3A5F"         : "#E2EAF4",
    cardShadow:  darkMode
      ? "0 20px 60px rgba(0,0,0,0.5)"
      : "0 20px 60px rgba(14,90,130,0.1)",
    // Textes
    textePrimaire:   darkMode ? "#E8F1F8" : "#1A2B3C",
    texteSecondaire: darkMode ? "#7A9BB5" : "#5A7184",
    texteLabel:      darkMode ? "#A8C4D8" : "#3D5A73",
    // Inputs
    inputBg:     darkMode ? "#0F2030" : "#F7FAFD",
    inputBorder: darkMode ? "#1E3A5F" : "#C8DCF0",
    inputFocus:  "#0E8C8C",
    inputTexte:  darkMode ? "#E8F1F8" : "#1A2B3C",
    // Bouton principal (Teal)
    boutonBg:    "linear-gradient(135deg, #0E8C8C, #0A6B7C)",
    // Accent corail
    accent:      "#FF6B47",
    // Erreur
    erreurBg:    darkMode ? "rgba(220,80,60,0.15)" : "#FFF0EE",
    erreurBorder:"rgba(220,80,60,0.3)",
    erreurTexte: darkMode ? "#FF9080" : "#C0392B",
    // Logo gradient
    logoGradient:"linear-gradient(135deg, #0E8C8C, #0A6B7C)",
    // Toggle bg
    toggleBg:    darkMode ? "#1E3A5F" : "#E2EAF4",
  };

  return (
    <div style={{
      minHeight: "100vh",
      width: "100%",
      margin: 0,
      padding: 0,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      backgroundColor: couleurs.pageBg,
      transition: "background-color 0.4s ease",
      boxSizing: "border-box",
    }}>

      {/* ── Toggle Dark/Light ── */}
      <button
        onClick={() => setDarkMode(!darkMode)}
        title={darkMode ? "Mode clair" : "Mode sombre"}
        style={{
          position: "fixed",
          top: "20px",
          right: "20px",
          width: "42px",
          height: "42px",
          borderRadius: "50%",
          border: `1px solid ${couleurs.cardBorder}`,
          backgroundColor: couleurs.toggleBg,
          fontSize: "18px",
          cursor: "pointer",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          transition: "all 0.3s ease",
          zIndex: 100,
        }}
      >
        {darkMode ? "☀️" : "🌙"}
      </button>

      {/* ── Carte Login ── */}
      <div style={{
        backgroundColor: couleurs.cardBg,
        border: `1px solid ${couleurs.cardBorder}`,
        borderRadius: "20px",
        padding: "2.5rem",
        width: "100%",
        maxWidth: "420px",
        boxShadow: couleurs.cardShadow,
        transition: "all 0.4s ease",
        margin: "1rem",
      }}>

        {/* ── En-tête ── */}
        <div style={{ textAlign: "center", marginBottom: "2rem" }}>
          <div style={{
            width: "56px",
            height: "56px",
            borderRadius: "14px",
            background: couleurs.logoGradient,
            margin: "0 auto 1rem",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: "26px",
            boxShadow: "0 8px 20px rgba(14,140,140,0.3)",
          }}>
            💼
          </div>
          <h1 style={{
            fontSize: "24px",
            fontWeight: "700",
            color: couleurs.textePrimaire,
            margin: "0 0 6px 0",
            letterSpacing: "-0.3px",
          }}>
            CV Matching
          </h1>
          <p style={{
            fontSize: "14px",
            color: couleurs.texteSecondaire,
            margin: 0,
          }}>
            Connectez-vous à votre compte
          </p>
        </div>

        {/* ── Erreur ── */}
        {erreur && (
          <div style={{
            backgroundColor: couleurs.erreurBg,
            border: `1px solid ${couleurs.erreurBorder}`,
            color: couleurs.erreurTexte,
            padding: "12px 16px",
            borderRadius: "12px",
            fontSize: "13px",
            marginBottom: "20px",
            display: "flex",
            alignItems: "center",
            gap: "8px",
          }}>
            ⚠️ {erreur}
          </div>
        )}

        {/* ── Champ Username ── */}
        <div style={{ marginBottom: "16px" }}>
          <label style={{
            display: "block",
            fontSize: "13px",
            fontWeight: "600",
            color: couleurs.texteLabel,
            marginBottom: "8px",
            letterSpacing: "0.2px",
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
              border: `1.5px solid ${couleurs.inputBorder}`,
              backgroundColor: couleurs.inputBg,
              color: couleurs.inputTexte,
              fontSize: "14px",
              boxSizing: "border-box",
              outline: "none",
              transition: "border-color 0.2s",
            }}
            onFocus={(e) => e.target.style.borderColor = couleurs.inputFocus}
            onBlur={(e) => e.target.style.borderColor = couleurs.inputBorder}
          />
        </div>

        {/* ── Champ Mot de passe ── */}
        <div style={{ marginBottom: "28px" }}>
          <label style={{
            display: "block",
            fontSize: "13px",
            fontWeight: "600",
            color: couleurs.texteLabel,
            marginBottom: "8px",
            letterSpacing: "0.2px",
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
              border: `1.5px solid ${couleurs.inputBorder}`,
              backgroundColor: couleurs.inputBg,
              color: couleurs.inputTexte,
              fontSize: "14px",
              boxSizing: "border-box",
              outline: "none",
              transition: "border-color 0.2s",
            }}
            onFocus={(e) => e.target.style.borderColor = couleurs.inputFocus}
            onBlur={(e) => e.target.style.borderColor = couleurs.inputBorder}
          />
        </div>

        {/* ── Bouton connexion ── */}
        <button
          onClick={handleLogin}
          style={{
            width: "100%",
            padding: "14px",
            background: couleurs.boutonBg,
            color: "white",
            border: "none",
            borderRadius: "12px",
            fontSize: "15px",
            fontWeight: "600",
            cursor: "pointer",
            letterSpacing: "0.3px",
            boxShadow: "0 8px 20px rgba(14,140,140,0.35)",
            transition: "transform 0.15s, box-shadow 0.15s",
          }}
          onMouseEnter={(e) => {
            e.target.style.transform = "translateY(-1px)";
            e.target.style.boxShadow = "0 12px 28px rgba(14,140,140,0.45)";
          }}
          onMouseLeave={(e) => {
            e.target.style.transform = "translateY(0)";
            e.target.style.boxShadow = "0 8px 20px rgba(14,140,140,0.35)";
          }}
        >
          Se connecter
        </button>

        {/* ── Séparateur ── */}
        <div style={{
          display: "flex",
          alignItems: "center",
          gap: "12px",
          margin: "20px 0",
        }}>
          <div style={{ flex:1, height:"1px", backgroundColor: couleurs.cardBorder }}/>
          <span style={{ fontSize:"12px", color: couleurs.texteSecondaire }}>ou</span>
          <div style={{ flex:1, height:"1px", backgroundColor: couleurs.cardBorder }}/>
        </div>

        {/* ── Lien inscription ── */}
        <p style={{
          textAlign: "center",
          fontSize: "13px",
          color: couleurs.texteSecondaire,
          margin: 0,
        }}>
          Pas encore de compte ?{" "}
          <Link to="/register" style={{
            color: couleurs.accent,
            textDecoration: "none",
            fontWeight: "600",
          }}>
            Créer un compte
          </Link>
        </p>

      </div>
    </div>
  );
}

export default LoginPage;