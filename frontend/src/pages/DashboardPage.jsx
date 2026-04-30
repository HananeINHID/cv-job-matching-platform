import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import API from "../services/api";

function DashboardPage() {
  const navigate = useNavigate();
  const [profil, setProfil]       = useState(null);
  const [loading, setLoading]     = useState(true);
  const [recherche, setRecherche] = useState("");

  // Charger le profil de l'utilisateur depuis le backend
  useEffect(() => {
    const token = localStorage.getItem("token")
    if (!token) {
      setProfil(null); 
      setLoading(false);
      return; 
    }

    const chargerProfil = async () => {
      try {
        const response = await API.get("/profile/");
        const data = response.data;
        // Le serializer retourne hard_skills_list / soft_skills_list comme listes.
        // On normalise pour que le reste du composant lise toujours data.hard_skills etc.
        setProfil({
          ...data,
          hard_skills: Array.isArray(data.hard_skills_list) ? data.hard_skills_list
                       : Array.isArray(data.hard_skills) ? data.hard_skills : [],
          soft_skills: Array.isArray(data.soft_skills_list) ? data.soft_skills_list
                       : Array.isArray(data.soft_skills) ? data.soft_skills : [],
        });
      } catch (error) {
        // MODE TEST : on ne redirige pas vers login
        console.log("Backend pas prêt, utilisation des données mock");
      } finally {
        setLoading(false);
      }
    };
    chargerProfil();
  }, []);

  const handleRecherche = () => {
    // On envoie vers ResultsPage avec le mot-clé
    navigate("/results", { state: { recherche } });
  };

  const handleDeconnexion = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  if (loading) {
    return (
      <div style={styles.centrer}>
        <p style={{ color: "#888" }}>Chargement...</p>
      </div>
    );
  }

  // Données mock si backend pas encore prêt
  const data = profil || {
    personal_info: { nom: "Rachid Alami", titre: "Développeur Frontend", ville: "Casablanca" },
    hard_skills: ["React", "JavaScript", "CSS"],
    soft_skills: ["Communication", "Travail en équipe"],
    experiences: [{ poste: "Stagiaire Dev", entreprise: "TechMaroc" }],
    formations: [{ diplome: "Licence IASD", etablissement: "FSS Marrakech" }],
  };

  return (
    <div style={styles.page}>

      {/* ── NAVBAR ── */}
      <nav style={styles.navbar}>
        <span style={styles.navLogo}>CV Matching</span>
        <div style={styles.navDroit}>
          <span style={styles.navNom}>{data.personal_info.nom}</span>
          <button onClick={handleDeconnexion} style={styles.boutonDeco}>
            Déconnexion
          </button>
        </div>
      </nav>

      <div style={styles.contenu}>

        {/* ── BIENVENUE ── */}
        <div style={styles.bienvenue}>
          <h1 style={styles.titre}>
            Bonjour, {data.personal_info.nom.split(" ")[0]} 👋
          </h1>
          <p style={styles.sousTitre}>{data.personal_info.titre} · {data.personal_info.ville}</p>
        </div>

        {/* ── BARRE DE RECHERCHE ── */}
        <div style={styles.searchBox}>
          <h2 style={styles.searchTitre}>Trouver des offres</h2>
          <div style={styles.searchRow}>
            <input
              style={styles.searchInput}
              value={recherche}
              onChange={(e) => setRecherche(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleRecherche()}
              placeholder="Ex: Développeur React, Data Scientist..."
            />
            <button onClick={handleRecherche} style={styles.boutonRecherche}>
              Lancer la recherche
            </button>
          </div>
        </div>

        {/* ── STATS RAPIDES ── */}
        <div style={styles.statsGrille}>
          <div style={styles.statCard}>
            <p style={styles.statLabel}>Hard Skills</p>
            <p style={styles.statNombre}>{data.hard_skills.length}</p>
          </div>
          <div style={styles.statCard}>
            <p style={styles.statLabel}>Soft Skills</p>
            <p style={styles.statNombre}>{data.soft_skills.length}</p>
          </div>
          <div style={styles.statCard}>
            <p style={styles.statLabel}>Expériences</p>
            <p style={styles.statNombre}>{data.experiences.length}</p>
          </div>
          <div style={styles.statCard}>
            <p style={styles.statLabel}>Formations</p>
            <p style={styles.statNombre}>{data.formations.length}</p>
          </div>
        </div>

        {/* ── MON PROFIL ── */}
        <div style={styles.grille2}>

          {/* Compétences */}
          <div style={styles.carte}>
            <h3 style={styles.carteTitre}>Mes compétences techniques</h3>
            <div style={styles.tags}>
              {data.hard_skills.map((s) => (
                <span key={s} style={styles.tagViolet}>{s}</span>
              ))}
            </div>
            <h3 style={{ ...styles.carteTitre, marginTop: "16px" }}>
              Soft Skills
            </h3>
            <div style={styles.tags}>
              {data.soft_skills.map((s) => (
                <span key={s} style={styles.tagVert}>{s}</span>
              ))}
            </div>
          </div>

          {/* Expériences */}
          <div style={styles.carte}>
            <h3 style={styles.carteTitre}>Mes expériences</h3>
            {data.experiences.map((exp, i) => (
              <div key={i} style={styles.ligneInfo}>
                <p style={styles.lignePoste}>{exp.poste}</p>
                <p style={styles.ligneEntreprise}>{exp.entreprise}</p>
              </div>
            ))}

            <h3 style={{ ...styles.carteTitre, marginTop: "16px" }}>
              Mes formations
            </h3>
            {data.formations.map((form, i) => (
              <div key={i} style={styles.ligneInfo}>
                <p style={styles.lignePoste}>{form.diplome}</p>
                <p style={styles.ligneEntreprise}>{form.etablissement}</p>
              </div>
            ))}
          </div>
        </div>

        {/* ── MODIFIER PROFIL ── */}
        <button
          onClick={() => navigate("/cv-form")}
          style={styles.boutonModifier}
        >
          Modifier mon profil
        </button>

      </div>
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    backgroundColor: "#f5f5f5",
  },
  centrer: {
    minHeight: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  navbar: {
    backgroundColor: "white",
    borderBottom: "0.5px solid #ddd",
    padding: "0 2rem",
    height: "60px",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
  },
  navLogo: {
    fontSize: "18px",
    fontWeight: "500",
    color: "#534AB7",
  },
  navDroit: {
    display: "flex",
    alignItems: "center",
    gap: "16px",
  },
  navNom: {
    fontSize: "14px",
    color: "#444",
  },
  boutonDeco: {
    padding: "6px 14px",
    backgroundColor: "white",
    color: "#A32D2D",
    border: "1px solid #A32D2D",
    borderRadius: "8px",
    fontSize: "13px",
    cursor: "pointer",
  },
  contenu: {
    maxWidth: "900px",
    margin: "0 auto",
    padding: "2rem 1rem",
  },
  bienvenue: {
    marginBottom: "24px",
  },
  titre: {
    fontSize: "26px",
    fontWeight: "500",
    marginBottom: "4px",
  },
  sousTitre: {
    fontSize: "14px",
    color: "#888",
  },
  searchBox: {
    backgroundColor: "white",
    borderRadius: "12px",
    border: "0.5px solid #ddd",
    padding: "1.5rem",
    marginBottom: "20px",
  },
  searchTitre: {
    fontSize: "16px",
    fontWeight: "500",
    marginBottom: "12px",
    color: "#534AB7",
  },
  searchRow: {
    display: "flex",
    gap: "10px",
  },
  searchInput: {
    flex: 1,
    padding: "12px",
    borderRadius: "8px",
    border: "1px solid #ddd",
    fontSize: "14px",
  },
  boutonRecherche: {
    padding: "12px 20px",
    backgroundColor: "#534AB7",
    color: "white",
    border: "none",
    borderRadius: "8px",
    fontSize: "14px",
    cursor: "pointer",
    whiteSpace: "nowrap",
  },
  statsGrille: {
    display: "grid",
    gridTemplateColumns: "repeat(4, 1fr)",
    gap: "12px",
    marginBottom: "20px",
  },
  statCard: {
    backgroundColor: "white",
    borderRadius: "10px",
    border: "0.5px solid #ddd",
    padding: "1rem",
    textAlign: "center",
  },
  statLabel: {
    fontSize: "12px",
    color: "#888",
    marginBottom: "6px",
  },
  statNombre: {
    fontSize: "28px",
    fontWeight: "500",
    color: "#534AB7",
    margin: 0,
  },
  grille2: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "16px",
    marginBottom: "20px",
  },
  carte: {
    backgroundColor: "white",
    borderRadius: "12px",
    border: "0.5px solid #ddd",
    padding: "1.5rem",
  },
  carteTitre: {
    fontSize: "14px",
    fontWeight: "500",
    color: "#444",
    marginBottom: "12px",
  },
  tags: {
    display: "flex",
    flexWrap: "wrap",
    gap: "8px",
  },
  tagViolet: {
    backgroundColor: "#EEEDFE",
    color: "#534AB7",
    padding: "4px 12px",
    borderRadius: "20px",
    fontSize: "12px",
  },
  tagVert: {
    backgroundColor: "#E1F5EE",
    color: "#0F6E56",
    padding: "4px 12px",
    borderRadius: "20px",
    fontSize: "12px",
  },
  ligneInfo: {
    borderLeft: "3px solid #EEEDFE",
    paddingLeft: "10px",
    marginBottom: "10px",
  },
  lignePoste: {
    fontSize: "13px",
    fontWeight: "500",
    color: "#333",
    margin: 0,
  },
  ligneEntreprise: {
    fontSize: "12px",
    color: "#888",
    margin: 0,
  },
  boutonModifier: {
    padding: "12px 24px",
    backgroundColor: "white",
    color: "#534AB7",
    border: "1px solid #534AB7",
    borderRadius: "8px",
    fontSize: "14px",
    cursor: "pointer",
  },
};

export default DashboardPage;