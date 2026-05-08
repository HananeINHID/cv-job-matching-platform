import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Sun, Moon, UserPlus, AlertTriangle, CheckCircle } from "lucide-react";
import API from "../services/api";

function RegisterPage() {
  const [nom, setNom]           = useState("");
  const [email, setEmail]       = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm]   = useState("");
  const [erreur, setErreur]     = useState("");
  const [succes, setSucces]     = useState(false);
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem("darkMode");
    if (saved !== null) return saved === "true";
    return window.matchMedia("(prefers-color-scheme: dark)").matches;
  });
  const navigate = useNavigate();

  useEffect(() => {
    localStorage.setItem("darkMode", darkMode);
  }, [darkMode]);

  const c = {
    pageBg:      darkMode ? "#0D1B2A" : "#F0F4F8",
    cardBg:      darkMode ? "#1A2B3C" : "#FFFFFF",
    cardBorder:  darkMode ? "#1E3A5F" : "#E2EAF4",
    cardShadow:  darkMode ? "0 20px 60px rgba(0,0,0,0.5)" : "0 20px 60px rgba(14,90,130,0.1)",
    textePrimaire:   darkMode ? "#E8F1F8" : "#1A2B3C",
    texteSecondaire: darkMode ? "#7A9BB5" : "#5A7184",
    texteLabel:      darkMode ? "#A8C4D8" : "#3D5A73",
    inputBg:     darkMode ? "#0F2030" : "#F7FAFD",
    inputBorder: darkMode ? "#1E3A5F" : "#C8DCF0",
    inputTexte:  darkMode ? "#E8F1F8" : "#1A2B3C",
    toggleBg:    darkMode ? "#1E3A5F" : "#E2EAF4",
    accent:      "#FF6B47",
    boutonBg:    "linear-gradient(135deg, #0E8C8C, #0A6B7C)",
    successBg:   darkMode ? "rgba(14,140,100,0.15)" : "#F0FFF8",
    successBorder: "rgba(14,140,100,0.3)",
    successTexte: darkMode ? "#50E0A0" : "#0A6B4A",
    erreurBg:    darkMode ? "rgba(220,80,60,0.15)" : "#FFF0EE",
    erreurBorder:"rgba(220,80,60,0.3)",
    erreurTexte: darkMode ? "#FF9080" : "#C0392B",
  };

  const handleRegister = async () => {
    setErreur("");
    if (!nom || !email || !password || !confirm) {
      setErreur("Veuillez remplir tous les champs."); return;
    }
    if (password !== confirm) {
      setErreur("Les mots de passe ne correspondent pas."); return;
    }
    if (password.length < 8) {
      setErreur("Minimum 8 caractères."); return;
    }
    try {
      await API.post("/auth/register/", {
        username: nom, email, password, password_confirm: confirm
      });
      setSucces(true);
      // Redirection vers login après 2 secondes
      setTimeout(() => navigate("/login"), 2000);

    } catch (error) {
      const data = error.response?.data;
      if (data) {
        const champ = Object.keys(data)[0];
        const msg = Array.isArray(data[champ]) ? data[champ][0] : data[champ];
        setErreur(msg);
      } else {
        setErreur("Erreur réseau. Vérifiez votre connexion.");
      }
    }
  };

  const inputStyle = {
    width: "100%",
    padding: "12px 16px",
    borderRadius: "12px",
    border: `1.5px solid ${c.inputBorder}`,
    backgroundColor: c.inputBg,
    color: c.inputTexte,
    fontSize: "14px",
    boxSizing: "border-box",
    outline: "none",
  };

  const labelStyle = {
    display: "block",
    fontSize: "13px",
    fontWeight: "600",
    color: c.texteLabel,
    marginBottom: "8px",
  };

  return (
    <div style={{
      minHeight: "100vh", width: "100vw",
      position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
      display: "flex", alignItems: "center", justifyContent: "center",
      backgroundColor: c.pageBg, overflowY: "auto", padding: "1rem",
    }}>

      <button onClick={() => setDarkMode(!darkMode)} style={{
        position: "fixed", top: "20px", right: "20px",
        width: "42px", height: "42px", borderRadius: "50%",
        border: `1px solid ${c.cardBorder}`, backgroundColor: c.toggleBg,
        cursor: "pointer", zIndex: 100,
        display: "flex", alignItems: "center", justifyContent: "center"
      }}>
        {darkMode ? <Sun size={20} color="#FFB300" /> : <Moon size={20} color="#5A7184" />}
      </button>

      <div style={{
        backgroundColor: c.cardBg, border: `1px solid ${c.cardBorder}`,
        borderRadius: "20px", padding: "2.5rem", width: "100%", maxWidth: "420px",
        boxShadow: c.cardShadow, margin: "1rem",
      }}>

        {/* En-tête */}
        <div style={{ textAlign: "center", marginBottom: "2rem" }}>
          <div style={{
            width: "56px", height: "56px", borderRadius: "14px",
            background: c.boutonBg, margin: "0 auto 1rem",
            display: "flex", alignItems: "center", justifyContent: "center",
            boxShadow: "0 8px 20px rgba(14,140,140,0.3)",
          }}>
            <UserPlus size={28} color="white" />
          </div>
          <h1 style={{ fontSize: "24px", fontWeight: "700", color: c.textePrimaire, margin: "0 0 6px 0" }}>
            Créer un compte
          </h1>
          <p style={{ fontSize: "14px", color: c.texteSecondaire, margin: 0 }}>
            Rejoignez CV Matching
          </p>
        </div>

        {/* Succès */}
        {succes && (
          <div style={{
            backgroundColor: c.successBg, border: `1px solid ${c.successBorder}`,
            color: c.successTexte, padding: "12px 16px", borderRadius: "12px",
            fontSize: "13px", marginBottom: "20px", textAlign: "center",
            display: "flex", alignItems: "center", justifyContent: "center", gap: "8px"
          }}>
            <CheckCircle size={16} /> Compte créé ! Redirection vers le login...
          </div>
        )}

        {/* Erreur */}
        {erreur && (
          <div style={{
            backgroundColor: c.erreurBg, border: `1px solid ${c.erreurBorder}`,
            color: c.erreurTexte, padding: "12px 16px", borderRadius: "12px",
            fontSize: "13px", marginBottom: "20px",
            display: "flex", alignItems: "center", gap: "8px"
          }}>
            <AlertTriangle size={16} /> {erreur}
          </div>
        )}

        {/* Champs */}
        {[
          { label: "Nom d'utilisateur", val: nom, set: setNom, type: "text", ph: "rachid_alami" },
          { label: "Email", val: email, set: setEmail, type: "email", ph: "rachid@email.com" },
          { label: "Mot de passe", val: password, set: setPassword, type: "password", ph: "••••••••" },
          { label: "Confirmer le mot de passe", val: confirm, set: setConfirm, type: "password", ph: "••••••••" },
        ].map(({ label, val, set, type, ph }) => (
          <div key={label} style={{ marginBottom: "16px" }}>
            <label style={labelStyle}>{label}</label>
            <input
              type={type} placeholder={ph} value={val}
              onChange={(e) => set(e.target.value)}
              style={inputStyle}
              onFocus={(e) => e.target.style.borderColor = "#0E8C8C"}
              onBlur={(e) => e.target.style.borderColor = c.inputBorder}
            />
          </div>
        ))}

        {/* Bouton */}
        <button onClick={handleRegister} style={{
          width: "100%", padding: "14px",
          background: c.boutonBg, color: "white", border: "none",
          borderRadius: "12px", fontSize: "15px", fontWeight: "600",
          cursor: "pointer", marginTop: "8px",
          boxShadow: "0 8px 20px rgba(14,140,140,0.35)",
        }}>
          Créer mon compte
        </button>

        {/* Séparateur */}
        <div style={{ display: "flex", alignItems: "center", gap: "12px", margin: "20px 0" }}>
          <div style={{ flex: 1, height: "1px", backgroundColor: c.cardBorder }}/>
          <span style={{ fontSize: "12px", color: c.texteSecondaire }}>ou</span>
          <div style={{ flex: 1, height: "1px", backgroundColor: c.cardBorder }}/>
        </div>

        <p style={{ textAlign: "center", fontSize: "13px", color: c.texteSecondaire, margin: 0 }}>
          Déjà un compte ?{" "}
          <Link to="/login" style={{ color: c.accent, textDecoration: "none", fontWeight: "600" }}>
            Se connecter
          </Link>
        </p>
      </div>
    </div>
  );
}

export default RegisterPage;