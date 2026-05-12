import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Briefcase, AlertTriangle, Eye, EyeOff, ArrowRight } from "lucide-react";
import API from "../services/api";

function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword]  = useState("");
  const [showPwd, setShowPwd]    = useState(false);
  const [erreur, setErreur]      = useState("");
  const [loading, setLoading]    = useState(false);
  const navigate = useNavigate();

  const handleLogin = async () => {
    setErreur("");
    if (!username || !password) {
      setErreur("Veuillez remplir tous les champs.");
      return;
    }
    setLoading(true);
    try {
      const response = await API.post("/token/", { username, password });
      localStorage.setItem("token", response.data.access);
      localStorage.setItem("refresh_token", response.data.refresh);
      navigate("/dashboard");
    } catch (err) {
      console.error("Erreur de connexion:", err);
      if (!err.response) {
        setErreur("Impossible de contacter le serveur. Vérifiez que le backend est lancé.");
      } else {
        setErreur("Nom d'utilisateur ou mot de passe incorrect.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: "100vh",
      width: "100%",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      backgroundColor: "var(--bg-main)",
      padding: "1rem",
      fontFamily: "'Inter', sans-serif",
    }}>
      {/* Fond décoratif */}
      <div style={{
        position: "fixed", inset: 0, zIndex: 0, overflow: "hidden", pointerEvents: "none",
      }}>
        <div style={{
          position: "absolute", top: "-20%", right: "-10%",
          width: "600px", height: "600px", borderRadius: "50%",
          background: "radial-gradient(circle, rgba(37,99,235,0.08) 0%, transparent 70%)",
        }} />
        <div style={{
          position: "absolute", bottom: "-10%", left: "-5%",
          width: "400px", height: "400px", borderRadius: "50%",
          background: "radial-gradient(circle, rgba(79,70,229,0.06) 0%, transparent 70%)",
        }} />
      </div>

      {/* Carte */}
      <div style={{
        position: "relative", zIndex: 1,
        backgroundColor: "var(--bg-surface)",
        border: "1px solid var(--border-color)",
        borderRadius: "20px",
        padding: "2.5rem",
        width: "100%",
        maxWidth: "420px",
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
            <Briefcase size={26} color="white" />
          </div>
          <h1 style={{
            fontSize: "22px", fontWeight: 800,
            color: "var(--text-main)",
            margin: "0 0 6px",
            letterSpacing: "-0.3px",
          }}>
            CV Matching
          </h1>
          <p style={{ fontSize: "14px", color: "var(--text-muted)", margin: 0 }}>
            Connectez-vous à votre espace
          </p>
        </div>

        {/* Erreur */}
        {erreur && (
          <div style={{
            display: "flex", alignItems: "center", gap: "8px",
            backgroundColor: "rgba(239,68,68,0.08)",
            border: "1px solid rgba(239,68,68,0.3)",
            color: "var(--color-danger)",
            padding: "10px 14px",
            borderRadius: "10px",
            fontSize: "13px",
            marginBottom: "20px",
          }}>
            <AlertTriangle size={15} />
            {erreur}
          </div>
        )}

        {/* Champ Username */}
        <div style={{ marginBottom: "16px" }}>
          <label style={{
            display: "block", fontSize: "13px", fontWeight: 600,
            color: "var(--text-muted)", marginBottom: "8px",
          }}>
            Nom d'utilisateur
          </label>
          <input
            type="text"
            placeholder="votre_username"
            value={username}
            onChange={e => setUsername(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleLogin()}
            style={{
              width: "100%", padding: "11px 14px",
              borderRadius: "10px",
              border: "1.5px solid var(--border-color)",
              backgroundColor: "var(--bg-main)",
              color: "var(--text-main)",
              fontSize: "14px", outline: "none",
              fontFamily: "inherit", transition: "border-color 0.2s",
              boxSizing: "border-box",
            }}
            onFocus={e => e.target.style.borderColor = "#2563EB"}
            onBlur={e => e.target.style.borderColor = "var(--border-color)"}
          />
        </div>

        {/* Champ Mot de passe */}
        <div style={{ marginBottom: "28px" }}>
          <label style={{
            display: "block", fontSize: "13px", fontWeight: 600,
            color: "var(--text-muted)", marginBottom: "8px",
          }}>
            Mot de passe
          </label>
          <div style={{ position: "relative" }}>
            <input
              type={showPwd ? "text" : "password"}
              placeholder="••••••••"
              value={password}
              onChange={e => setPassword(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleLogin()}
              style={{
                width: "100%", padding: "11px 40px 11px 14px",
                borderRadius: "10px",
                border: "1.5px solid var(--border-color)",
                backgroundColor: "var(--bg-main)",
                color: "var(--text-main)",
                fontSize: "14px", outline: "none",
                fontFamily: "inherit", transition: "border-color 0.2s",
                boxSizing: "border-box",
              }}
              onFocus={e => e.target.style.borderColor = "#2563EB"}
              onBlur={e => e.target.style.borderColor = "var(--border-color)"}
            />
            <button
              type="button"
              onClick={() => setShowPwd(!showPwd)}
              style={{
                position: "absolute", right: "12px", top: "50%", transform: "translateY(-50%)",
                background: "none", border: "none", cursor: "pointer",
                color: "var(--text-muted)", padding: "2px",
              }}
            >
              {showPwd ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
        </div>

        {/* Bouton connexion */}
        <button
          onClick={handleLogin}
          disabled={loading}
          style={{
            width: "100%", padding: "13px",
            background: loading ? "var(--text-muted)" : "linear-gradient(135deg, #2563EB, #4F46E5)",
            color: "white", border: "none", borderRadius: "10px",
            fontSize: "15px", fontWeight: 700,
            cursor: loading ? "not-allowed" : "pointer",
            letterSpacing: "0.2px",
            boxShadow: loading ? "none" : "0 4px 14px rgba(37,99,235,0.35)",
            transition: "all 0.2s ease",
            display: "flex", alignItems: "center", justifyContent: "center", gap: "8px",
            fontFamily: "inherit",
          }}
          onMouseEnter={e => { if (!loading) e.currentTarget.style.transform = "translateY(-1px)"; }}
          onMouseLeave={e => { e.currentTarget.style.transform = "translateY(0)"; }}
        >
          {loading ? (
            <>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" style={{ animation: "spin 1s linear infinite" }}>
                <circle cx="12" cy="12" r="10" stroke="rgba(255,255,255,0.3)" strokeWidth="3" />
                <path d="M12 2a10 10 0 0 1 10 10" stroke="white" strokeWidth="3" strokeLinecap="round" />
              </svg>
              Connexion en cours…
            </>
          ) : (
            <>Se connecter <ArrowRight size={16} /></>
          )}
        </button>

        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>

        {/* Séparateur */}
        <div style={{ display: "flex", alignItems: "center", gap: "12px", margin: "20px 0" }}>
          <div style={{ flex: 1, height: "1px", backgroundColor: "var(--border-color)" }} />
          <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>ou</span>
          <div style={{ flex: 1, height: "1px", backgroundColor: "var(--border-color)" }} />
        </div>

        {/* Lien inscription */}
        <p style={{ textAlign: "center", fontSize: "13px", color: "var(--text-muted)", margin: 0 }}>
          Pas encore de compte ?{" "}
          <Link to="/register" style={{ color: "#2563EB", textDecoration: "none", fontWeight: 700 }}>
            Créer un compte
          </Link>
        </p>
      </div>
    </div>
  );
}

export default LoginPage;