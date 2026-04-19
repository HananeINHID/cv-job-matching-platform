import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import API from "../services/api";

function LoginPage() {
  // Ces variables retiennent ce que l'utilisateur tape
  const [email, setEmail]       = useState("");
  const [password, setPassword] = useState("");
  const [erreur, setErreur]     = useState("");

  const navigate = useNavigate(); // pour changer de page

  const handleLogin = async () => {
  setErreur("");

  if (!email || !password) {
    setErreur("Veuillez remplir tous les champs.");
    return;
  }

  // ── MODE TEST (sans backend) ──
  // On simule une connexion réussie
  localStorage.setItem("token", "token-test-temporaire");
  navigate("/dashboard");

  // ── MODE PRODUCTION () ──
  // try {
  //   const response = await API.post("/auth/login/", { email, password });
  //   localStorage.setItem("token", response.data.access);
  //   navigate("/dashboard");
  // } catch (error) {
  //   setErreur("Email ou mot de passe incorrect.");
  // }
};

  return (
    <div style={styles.page}>
      <div style={styles.card}>

        <h1 style={styles.titre}>CV Matching</h1>
        <p style={styles.sousTitre}>Connectez-vous à votre compte</p>

        {/* Message d'erreur */}
        {erreur && <p style={styles.erreur}>{erreur}</p>}

        {/* Champ email */}
        <div style={styles.groupe}>
          <label style={styles.label}>Email</label>
          <input
            type="email"
            placeholder="exemple@email.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={styles.input}
          />
        </div>

        {/* Champ mot de passe */}
        <div style={styles.groupe}>
          <label style={styles.label}>Mot de passe</label>
          <input
            type="password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={styles.input}
          />
        </div>

        {/* Bouton connexion */}
        <button onClick={handleLogin} style={styles.bouton}>
          Se connecter
        </button>

        {/* Lien vers inscription */}
        <p style={styles.lienTexte}>
          Pas encore de compte ?{" "}
          <Link to="/register" style={styles.lien}>S'inscrire</Link>
        </p>

      </div>
    </div>
  );
}

// Styles simples en JS
const styles = {
  page: {
    minHeight: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#f5f5f5",
  },
  card: {
    backgroundColor: "white",
    padding: "2rem",
    borderRadius: "12px",
    border: "0.5px solid #ddd",
    width: "100%",
    maxWidth: "400px",
  },
  titre: {
    fontSize: "24px",
    fontWeight: "500",
    textAlign: "center",
    marginBottom: "4px",
  },
  sousTitre: {
    fontSize: "14px",
    color: "#888",
    textAlign: "center",
    marginBottom: "24px",
  },
  groupe: {
    marginBottom: "16px",
  },
  label: {
    display: "block",
    fontSize: "13px",
    marginBottom: "6px",
    color: "#444",
  },
  input: {
    width: "100%",
    padding: "10px",
    borderRadius: "8px",
    border: "1px solid #ddd",
    fontSize: "14px",
    boxSizing: "border-box",
  },
  bouton: {
    width: "100%",
    padding: "12px",
    backgroundColor: "#534AB7",
    color: "white",
    border: "none",
    borderRadius: "8px",
    fontSize: "15px",
    cursor: "pointer",
    marginTop: "8px",
  },
  erreur: {
    backgroundColor: "#FCEBEB",
    color: "#A32D2D",
    padding: "10px",
    borderRadius: "8px",
    fontSize: "13px",
    marginBottom: "16px",
  },
  lienTexte: {
    textAlign: "center",
    fontSize: "13px",
    marginTop: "16px",
    color: "#666",
  },
  lien: {
    color: "#534AB7",
    textDecoration: "none",
    fontWeight: "500",
  },
};

export default LoginPage;