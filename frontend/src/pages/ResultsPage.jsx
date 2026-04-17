import { useState, useEffect, useRef } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import {
  Chart as ChartJS,
  RadialLinearScale, PointElement, LineElement, Filler,
  CategoryScale, LinearScale, BarElement,
  ScatterController,
  Tooltip, Legend
} from "chart.js";
import { Radar, Bar, Scatter } from "react-chartjs-2";
import API from "../services/api";

ChartJS.register(
  RadialLinearScale, PointElement, LineElement, Filler,
  CategoryScale, LinearScale, BarElement,
  ScatterController,
  Tooltip, Legend
);

// ── DONNÉES MOCK ──
const MOCK_OFFRES = [
  { id:1, titre:"Développeur React Frontend", entreprise:"Capgemini Maroc",  ville:"Casablanca", contrat:"CDI",   score:87, competences:["React","JavaScript","CSS","Git"] },
  { id:2, titre:"Frontend Engineer",          entreprise:"OCP Digital",      ville:"Rabat",       contrat:"CDI",   score:74, competences:["React","TypeScript","REST API"] },
  { id:3, titre:"Développeur Full Stack",     entreprise:"StartupTech",      ville:"Casablanca", contrat:"CDD",   score:65, competences:["React","Node.js","MongoDB"] },
  { id:4, titre:"UI Developer",               entreprise:"Sofrecom",         ville:"Casablanca", contrat:"Stage", score:58, competences:["HTML","CSS","JavaScript"] },
  { id:5, titre:"Web Developer",              entreprise:"Maroc Telecom",    ville:"Rabat",       contrat:"CDI",   score:45, competences:["Vue.js","PHP","MySQL"] },
];

const couleurScore = (score) => {
  if (score >= 75) return { bg:"#EAF3DE", texte:"#3B6D11" };
  if (score >= 50) return { bg:"#FAEEDA", texte:"#854F0B" };
  return { bg:"#FCEBEB", texte:"#A32D2D" };
};

const couleurCluster = (nom) => {
  if (nom === "Frontend")  return "#534AB7";
  if (nom === "Data")      return "#0F6E56";
  if (nom === "Fullstack") return "#D85A30";
  return "#888";
};

function ResultsPage() {
  const navigate  = useNavigate();
  const location  = useLocation();
  const recherche = location.state?.recherche || "";

  const [offres, setOffres]           = useState([]);
  const [offreSelectionnee, setOffre] = useState(null);
  const [loading, setLoading]         = useState(true);
  const [onglet, setOnglet]           = useState("offres");

  useEffect(() => {
    const charger = async () => {
      try {
        const response = await API.get(`/matching/results/?q=${recherche}`);
        setOffres(response.data);
        setOffre(response.data[0]);
      } catch {
        setOffres(MOCK_OFFRES);
        setOffre(MOCK_OFFRES[0]);
      } finally {
        setLoading(false);
      }
    };
    charger();
  }, []);

  // ── Données Radar ──
  const radarData = {
    labels: ["React", "JavaScript", "CSS", "Python", "SQL", "Git"],
    datasets: [
      {
        label: "Votre profil",
        data: [90, 80, 75, 60, 50, 70],
        backgroundColor: "rgba(83, 74, 183, 0.2)",
        borderColor: "#534AB7",
        borderWidth: 2,
        pointBackgroundColor: "#534AB7",
      },
      {
        label: "Offre sélectionnée",
        data: [95, 90, 70, 30, 40, 80],
        backgroundColor: "rgba(15, 110, 86, 0.15)",
        borderColor: "#0F6E56",
        borderWidth: 2,
        pointBackgroundColor: "#0F6E56",
      },
    ],
  };

  // ── Données BarChart scores ──
  const barScoresData = {
    labels: offres.map((o) => o.entreprise),
    datasets: [{
      label: "Score de matching (%)",
      data: offres.map((o) => o.score),
      backgroundColor: offres.map((o) =>
        o.score >= 75 ? "#639922" :
        o.score >= 50 ? "#BA7517" : "#E24B4A"
      ),
      borderRadius: 6,
    }],
  };

  // ── Données BarChart horizontal (compétences) ──
  const competencesData = {
    labels: ["React", "JavaScript", "Python", "Django", "SQL", "Node.js", "CSS", "Git"],
    datasets: [{
      label: "Fréquence dans les offres",
      data: [95, 88, 75, 70, 65, 60, 58, 55],
      backgroundColor: "#534AB7",
      borderRadius: 6,
    }],
  };

  // ── Données Scatter clusters ──
  const clusterData = {
    datasets: [
      {
        label: "Frontend",
        data: [{ x:20,y:80 },{ x:25,y:75 },{ x:30,y:85 }],
        backgroundColor: "#534AB7",
        pointRadius: 10,
      },
      {
        label: "Data",
        data: [{ x:70,y:40 },{ x:75,y:35 },{ x:65,y:45 }],
        backgroundColor: "#0F6E56",
        pointRadius: 10,
      },
      {
        label: "Fullstack",
        data: [{ x:50,y:60 },{ x:55,y:55 },{ x:48,y:65 }],
        backgroundColor: "#D85A30",
        pointRadius: 10,
      },
    ],
  };

  if (loading) {
    return (
      <div style={styles.centrer}>
        <p style={{ color:"#888" }}>Analyse en cours...</p>
      </div>
    );
  }

  return (
    <div style={styles.page}>

      {/* ── NAVBAR ── */}
      <nav style={styles.navbar}>
        <span style={styles.navLogo}>CV Matching</span>
        <button onClick={() => navigate("/dashboard")} style={styles.retour}>
          ← Retour au dashboard
        </button>
      </nav>

      <div style={styles.contenu}>
        <h1 style={styles.titre}>Résultats de matching</h1>
        {recherche && <p style={styles.sousTitre}>Recherche : « {recherche} »</p>}

        {/* ── ONGLETS ── */}
        <div style={styles.onglets}>
          {["offres","graphiques","clusters"].map((o) => (
            <button key={o} onClick={() => setOnglet(o)}
              style={onglet === o ? styles.ongletActif : styles.onglet}>
              {o === "offres"     && "📋 Offres"}
              {o === "graphiques" && "📊 Graphiques"}
              {o === "clusters"   && "🔵 Clusters"}
            </button>
          ))}
        </div>

        {/* ══ ONGLET 1 : OFFRES ══ */}
        {onglet === "offres" && (
          <div style={styles.grille2}>

            <div>
              {offres.map((offre) => {
                const c = couleurScore(offre.score);
                const actif = offreSelectionnee?.id === offre.id;
                return (
                  <div key={offre.id} onClick={() => setOffre(offre)}
                    style={{ ...styles.offreCard,
                      border: actif ? "2px solid #534AB7" : "0.5px solid #ddd" }}>
                    <div style={styles.offreHeader}>
                      <div>
                        <p style={styles.offreTitre}>{offre.titre}</p>
                        <p style={styles.offreEntreprise}>{offre.entreprise} · {offre.ville}</p>
                      </div>
                      <div style={{ ...styles.scoreBadge, backgroundColor:c.bg, color:c.texte }}>
                        {offre.score}%
                      </div>
                    </div>
                    <span style={styles.contratBadge}>{offre.contrat}</span>
                  </div>
                );
              })}
            </div>

            {offreSelectionnee && (
              <div style={styles.detail}>
                <h2 style={styles.detailTitre}>{offreSelectionnee.titre}</h2>
                <p style={styles.detailEntreprise}>
                  {offreSelectionnee.entreprise} · {offreSelectionnee.ville}
                </p>
                <div style={styles.scoreGrand}>
                  <p style={styles.scoreLabel}>Score de compatibilité</p>
                  <p style={{ ...styles.scoreNombre, color: couleurScore(offreSelectionnee.score).texte }}>
                    {offreSelectionnee.score}%
                  </p>
                  <div style={styles.barreContainer}>
                    <div style={{
                      ...styles.barreFill,
                      width: `${offreSelectionnee.score}%`,
                      backgroundColor:
                        offreSelectionnee.score >= 75 ? "#639922" :
                        offreSelectionnee.score >= 50 ? "#BA7517" : "#E24B4A",
                    }}/>
                  </div>
                </div>
                <p style={styles.detailLabel}>Compétences requises</p>
                <div style={styles.tags}>
                  {offreSelectionnee.competences.map((c) => (
                    <span key={c} style={styles.tagViolet}>{c}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* ══ ONGLET 2 : GRAPHIQUES ══ */}
        {onglet === "graphiques" && (
          <div>

            {/* Radar */}
            <div style={styles.carte}>
              <h2 style={styles.carteTitre}>Vos compétences vs l'offre sélectionnée</h2>
              <p style={styles.carteDesc}>
                Violet = votre profil · Vert = compétences requises par l'offre
              </p>
              <div style={{ maxWidth:"450px", margin:"0 auto" }}>
                <Radar data={radarData} options={{
                  responsive: true,
                  scales: { r: { beginAtZero:true, max:100 } },
                  plugins: { legend: { position:"bottom" } },
                }}/>
              </div>
            </div>

            {/* Distribution scores */}
            <div style={styles.carte}>
              <h2 style={styles.carteTitre}>Score de matching par offre</h2>
              <p style={styles.carteDesc}>
                Vert ≥ 75% · Orange entre 50-75% · Rouge &lt; 50%
              </p>
              <Bar data={barScoresData} options={{
                responsive: true,
                scales: { y: { beginAtZero:true, max:100 } },
                plugins: { legend: { display:false } },
              }}/>
            </div>

            {/* Compétences demandées */}
            <div style={styles.carte}>
              <h2 style={styles.carteTitre}>Compétences les plus demandées</h2>
              <p style={styles.carteDesc}>
                Fréquence d'apparition dans toutes les offres scrapées
              </p>
              <Bar data={competencesData} options={{
                indexAxis: "y",
                responsive: true,
                plugins: { legend: { display:false } },
                scales: { x: { beginAtZero:true, max:100 } },
              }}/>
            </div>
          </div>
        )}

        {/* ══ ONGLET 3 : CLUSTERS ══ */}
        {onglet === "clusters" && (
          <div style={styles.carte}>
            <h2 style={styles.carteTitre}>Clusters K-Means — regroupement des offres</h2>
            <p style={styles.carteDesc}>
              Chaque point = une offre. Les couleurs = le cluster détecté par l'algorithme de Youssef.
            </p>
            <Scatter data={clusterData} options={{
              responsive: true,
              plugins: { legend: { position:"bottom" } },
              scales: {
                x: { title:{ display:true, text:"Axe 1" } },
                y: { title:{ display:true, text:"Axe 2" } },
              },
            }}/>
          </div>
        )}

      </div>
    </div>
  );
}

const styles = {
  page:            { minHeight:"100vh", backgroundColor:"#f5f5f5" },
  centrer:         { minHeight:"100vh", display:"flex", alignItems:"center", justifyContent:"center" },
  navbar:          { backgroundColor:"white", borderBottom:"0.5px solid #ddd", padding:"0 2rem", height:"60px", display:"flex", alignItems:"center", justifyContent:"space-between" },
  navLogo:         { fontSize:"18px", fontWeight:"500", color:"#534AB7" },
  retour:          { padding:"6px 14px", backgroundColor:"white", color:"#534AB7", border:"1px solid #534AB7", borderRadius:"8px", fontSize:"13px", cursor:"pointer" },
  contenu:         { maxWidth:"1000px", margin:"0 auto", padding:"2rem 1rem" },
  titre:           { fontSize:"26px", fontWeight:"500", marginBottom:"4px" },
  sousTitre:       { fontSize:"14px", color:"#888", marginBottom:"20px" },
  onglets:         { display:"flex", gap:"8px", marginBottom:"24px" },
  onglet:          { padding:"8px 20px", backgroundColor:"white", border:"0.5px solid #ddd", borderRadius:"8px", fontSize:"14px", cursor:"pointer", color:"#666" },
  ongletActif:     { padding:"8px 20px", backgroundColor:"#534AB7", border:"none", borderRadius:"8px", fontSize:"14px", cursor:"pointer", color:"white", fontWeight:"500" },
  grille2:         { display:"grid", gridTemplateColumns:"1fr 1fr", gap:"16px" },
  offreCard:       { backgroundColor:"white", borderRadius:"10px", padding:"1rem", marginBottom:"10px", cursor:"pointer" },
  offreHeader:     { display:"flex", justifyContent:"space-between", alignItems:"flex-start" },
  offreTitre:      { fontSize:"14px", fontWeight:"500", margin:0, color:"#222" },
  offreEntreprise: { fontSize:"12px", color:"#888", margin:"4px 0 0 0" },
  scoreBadge:      { padding:"4px 10px", borderRadius:"20px", fontSize:"13px", fontWeight:"500", whiteSpace:"nowrap" },
  contratBadge:    { backgroundColor:"#F1EFE8", color:"#5F5E5A", padding:"3px 10px", borderRadius:"20px", fontSize:"11px", marginTop:"8px", display:"inline-block" },
  detail:          { backgroundColor:"white", borderRadius:"12px", border:"0.5px solid #ddd", padding:"1.5rem", alignSelf:"flex-start" },
  detailTitre:     { fontSize:"18px", fontWeight:"500", marginBottom:"4px" },
  detailEntreprise:{ fontSize:"13px", color:"#888", marginBottom:"20px" },
  scoreGrand:      { marginBottom:"20px" },
  scoreLabel:      { fontSize:"12px", color:"#888", margin:"0 0 4px 0" },
  scoreNombre:     { fontSize:"42px", fontWeight:"500", margin:"0 0 8px 0" },
  barreContainer:  { backgroundColor:"#f0f0f0", borderRadius:"10px", height:"8px", overflow:"hidden" },
  barreFill:       { height:"100%", borderRadius:"10px", transition:"width 0.5s ease" },
  detailLabel:     { fontSize:"12px", color:"#888", margin:"16px 0 8px 0" },
  tags:            { display:"flex", flexWrap:"wrap", gap:"6px" },
  tagViolet:       { backgroundColor:"#EEEDFE", color:"#534AB7", padding:"4px 10px", borderRadius:"20px", fontSize:"12px" },
  carte:           { backgroundColor:"white", borderRadius:"12px", border:"0.5px solid #ddd", padding:"1.5rem", marginBottom:"20px" },
  carteTitre:      { fontSize:"16px", fontWeight:"500", marginBottom:"6px", color:"#333" },
  carteDesc:       { fontSize:"13px", color:"#888", marginBottom:"16px" },
};

export default ResultsPage;