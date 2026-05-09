import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { UserPlus, AlertTriangle, CheckCircle, ArrowRight } from "lucide-react";
import API from "../services/api";

function RegisterPage() {
  const [nom, setNom]           = useState("");
  const [email, setEmail]       = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm]   = useState("");
  const [erreur, setErreur]     = useState("");
  const [succes, setSucces]     = useState(false);
  const [loading, setLoading]   = useState(false);
  const navigate = useNavigate();

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
    setLoading(true);
    try {
      await API.post("/auth/register/", {
        username: nom, email, password, password_confirm: confirm
      });
      setSucces(true);
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
    } finally {
      setLoading(false);
    }
  };

  const inputBase = {
    width: "100%", padding: "11px 14px",
    borderRadius: "10px",
    border: "1.5px solid var(--border-color)",
    backgroundColor: "var(--bg-main)",
    color: "var(--text-main)",
    fontSize: "14px", boxSizing: "border-box", outline: "none",
    fontFamily: "inherit", transition: "border-color 0.2s",
  };

  return (
    <div style={{
      minHeight: "100vh",
      display: "flex", alignItems: "center", justifyContent: "center",
      backgroundColor: "var(--bg-main)",
      padding: "1rem",
      fontFamily: "'Inter', sans-serif",
    }}>
      {/* Fond décoratif */}
      <div style={{ position: "fixed", inset: 0, zIndex: 0, overflow: "hidden", pointerEvents: "none" }}>
        <div style={{
          position: "absolute", top: "-15%", left: "-5%",
          width: "500px", height: "500px", borderRadius: "50%",
          background: "radial-gradient(circle, rgba(79,70,229,0.08) 0%, transparent 70%)",
        }} />
        <div style={{
          position: "absolute", bottom: "-10%", right: "-5%",
          width: "400px", height: "400px", borderRadius: "50%",
          background: "radial-gradient(circle, rgba(37,99,235,0.06) 0%, transparent 70%)",
        }} />
      </div>

      {/* Carte */}
      <div style={{
        position: "relative", zIndex: 1,
        backgroundColor: "var(--bg-surface)",
        border: "1px solid var(--border-color)",
        borderRadius: "20px", padding: "2.5rem",
        width: "100%", maxWidth: "420px",
        boxShadow: "var(--shadow-lg)",
      }}>

        {/* En-tête */}
        <div style={{ textAlign: "center", marginBottom: "2rem" }}>
          <div style={{
            width: "56px", height: "56px", borderRadius: "14px",
            background: "linear-gradient(135deg, #2563EB, #4F46E5)",
            margin: "0 auto 1rem",
            display: "flex", alignItems: "center", justifyContent: "center",
            boxShadow: "0 8px 20px rgba(37,99,235,0.3)",
          }}>
            <UserPlus size={26} color="white" />
          </div>
          <h1 style={{
            fontSize: "22px", fontWeight: 800,
            color: "var(--text-main)", margin: "0 0 6px", letterSpacing: "-0.3px",
          }}>
            Créer un compte
          </h1>
          <p style={{ fontSize: "14px", color: "var(--text-muted)", margin: 0 }}>
            Rejoignez CV Matching Platform
          </p>
        </div>

        {/* Succès */}
        {succes && (
          <div style={{
            display: "flex", alignItems: "center", justifyContent: "center", gap: "8px",
            backgroundColor: "rgba(16,185,129,0.1)",
            border: "1px solid rgba(16,185,129,0.3)",
            color: "var(--color-success)",
            padding: "12px 16px", borderRadius: "10px",
            fontSize: "13px", marginBottom: "20px",
          }}>
            <CheckCircle size={15} /> Compte créé ! Redirection vers le login…
          </div>
        )}

        {/* Erreur */}
        {erreur && (
          <div style={{
            display: "flex", alignItems: "center", gap: "8px",
            backgroundColor: "rgba(239,68,68,0.08)",
            border: "1px solid rgba(239,68,68,0.3)",
            color: "var(--color-danger)",
            padding: "10px 14px", borderRadius: "10px",
            fontSize: "13px", marginBottom: "20px",
          }}>
            <AlertTriangle size={15} /> {erreur}
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
            <label style={{
              display: "block", fontSize: "13px", fontWeight: 600,
              color: "var(--text-muted)", marginBottom: "8px",
            }}>{label}</label>
            <input
              type={type} placeholder={ph} value={val}
              onChange={e => set(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleRegister()}
              style={inputBase}
              onFocus={e => e.target.style.borderColor = "#2563EB"}
              onBlur={e => e.target.style.borderColor = "var(--border-color)"}
            />
          </div>
        ))}

        {/* Bouton */}
        <button
          onClick={handleRegister}
          disabled={loading || succes}
          style={{
            width: "100%", padding: "13px",
            background: (loading || succes) ? "var(--text-muted)" : "linear-gradient(135deg, #2563EB, #4F46E5)",
            color: "white", border: "none", borderRadius: "10px",
            fontSize: "15px", fontWeight: 700,
            cursor: (loading || succes) ? "not-allowed" : "pointer",
            marginTop: "8px",
            boxShadow: (loading || succes) ? "none" : "0 4px 14px rgba(37,99,235,0.35)",
            transition: "all 0.2s ease",
            display: "flex", alignItems: "center", justifyContent: "center", gap: "8px",
            fontFamily: "inherit",
          }}
          onMouseEnter={e => { if (!loading && !succes) e.currentTarget.style.transform = "translateY(-1px)"; }}
          onMouseLeave={e => { e.currentTarget.style.transform = "translateY(0)"; }}
        >
          {loading ? (
            <>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" style={{ animation: "spin 1s linear infinite" }}>
                <circle cx="12" cy="12" r="10" stroke="rgba(255,255,255,0.3)" strokeWidth="3" />
                <path d="M12 2a10 10 0 0 1 10 10" stroke="white" strokeWidth="3" strokeLinecap="round" />
              </svg>
              Création en cours…
            </>
          ) : (
            <>Créer mon compte <ArrowRight size={16} /></>
          )}
        </button>

        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>

        {/* Séparateur */}
        <div style={{ display: "flex", alignItems: "center", gap: "12px", margin: "20px 0" }}>
          <div style={{ flex: 1, height: "1px", backgroundColor: "var(--border-color)" }} />
          <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>ou</span>
          <div style={{ flex: 1, height: "1px", backgroundColor: "var(--border-color)" }} />
        </div>

        <p style={{ textAlign: "center", fontSize: "13px", color: "var(--text-muted)", margin: 0 }}>
          Déjà un compte ?{" "}
          <Link to="/login" style={{ color: "#2563EB", textDecoration: "none", fontWeight: 700 }}>
            Se connecter
          </Link>
        </p>
      </div>
    </div>
  );
}

export default RegisterPage;