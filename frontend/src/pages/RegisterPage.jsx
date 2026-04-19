import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import API from "../services/api";

function RegisterPage() {
  const [nom, setNom]           = useState("");
  const [email, setEmail]       = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm]   = useState("");
  const [erreur, setErreur]     = useState("");
  const [succes, setSucces]     = useState(false);

  const navigate = useNavigate();

  const handleRegister = async () => {
    setErreur("");

    // Vérification simple avant d'envoyer
    if (!nom || !email || !password || !confirm) {
      setErreur("Veuillez remplir tous les champs.");
      return;
    }
    if (password !== confirm) {
      setErreur("Les mots de passe ne correspondent pas.");
      return;
    }
    if (password.length < 6) {
      setErreur("Le mot de passe doit contenir au moins 6 caractères.");
      return;
    }

    try {
      await API.post("/auth/register/", {
        name: nom,
        email,
        password,
      });

      setSucces(true);
      // Après 2 secondes → aller vers login
      setTimeout(() => navigate("/login"), 2000);

    } catch (error) {
      setErreur("Erreur lors de l'inscription. Cet email est peut-être déjà utilisé.");
    }
  };

  return (
    <div style={styles.page}>
      <div style={styles.card}>

        <h1 style={styles.titre}>Créer un compte</h1>
        <p style={styles.sousTitre}>Rejoignez CV Matching</p>

        {/* Message succès */}
        {succes && (
          <p style={styles.succes}>
            Compte créé avec succès ! Redirection...
          </p>
        )}

        {/* Message erreur */}
        {erreur && <p style={styles.erreur}>{erreur}</p>}

        {/* Nom complet */}
        <div style={styles.groupe}>
          <label style={styles.label}>Nom complet</label>
          <input
            type="text"
            placeholder="Rachid Alami"
            value={nom}
            onChange={(e) => setNom(e.target.value)}
            style={styles.input}
          />
        </div>

        {/* Email */}
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

        {/* Mot de passe */}
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

        {/* Confirmation */}
        <div style={styles.groupe}>
          <label style={styles.label}>Confirmer le mot de passe</label>
          <input
            type="password"
            placeholder="••••••••"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            style={styles.input}
          />
        </div>

        <button onClick={handleRegister} style={styles.bouton}>
          S'inscrire
        </button>

        <p style={styles.lienTexte}>
          Déjà un compte ?{" "}
          <Link to="/login" style={styles.lien}>Se connecter</Link>
        </p>

      </div>
    </div>
  );
}

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
  succes: {
    backgroundColor: "#EAF3DE",
    color: "#3B6D11",
    padding: "10px",
    borderRadius: "8px",
    fontSize: "13px",
    marginBottom: "16px",
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

export default RegisterPage;