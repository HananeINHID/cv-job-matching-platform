import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import API from "../services/api";

function DashboardPage() {
  const navigate = useNavigate();
  const [darkMode, setDarkMode] = useState(false);
  const [profil, setProfil]     = useState(null);
  const [loading, setLoading]   = useState(true);
  const [recherche, setRecherche] = useState("");

  useEffect(() => {
    setDarkMode(window.matchMedia("(prefers-color-scheme: dark)").matches);
  }, []);

  // Extraire le username du token JWT
  const getNomDepuisToken = () => {
    const token = localStorage.getItem("token");
    if (!token) return "Utilisateur";
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      return payload.username || "Utilisateur";
    } catch { return "Utilisateur"; }
  };

  useEffect(() => {
    const charger = async () => {
      const token = localStorage.getItem("token");
      if (!token) { setLoading(false); return; }
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
    texteLabel:      darkMode ? "#A8C4D8" : "#3D5A73",
    inputBg:     darkMode ? "#0F2030" : "#F7FAFD",
    inputBorder: darkMode ? "#1E3A5F" : "#C8DCF0",
    inputTexte:  darkMode ? "#E8F1F8" : "#1A2B3C",
    toggleBg:    darkMode ? "#1E3A5F" : "#E2EAF4",
    boutonBg:    "linear-gradient(135deg, #0E8C8C, #0A6B7C)",
    accent:      "#FF6B47",
    tealColor:   darkMode ? "#4DD9D9" : "#0E8C8C",
    tagTealBg:   darkMode ? "rgba(14,140,140,0.2)" : "#E6F7F7",
    tagTealText: darkMode ? "#4DD9D9" : "#0E8C8C",
    tagOrangeBg: darkMode ? "rgba(255,107,71,0.2)" : "#FFF0EC",
    tagOrangeText: darkMode ? "#FF9B7A" : "#CC4A25",
    statNumColor: darkMode ? "#4DD9D9" : "#0E8C8C",
    decoText:    darkMode ? "#FF9080" : "#C0392B",
    decoBorder:  darkMode ? "#3D1515" : "#FDDEDE",
    decoBg:      darkMode ? "rgba(220,80,60,0.1)" : "#FFF5F5",
  };

  const data = profil || {
    personal_info: { nom: getNomDepuisToken(), titre: "Profil non complété", ville: "" },
    hard_skills_list: [], soft_skills_list: [],
    experiences: [], formations: [],
  };

  const hardSkills = data.hard_skills_list || data.hard_skills || [];
  const softSkills = data.soft_skills_list || data.soft_skills || [];

  if (loading) return (
    <div style={{ minHeight:"100vh", width:"100%", backgroundColor: c.pageBg,
      display:"flex", alignItems:"center", justifyContent:"center" }}>
      <div style={{ textAlign:"center" }}>
        <div style={{ fontSize:"32px", marginBottom:"12px" }}>⏳</div>
        <p style={{ color: c.texteSecondaire }}>Chargement...</p>
      </div>
    </div>
  );

  return (
    <div style={{ minHeight:"100vh", width:"100%", backgroundColor: c.pageBg }}>

      {/* ── NAVBAR ── */}
      <nav style={{
        backgroundColor: c.navBg, borderBottom: `1px solid ${c.cardBorder}`,
        padding: "0 2rem", height: "64px",
        display: "flex", alignItems: "center", justifyContent: "space-between",
        position: "sticky", top: 0, zIndex: 50,
        boxShadow: darkMode ? "0 2px 20px rgba(0,0,0,0.3)" : "0 2px 20px rgba(14,90,130,0.08)",
      }}>
        <span style={{
          fontSize: "20px", fontWeight: "700",
          background: c.boutonBg,
          WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
        }}>
          💼 CV Matching
        </span>
        <div style={{ display:"flex", alignItems:"center", gap:"12px" }}>
          <span style={{
            fontSize: "13px", fontWeight: "600",
            color: c.tealColor,
            backgroundColor: c.tagTealBg,
            padding: "6px 14px", borderRadius: "20px",
            border: `1px solid ${darkMode ? "rgba(14,140,140,0.3)" : "rgba(14,140,140,0.2)"}`,
          }}>
            👤 {getNomDepuisToken()}
          </span>
          <button onClick={() => setDarkMode(!darkMode)} style={{
            width:"38px", height:"38px", borderRadius:"50%",
            border: `1px solid ${c.cardBorder}`, backgroundColor: c.toggleBg,
            fontSize:"16px", cursor:"pointer",
          }}>
            {darkMode ? "☀️" : "🌙"}
          </button>
          <button onClick={() => { localStorage.removeItem("token"); navigate("/login"); }}
            style={{
              padding: "8px 16px", backgroundColor: c.decoBg,
              color: c.decoText, border: `1px solid ${c.decoBorder}`,
              borderRadius: "10px", fontSize: "13px", fontWeight: "600", cursor: "pointer",
            }}>
            Déconnexion
          </button>
        </div>
      </nav>

      {/* ── CONTENU ── */}
      <div style={{ maxWidth:"960px", margin:"0 auto", padding:"2rem 1rem" }}>

        {/* Bienvenue */}
        <div style={{ marginBottom:"28px" }}>
          <h1 style={{ fontSize:"28px", fontWeight:"700", color: c.textePrimaire, marginBottom:"6px" }}>
            Bonjour, {getNomDepuisToken()} 👋
          </h1>
          <p style={{ fontSize:"15px", color: c.texteSecondaire }}>
            {data.personal_info?.titre || "Complétez votre profil pour commencer"}
            {data.personal_info?.ville ? ` · ${data.personal_info.ville}` : ""}
          </p>
        </div>

        {/* Barre de recherche */}
        <div style={{
          backgroundColor: c.cardBg, border: `1px solid ${c.cardBorder}`,
          borderRadius: "16px", padding: "1.5rem", marginBottom: "20px",
          boxShadow: c.cardShadow,
        }}>
          <h2 style={{ fontSize:"16px", fontWeight:"700", color: c.tealColor, marginBottom:"14px" }}>
            🔍 Trouver des offres
          </h2>
          <div style={{ display:"flex", gap:"10px" }}>
            <input
              style={{
                flex: 1, padding: "12px 16px", borderRadius: "12px",
                border: `1.5px solid ${c.inputBorder}`, backgroundColor: c.inputBg,
                color: c.inputTexte, fontSize: "14px", outline: "none",
              }}
              value={recherche}
              onChange={(e) => setRecherche(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && navigate("/results", { state: { recherche } })}
              onFocus={(e) => e.target.style.borderColor = "#0E8C8C"}
              onBlur={(e) => e.target.style.borderColor = c.inputBorder}
              placeholder="Ex: Développeur React, Data Scientist..."
            />
            <button
              onClick={() => navigate("/results", { state: { recherche } })}
              style={{
                padding: "12px 24px", background: c.boutonBg, color: "white",
                border: "none", borderRadius: "12px", fontSize: "14px",
                fontWeight: "600", cursor: "pointer", whiteSpace: "nowrap",
                boxShadow: "0 6px 16px rgba(14,140,140,0.3)",
              }}>
              Lancer →
            </button>
          </div>
        </div>

        {/* Stats */}
        <div style={{ display:"grid", gridTemplateColumns:"repeat(4,1fr)", gap:"12px", marginBottom:"20px" }}>
          {[
            { label: "Hard Skills", valeur: hardSkills.length, icon: "⚡" },
            { label: "Soft Skills", valeur: softSkills.length, icon: "🤝" },
            { label: "Expériences", valeur: data.experiences?.length || 0, icon: "💼" },
            { label: "Formations", valeur: data.formations?.length || 0, icon: "🎓" },
          ].map(({ label, valeur, icon }) => (
            <div key={label} style={{
              backgroundColor: c.cardBg, border: `1px solid ${c.cardBorder}`,
              borderRadius: "14px", padding: "1.2rem", textAlign: "center",
              boxShadow: c.cardShadow,
            }}>
              <div style={{ fontSize:"24px", marginBottom:"6px" }}>{icon}</div>
              <p style={{ fontSize:"11px", color: c.texteSecondaire, marginBottom:"4px", fontWeight:"600", textTransform:"uppercase", letterSpacing:"0.5px" }}>{label}</p>
              <p style={{ fontSize:"28px", fontWeight:"700", color: c.statNumColor, margin:0 }}>{valeur}</p>
            </div>
          ))}
        </div>

        {/* Profil */}
        <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:"16px", marginBottom:"20px" }}>

          {/* Compétences */}
          <div style={{ backgroundColor: c.cardBg, border: `1px solid ${c.cardBorder}`, borderRadius:"16px", padding:"1.5rem", boxShadow: c.cardShadow }}>
            <h3 style={{ fontSize:"14px", fontWeight:"700", color: c.tealColor, marginBottom:"14px" }}>
              ⚡ Compétences techniques
            </h3>
            <div style={{ display:"flex", flexWrap:"wrap", gap:"8px", marginBottom:"16px" }}>
              {hardSkills.length > 0 ? hardSkills.map((s) => (
                <span key={s} style={{ backgroundColor: c.tagTealBg, color: c.tagTealText, padding:"5px 12px", borderRadius:"20px", fontSize:"12px", fontWeight:"600" }}>{s}</span>
              )) : <p style={{ fontSize:"13px", color: c.texteSecondaire }}>Aucune compétence ajoutée</p>}
            </div>
            <h3 style={{ fontSize:"14px", fontWeight:"700", color: c.accent, marginBottom:"14px" }}>
              🤝 Soft Skills
            </h3>
            <div style={{ display:"flex", flexWrap:"wrap", gap:"8px" }}>
              {softSkills.length > 0 ? softSkills.map((s) => (
                <span key={s} style={{ backgroundColor: c.tagOrangeBg, color: c.tagOrangeText, padding:"5px 12px", borderRadius:"20px", fontSize:"12px", fontWeight:"600" }}>{s}</span>
              )) : <p style={{ fontSize:"13px", color: c.texteSecondaire }}>Aucun soft skill ajouté</p>}
            </div>
          </div>

          {/* Expériences & Formations */}
          <div style={{ backgroundColor: c.cardBg, border: `1px solid ${c.cardBorder}`, borderRadius:"16px", padding:"1.5rem", boxShadow: c.cardShadow }}>
            <h3 style={{ fontSize:"14px", fontWeight:"700", color: c.tealColor, marginBottom:"14px" }}>
              💼 Expériences
            </h3>
            {data.experiences?.length > 0 ? data.experiences.map((exp, i) => (
              <div key={i} style={{ borderLeft:`3px solid ${c.tealColor}`, paddingLeft:"12px", marginBottom:"12px" }}>
                <p style={{ fontSize:"13px", fontWeight:"700", color: c.textePrimaire, margin:0 }}>{exp.poste || "—"}</p>
                <p style={{ fontSize:"12px", color: c.texteSecondaire, margin:"2px 0 0" }}>{exp.entreprise || "—"}</p>
              </div>
            )) : <p style={{ fontSize:"13px", color: c.texteSecondaire }}>Aucune expérience ajoutée</p>}

            <h3 style={{ fontSize:"14px", fontWeight:"700", color: c.accent, margin:"16px 0 14px" }}>
              🎓 Formations
            </h3>
            {data.formations?.length > 0 ? data.formations.map((form, i) => (
              <div key={i} style={{ borderLeft:`3px solid ${c.accent}`, paddingLeft:"12px", marginBottom:"12px" }}>
                <p style={{ fontSize:"13px", fontWeight:"700", color: c.textePrimaire, margin:0 }}>{form.diplome || "—"}</p>
                <p style={{ fontSize:"12px", color: c.texteSecondaire, margin:"2px 0 0" }}>{form.etablissement || "—"}</p>
              </div>
            )) : <p style={{ fontSize:"13px", color: c.texteSecondaire }}>Aucune formation ajoutée</p>}
          </div>
        </div>

        {/* Bouton modifier */}
        <button onClick={() => navigate("/cv-form")} style={{
          padding:"12px 28px", backgroundColor:"transparent",
          color: c.tealColor, border:`1.5px solid ${c.tealColor}`,
          borderRadius:"12px", fontSize:"14px", fontWeight:"600", cursor:"pointer",
        }}>
          ✏️ Modifier mon profil
        </button>
      </div>
    </div>
  );
}

export default DashboardPage;