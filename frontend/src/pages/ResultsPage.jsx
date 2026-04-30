import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Chart as ChartJS, RadialLinearScale, PointElement, LineElement,
  Filler, CategoryScale, LinearScale, BarElement, ScatterController,
  Tooltip, Legend } from "chart.js";
import { Radar, Bar, Scatter } from "react-chartjs-2";
import API from "../services/api";

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler,
  CategoryScale, LinearScale, BarElement, ScatterController, Tooltip, Legend);

const MOCK_OFFRES = [
  { id:1, titre:"Développeur React Frontend", entreprise:"Capgemini Maroc",  ville:"Casablanca", contrat:"CDI",   score:87, competences:["React","JavaScript","CSS","Git"] },
  { id:2, titre:"Frontend Engineer",          entreprise:"OCP Digital",      ville:"Rabat",       contrat:"CDI",   score:74, competences:["React","TypeScript","REST API"] },
  { id:3, titre:"Développeur Full Stack",     entreprise:"StartupTech",      ville:"Casablanca",  contrat:"CDD",   score:65, competences:["React","Node.js","MongoDB"] },
  { id:4, titre:"UI Developer",               entreprise:"Sofrecom",         ville:"Casablanca",  contrat:"Stage", score:58, competences:["HTML","CSS","JavaScript"] },
  { id:5, titre:"Web Developer",              entreprise:"Maroc Telecom",    ville:"Rabat",       contrat:"CDI",   score:45, competences:["Vue.js","PHP","MySQL"] },
];

function ResultsPage() {
  const navigate   = useNavigate();
  const location   = useLocation();
  const recherche  = location.state?.recherche || "";
  const [darkMode, setDarkMode]           = useState(false);
  const [offres, setOffres]               = useState([]);
  const [offreSelectionnee, setOffre]     = useState(null);
  const [loading, setLoading]             = useState(true);
  const [onglet, setOnglet]               = useState("offres");

  useEffect(() => {
    setDarkMode(window.matchMedia("(prefers-color-scheme: dark)").matches);
  }, []);

  useEffect(() => {
    const charger = async () => {
      try {
        const response = await API.get(`/matching/results/?q=${recherche}`);
        setOffres(response.data);
        setOffre(response.data[0]);
      } catch {
        setOffres(MOCK_OFFRES);
        setOffre(MOCK_OFFRES[0]);
      } finally { setLoading(false); }
    };
    charger();
  }, []);

  const c = {
    pageBg:      darkMode ? "#0D1B2A" : "#F0F4F8",
    navBg:       darkMode ? "#0F2030" : "#FFFFFF",
    cardBg:      darkMode ? "#1A2B3C" : "#FFFFFF",
    cardBorder:  darkMode ? "#1E3A5F" : "#E2EAF4",
    cardShadow:  darkMode ? "0 4px 20px rgba(0,0,0,0.3)" : "0 4px 20px rgba(14,90,130,0.06)",
    textePrimaire:   darkMode ? "#E8F1F8" : "#1A2B3C",
    texteSecondaire: darkMode ? "#7A9BB5" : "#5A7184",
    tealColor:   darkMode ? "#4DD9D9" : "#0E8C8C",
    accent:      "#FF6B47",
    toggleBg:    darkMode ? "#1E3A5F" : "#E2EAF4",
    tagTealBg:   darkMode ? "rgba(14,140,140,0.2)" : "#E6F7F7",
    tagTealText: darkMode ? "#4DD9D9" : "#0E8C8C",
    boutonBg:    "linear-gradient(135deg, #0E8C8C, #0A6B7C)",
    inputBg:     darkMode ? "#0F2030" : "#F7FAFD",
    inputBorder: darkMode ? "#1E3A5F" : "#C8DCF0",
    inputTexte:  darkMode ? "#E8F1F8" : "#1A2B3C",
  };

  const couleurScore = (score) => {
    if (score >= 75) return { bg: darkMode ? "rgba(14,140,100,0.2)" : "#F0FFF8", txt: darkMode ? "#50E0A0" : "#0A6B4A" };
    if (score >= 50) return { bg: darkMode ? "rgba(255,160,0,0.2)" : "#FFFBF0", txt: darkMode ? "#FFD070" : "#996600" };
    return { bg: darkMode ? "rgba(220,80,60,0.2)" : "#FFF0EE", txt: darkMode ? "#FF9080" : "#C0392B" };
  };

  const radarData = {
    labels: ["React", "JavaScript", "CSS", "Python", "SQL", "Git"],
    datasets: [
      { label:"Votre profil", data:[90,80,75,60,50,70],
        backgroundColor:"rgba(14,140,140,0.2)", borderColor:"#0E8C8C",
        borderWidth:2, pointBackgroundColor:"#0E8C8C" },
      { label:"Offre sélectionnée", data:[95,90,70,30,40,80],
        backgroundColor:"rgba(255,107,71,0.15)", borderColor:"#FF6B47",
        borderWidth:2, pointBackgroundColor:"#FF6B47" },
    ],
  };

  const barScoresData = {
    labels: offres.map((o) => o.entreprise),
    datasets: [{ label:"Score (%)", data: offres.map((o) => o.score),
      backgroundColor: offres.map((o) => o.score>=75?"#0E8C8C": o.score>=50?"#F0A500":"#E24B4A"),
      borderRadius: 8 }],
  };

  const competencesData = {
    labels: ["React","JavaScript","Python","Django","SQL","Node.js","CSS","Git"],
    datasets: [{ label:"Fréquence", data:[95,88,75,70,65,60,58,55],
      backgroundColor:"#0E8C8C", borderRadius:6 }],
  };

  const clusterData = {
    datasets: [
      { label:"Frontend", data:[{x:20,y:80},{x:25,y:75},{x:30,y:85}], backgroundColor:"#0E8C8C", pointRadius:10 },
      { label:"Data",     data:[{x:70,y:40},{x:75,y:35},{x:65,y:45}], backgroundColor:"#FF6B47", pointRadius:10 },
      { label:"Fullstack",data:[{x:50,y:60},{x:55,y:55},{x:48,y:65}], backgroundColor:"#764BA2", pointRadius:10 },
    ],
  };

  const chartOptions = (darkMode) => ({
    plugins: { legend: { labels: { color: darkMode ? "#E8F1F8" : "#1A2B3C" } } },
    scales: {
      x: { ticks: { color: darkMode ? "#7A9BB5" : "#5A7184" }, grid: { color: darkMode ? "rgba(255,255,255,0.05)" : "rgba(0,0,0,0.05)" } },
      y: { ticks: { color: darkMode ? "#7A9BB5" : "#5A7184" }, grid: { color: darkMode ? "rgba(255,255,255,0.05)" : "rgba(0,0,0,0.05)" } },
    },
  });

  if (loading) return (
    <div style={{ minHeight:"100vh", width:"100%", backgroundColor: c.pageBg,
      display:"flex", alignItems:"center", justifyContent:"center" }}>
      <p style={{ color: c.texteSecondaire, fontSize:"16px" }}>⏳ Analyse en cours...</p>
    </div>
  );

  return (
    <div style={{ minHeight:"100vh", width:"100%", backgroundColor: c.pageBg }}>

      {/* Navbar */}
      <nav style={{
        backgroundColor: c.navBg, borderBottom: `1px solid ${c.cardBorder}`,
        padding:"0 2rem", height:"64px",
        display:"flex", alignItems:"center", justifyContent:"space-between",
        position:"sticky", top:0, zIndex:50,
        boxShadow: darkMode ? "0 2px 20px rgba(0,0,0,0.3)" : "0 2px 20px rgba(14,90,130,0.08)",
      }}>
        <span style={{ fontSize:"20px", fontWeight:"700", background: c.boutonBg,
          WebkitBackgroundClip:"text", WebkitTextFillColor:"transparent" }}>
          💼 CV Matching
        </span>
        <div style={{ display:"flex", gap:"10px", alignItems:"center" }}>
          <button onClick={() => navigate("/dashboard")} style={{
            padding:"8px 16px", backgroundColor:"transparent",
            color: c.texteSecondaire, border:`1px solid ${c.cardBorder}`,
            borderRadius:"10px", fontSize:"13px", cursor:"pointer",
          }}>← Dashboard</button>
          <button onClick={() => setDarkMode(!darkMode)} style={{
            width:"38px", height:"38px", borderRadius:"50%",
            border:`1px solid ${c.cardBorder}`, backgroundColor: c.toggleBg,
            fontSize:"16px", cursor:"pointer",
          }}>{darkMode ? "☀️" : "🌙"}</button>
        </div>
      </nav>

      <div style={{ maxWidth:"1050px", margin:"0 auto", padding:"2rem 1rem" }}>

        <h1 style={{ fontSize:"26px", fontWeight:"700", color: c.textePrimaire, marginBottom:"4px" }}>
          Résultats de matching
        </h1>
        {recherche && <p style={{ fontSize:"14px", color: c.texteSecondaire, marginBottom:"20px" }}>
          Recherche : « {recherche} »
        </p>}

        {/* Onglets */}
        <div style={{ display:"flex", gap:"8px", marginBottom:"24px" }}>
          {[
            { id:"offres",      label:"📋 Offres" },
            { id:"graphiques",  label:"📊 Graphiques" },
            { id:"clusters",    label:"🔵 Clusters" },
          ].map(({ id, label }) => (
            <button key={id} onClick={() => setOnglet(id)} style={{
              padding:"10px 22px",
              background: onglet === id ? c.boutonBg : "transparent",
              color: onglet === id ? "white" : c.texteSecondaire,
              border: onglet === id ? "none" : `1px solid ${c.cardBorder}`,
              borderRadius:"10px", fontSize:"14px", fontWeight:"600",
              cursor:"pointer",
              boxShadow: onglet === id ? "0 4px 12px rgba(14,140,140,0.3)" : "none",
            }}>
              {label}
            </button>
          ))}
        </div>

        {/* ── ONGLET OFFRES ── */}
        {onglet === "offres" && (
          <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:"16px" }}>

            <div>
              {offres.map((offre) => {
                const sc = couleurScore(offre.score);
                const actif = offreSelectionnee?.id === offre.id;
                return (
                  <div key={offre.id} onClick={() => setOffre(offre)} style={{
                    backgroundColor: c.cardBg,
                    border: actif ? `2px solid ${c.tealColor}` : `1px solid ${c.cardBorder}`,
                    borderRadius:"14px", padding:"1rem", marginBottom:"10px",
                    cursor:"pointer", boxShadow: actif ? `0 0 0 3px ${darkMode?"rgba(14,140,140,0.2)":"rgba(14,140,140,0.1)"}` : c.cardShadow,
                    transition:"all 0.2s",
                  }}>
                    <div style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start" }}>
                      <div>
                        <p style={{ fontSize:"14px", fontWeight:"700", color: c.textePrimaire, margin:0 }}>{offre.titre}</p>
                        <p style={{ fontSize:"12px", color: c.texteSecondaire, margin:"4px 0 0" }}>{offre.entreprise} · {offre.ville}</p>
                      </div>
                      <span style={{ backgroundColor: sc.bg, color: sc.txt,
                        padding:"5px 12px", borderRadius:"20px", fontSize:"13px", fontWeight:"700" }}>
                        {offre.score}%
                      </span>
                    </div>
                    <span style={{ backgroundColor: c.tagTealBg, color: c.tagTealText,
                      padding:"3px 10px", borderRadius:"20px", fontSize:"11px",
                      fontWeight:"600", marginTop:"8px", display:"inline-block" }}>
                      {offre.contrat}
                    </span>
                  </div>
                );
              })}
            </div>

            {offreSelectionnee && (
              <div style={{ backgroundColor: c.cardBg, border:`1px solid ${c.cardBorder}`,
                borderRadius:"16px", padding:"1.5rem", alignSelf:"flex-start",
                boxShadow: c.cardShadow, position:"sticky", top:"80px" }}>
                <h2 style={{ fontSize:"18px", fontWeight:"700", color: c.textePrimaire, marginBottom:"4px" }}>
                  {offreSelectionnee.titre}
                </h2>
                <p style={{ fontSize:"13px", color: c.texteSecondaire, marginBottom:"20px" }}>
                  {offreSelectionnee.entreprise} · {offreSelectionnee.ville}
                </p>

                <p style={{ fontSize:"12px", color: c.texteSecondaire, margin:"0 0 6px" }}>Score de compatibilité</p>
                <p style={{ fontSize:"44px", fontWeight:"700", margin:"0 0 10px",
                  color: couleurScore(offreSelectionnee.score).txt }}>
                  {offreSelectionnee.score}%
                </p>
                <div style={{ backgroundColor: darkMode?"#0F2030":"#F0F4F8", borderRadius:"10px", height:"8px", overflow:"hidden", marginBottom:"20px" }}>
                  <div style={{ height:"100%", borderRadius:"10px",
                    width:`${offreSelectionnee.score}%`,
                    background: c.boutonBg, transition:"width 0.5s ease" }}/>
                </div>

                <p style={{ fontSize:"12px", fontWeight:"600", color: c.texteSecondaire, marginBottom:"10px", textTransform:"uppercase", letterSpacing:"0.5px" }}>
                  Compétences requises
                </p>
                <div style={{ display:"flex", flexWrap:"wrap", gap:"6px" }}>
                  {offreSelectionnee.competences.map((comp) => (
                    <span key={comp} style={{ backgroundColor: c.tagTealBg, color: c.tagTealText,
                      padding:"5px 12px", borderRadius:"20px", fontSize:"12px", fontWeight:"600" }}>
                      {comp}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* ── ONGLET GRAPHIQUES ── */}
        {onglet === "graphiques" && (
          <div>
            {[
              { titre:"Vos compétences vs l'offre", desc:"Teal = votre profil · Orange = offre sélectionnée",
                composant: <div style={{ maxWidth:"420px", margin:"0 auto" }}>
                  <Radar data={radarData} options={{ ...chartOptions(darkMode), scales: { r: { beginAtZero:true, max:100, ticks:{ color: darkMode?"#7A9BB5":"#5A7184" }, grid:{ color: darkMode?"rgba(255,255,255,0.08)":"rgba(0,0,0,0.08)" }, pointLabels:{ color: darkMode?"#E8F1F8":"#1A2B3C" } } }, plugins:{ legend:{ labels:{ color: darkMode?"#E8F1F8":"#1A2B3C" } } } }}/>
                </div> },
              { titre:"Score de matching par offre", desc:"Vert ≥ 75% · Orange 50-75% · Rouge < 50%",
                composant: <Bar data={barScoresData} options={{ ...chartOptions(darkMode), scales:{ y:{ beginAtZero:true, max:100, ticks:{color: darkMode?"#7A9BB5":"#5A7184"}, grid:{color: darkMode?"rgba(255,255,255,0.05)":"rgba(0,0,0,0.05)"} }, x:{ticks:{color: darkMode?"#7A9BB5":"#5A7184"}, grid:{color: darkMode?"rgba(255,255,255,0.05)":"rgba(0,0,0,0.05)"}} }, plugins:{legend:{display:false}} }}/> },
              { titre:"Compétences les plus demandées", desc:"Fréquence d'apparition dans toutes les offres",
                composant: <Bar data={competencesData} options={{ ...chartOptions(darkMode), indexAxis:"y", scales:{ x:{beginAtZero:true, max:100, ticks:{color: darkMode?"#7A9BB5":"#5A7184"}, grid:{color: darkMode?"rgba(255,255,255,0.05)":"rgba(0,0,0,0.05)"}}, y:{ticks:{color: darkMode?"#7A9BB5":"#5A7184"}, grid:{color: darkMode?"rgba(255,255,255,0.05)":"rgba(0,0,0,0.05)"}} }, plugins:{legend:{display:false}} }}/> },
            ].map(({ titre, desc, composant }) => (
              <div key={titre} style={{ backgroundColor: c.cardBg, border:`1px solid ${c.cardBorder}`,
                borderRadius:"16px", padding:"1.5rem", marginBottom:"16px", boxShadow: c.cardShadow }}>
                <h2 style={{ fontSize:"16px", fontWeight:"700", color: c.textePrimaire, marginBottom:"4px" }}>{titre}</h2>
                <p style={{ fontSize:"13px", color: c.texteSecondaire, marginBottom:"16px" }}>{desc}</p>
                {composant}
              </div>
            ))}
          </div>
        )}

        {/* ── ONGLET CLUSTERS ── */}
        {onglet === "clusters" && (
          <div style={{ backgroundColor: c.cardBg, border:`1px solid ${c.cardBorder}`,
            borderRadius:"16px", padding:"1.5rem", boxShadow: c.cardShadow }}>
            <h2 style={{ fontSize:"16px", fontWeight:"700", color: c.textePrimaire, marginBottom:"4px" }}>
              Clusters K-Means — regroupement des offres
            </h2>
            <p style={{ fontSize:"13px", color: c.texteSecondaire, marginBottom:"16px" }}>
              Chaque point = une offre. Les couleurs = le cluster détecté par l'algorithme de Youssef.
            </p>
            <Scatter data={clusterData} options={{ ...chartOptions(darkMode), plugins:{ legend:{ position:"bottom", labels:{ color: darkMode?"#E8F1F8":"#1A2B3C" } } } }}/>
          </div>
        )}
      </div>
    </div>
  );
}

export default ResultsPage;