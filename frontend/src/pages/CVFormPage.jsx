import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { 
  Briefcase, ArrowLeft, Sun, Moon, AlertTriangle, X, Plus, Save 
} from "lucide-react";
import API from "../services/api";

function CVFormPage() {
  const navigate = useNavigate();
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem("darkMode");
    if (saved !== null) return saved === "true";
    return window.matchMedia("(prefers-color-scheme: dark)").matches;
  });
  const [nom, setNom]             = useState("");
  const [email, setEmail]         = useState("");
  const [telephone, setTelephone] = useState("");
  const [ville, setVille]         = useState("");
  const [titre, setTitre]         = useState("");
  const [hardSkillInput, setHardSkillInput] = useState("");
  const [softSkillInput, setSoftSkillInput] = useState("");
  const [hardSkills, setHardSkills] = useState([]);
  const [softSkills, setSoftSkills] = useState([]);
  const [experiences, setExperiences] = useState([
    { poste: "", entreprise: "", debut: "", fin: "", description: "" }
  ]);
  const [formations, setFormations] = useState([
    { diplome: "", etablissement: "", annee: "", domaine: "" }
  ]);
  const [erreur, setErreur] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    localStorage.setItem("darkMode", darkMode);
  }, [darkMode]);

  const c = {
    pageBg:      darkMode ? "#0D1B2A" : "#F0F4F8",
    cardBg:      darkMode ? "#1A2B3C" : "#FFFFFF",
    cardBorder:  darkMode ? "#1E3A5F" : "#E2EAF4",
    navBg:       darkMode ? "#0F2030" : "#FFFFFF",
    textePrimaire:   darkMode ? "#E8F1F8" : "#1A2B3C",
    texteSecondaire: darkMode ? "#7A9BB5" : "#5A7184",
    texteLabel:      darkMode ? "#A8C4D8" : "#3D5A73",
    sectionTitreColor: darkMode ? "#4DD9D9" : "#0E8C8C",
    inputBg:     darkMode ? "#0F2030" : "#F7FAFD",
    inputBorder: darkMode ? "#1E3A5F" : "#C8DCF0",
    inputTexte:  darkMode ? "#E8F1F8" : "#1A2B3C",
    toggleBg:    darkMode ? "#1E3A5F" : "#E2EAF4",
    boutonBg:    "linear-gradient(135deg, #0E8C8C, #0A6B7C)",
    accent:      "#FF6B47",
    tagTealBg:   darkMode ? "rgba(14,140,140,0.2)" : "#E6F7F7",
    tagTealText: darkMode ? "#4DD9D9" : "#0E8C8C",
    tagOrangeBg: darkMode ? "rgba(255,107,71,0.2)" : "#FFF0EC",
    tagOrangeText: darkMode ? "#FF9B7A" : "#CC4A25",
    erreurBg:    darkMode ? "rgba(220,80,60,0.15)" : "#FFF0EE",
    erreurBorder:"rgba(220,80,60,0.3)",
    erreurTexte: darkMode ? "#FF9080" : "#C0392B",
    itemBg:      darkMode ? "#0F2030" : "#F7FAFD",
    itemBorder:  darkMode ? "#1E3A5F" : "#E2EAF4",
    suppressBg:  darkMode ? "rgba(220,80,60,0.15)" : "#FFF0EE",
    suppressText:darkMode ? "#FF9080" : "#C0392B",
  };

  const ajouterHardSkill = () => {
    if (hardSkillInput.trim() && !hardSkills.includes(hardSkillInput.trim())) {
      setHardSkills([...hardSkills, hardSkillInput.trim()]);
      setHardSkillInput("");
    }
  };
  const ajouterSoftSkill = () => {
    if (softSkillInput.trim() && !softSkills.includes(softSkillInput.trim())) {
      setSoftSkills([...softSkills, softSkillInput.trim()]);
      setSoftSkillInput("");
    }
  };
  const modifierExperience = (i, champ, val) => {
    const cp = [...experiences]; cp[i][champ] = val; setExperiences(cp);
  };
  const modifierFormation = (i, champ, val) => {
    const cp = [...formations]; cp[i][champ] = val; setFormations(cp);
  };

  const handleSubmit = async () => {
    setErreur("");
    if (!nom || !email || !titre) {
      setErreur("Veuillez remplir : nom, email et titre."); return;
    }
    if (hardSkills.length === 0) {
      setErreur("Ajoutez au moins une compétence technique."); return;
    }
    setLoading(true);
    try {
      await API.post("/profile/cv/", {
        personal_info: { nom, email, telephone, ville, titre },
        hard_skills: hardSkills,
        soft_skills: softSkills,
        experiences: experiences.filter(e => e.poste || e.entreprise),
        formations: formations.filter(f => f.diplome || f.etablissement),
      });
      navigate("/dashboard");
    } catch (error) {
      setErreur("Erreur: " + JSON.stringify(error.response?.data));
    } finally {
      setLoading(false);
    }
  };

  const inputStyle = {
    width: "100%", padding: "11px 14px", borderRadius: "10px",
    border: `1.5px solid ${c.inputBorder}`, backgroundColor: c.inputBg,
    color: c.inputTexte, fontSize: "14px", boxSizing: "border-box", outline: "none",
  };

  const labelStyle = {
    display: "block", fontSize: "12px", fontWeight: "600",
    color: c.texteLabel, marginBottom: "6px",
  };

  const sectionStyle = {
    backgroundColor: c.cardBg, border: `1px solid ${c.cardBorder}`,
    borderRadius: "16px", padding: "1.5rem", marginBottom: "16px",
    boxShadow: darkMode ? "0 4px 20px rgba(0,0,0,0.3)" : "0 4px 20px rgba(14,90,130,0.06)",
  };

  return (
    <div style={{ minHeight: "100vh", width: "100%", backgroundColor: c.pageBg }}>

      {/* Navbar */}
      <nav style={{
        backgroundColor: c.navBg, borderBottom: `1px solid ${c.cardBorder}`,
        padding: "0 2rem", height: "60px",
        display: "flex", alignItems: "center", justifyContent: "space-between",
        position: "sticky", top: 0, zIndex: 50,
      }}>
        <span style={{
          fontSize: "18px", fontWeight: "700",
          background: c.boutonBg, WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent",
          display: "flex", alignItems: "center", gap: "8px"
        }}>
          <Briefcase size={20} style={{ color: "#0E8C8C" }} /> CV Matching
        </span>
        <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
          <button onClick={() => navigate("/dashboard")} style={{
            padding: "8px 16px", background: "transparent",
            color: c.texteSecondaire, border: `1px solid ${c.cardBorder}`,
            borderRadius: "10px", fontSize: "13px", cursor: "pointer",
            display: "flex", alignItems: "center", gap: "6px"
          }}>
            <ArrowLeft size={14} /> Dashboard
          </button>
          <button onClick={() => setDarkMode(!darkMode)} style={{
            width: "38px", height: "38px", borderRadius: "50%",
            border: `1px solid ${c.cardBorder}`, backgroundColor: c.toggleBg,
            fontSize: "16px", cursor: "pointer",
            display: "flex", alignItems: "center", justifyContent: "center"
          }}>
            {darkMode ? <Sun size={18} color="#FFB300" /> : <Moon size={18} color="#5A7184" />}
          </button>
        </div>
      </nav>

      {/* Contenu */}
      <div style={{ width: "100%", margin: "0 auto", padding: "2rem 1rem", boxSizing: "border-box" }}>

        <h1 style={{ fontSize: "24px", fontWeight: "700", color: c.textePrimaire, marginBottom: "4px" }}>
          Mon Profil CV
        </h1>
        <p style={{ fontSize: "14px", color: c.texteSecondaire, marginBottom: "24px" }}>
          Remplissez vos informations pour trouver les offres qui vous correspondent
        </p>

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

        {/* Section 1 */}
        <div style={sectionStyle}>
          <h2 style={{ fontSize: "15px", fontWeight: "700", color: c.sectionTitreColor, marginBottom: "16px", paddingBottom: "10px", borderBottom: `1px solid ${c.cardBorder}` }}>
            1. Informations personnelles
          </h2>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
            {[
              { label: "Nom complet *", val: nom, set: setNom, ph: "Rachid Alami", type: "text" },
              { label: "Email *", val: email, set: setEmail, ph: "rachid@email.com", type: "email" },
              { label: "Téléphone", val: telephone, set: setTelephone, ph: "+212 6XX XXX XXX", type: "text" },
              { label: "Ville", val: ville, set: setVille, ph: "Casablanca", type: "text" },
            ].map(({ label, val, set, ph, type }) => (
              <div key={label}>
                <label style={labelStyle}>{label}</label>
                <input type={type} placeholder={ph} value={val}
                  onChange={(e) => set(e.target.value)} style={inputStyle}
                  onFocus={(e) => e.target.style.borderColor = "#0E8C8C"}
                  onBlur={(e) => e.target.style.borderColor = c.inputBorder}
                />
              </div>
            ))}
          </div>
          <div style={{ marginTop: "12px" }}>
            <label style={labelStyle}>Titre du poste recherché *</label>
            <input type="text" placeholder="Développeur Frontend React"
              value={titre} onChange={(e) => setTitre(e.target.value)}
              style={inputStyle}
              onFocus={(e) => e.target.style.borderColor = "#0E8C8C"}
              onBlur={(e) => e.target.style.borderColor = c.inputBorder}
            />
          </div>
        </div>

        {/* Section 2 — Compétences */}
        <div style={sectionStyle}>
          <h2 style={{ fontSize: "15px", fontWeight: "700", color: c.sectionTitreColor, marginBottom: "16px", paddingBottom: "10px", borderBottom: `1px solid ${c.cardBorder}` }}>
            2. Compétences
          </h2>

          {/* Hard Skills */}
          <div style={{ marginBottom: "16px" }}>
            <label style={labelStyle}>Compétences techniques (Hard Skills)</label>
            <div style={{ display: "flex", gap: "8px" }}>
              <input type="text" placeholder="React, Python... puis Entrée"
                value={hardSkillInput}
                onChange={(e) => setHardSkillInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && ajouterHardSkill()}
                style={{ ...inputStyle, flex: 1 }}
                onFocus={(e) => e.target.style.borderColor = "#0E8C8C"}
                onBlur={(e) => e.target.style.borderColor = c.inputBorder}
              />
              <button onClick={ajouterHardSkill} style={{
                padding: "11px 18px", background: c.boutonBg, color: "white",
                border: "none", borderRadius: "10px", fontSize: "13px",
                fontWeight: "600", cursor: "pointer", whiteSpace: "nowrap",
              }}>
                Ajouter
              </button>
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginTop: "10px" }}>
              {hardSkills.map((s) => (
                <span key={s} style={{
                  backgroundColor: c.tagTealBg, color: c.tagTealText,
                  padding: "5px 12px", borderRadius: "20px", fontSize: "13px",
                  display: "flex", alignItems: "center", gap: "6px",
                  border: `1px solid ${darkMode ? "rgba(14,140,140,0.3)" : "rgba(14,140,140,0.2)"}`,
                }}>
                  {s}
                  {s}
                  <span onClick={() => setHardSkills(hardSkills.filter(x => x !== s))}
                    style={{ cursor: "pointer", display: "flex", alignItems: "center", opacity: 0.7 }}>
                    <X size={12} />
                  </span>
                </span>
              ))}
            </div>
          </div>

          {/* Soft Skills */}
          <div>
            <label style={labelStyle}>Compétences humaines (Soft Skills)</label>
            <div style={{ display: "flex", gap: "8px" }}>
              <input type="text" placeholder="Communication, Travail en équipe..."
                value={softSkillInput}
                onChange={(e) => setSoftSkillInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && ajouterSoftSkill()}
                style={{ ...inputStyle, flex: 1 }}
                onFocus={(e) => e.target.style.borderColor = "#0E8C8C"}
                onBlur={(e) => e.target.style.borderColor = c.inputBorder}
              />
              <button onClick={ajouterSoftSkill} style={{
                padding: "11px 18px", background: c.boutonBg, color: "white",
                border: "none", borderRadius: "10px", fontSize: "13px",
                fontWeight: "600", cursor: "pointer", whiteSpace: "nowrap",
              }}>
                Ajouter
              </button>
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginTop: "10px" }}>
              {softSkills.map((s) => (
                <span key={s} style={{
                  backgroundColor: c.tagOrangeBg, color: c.tagOrangeText,
                  padding: "5px 12px", borderRadius: "20px", fontSize: "13px",
                  display: "flex", alignItems: "center", gap: "6px",
                  border: `1px solid ${darkMode ? "rgba(255,107,71,0.3)" : "rgba(255,107,71,0.2)"}`,
                }}>
                  {s}
                  {s}
                  <span onClick={() => setSoftSkills(softSkills.filter(x => x !== s))}
                    style={{ cursor: "pointer", display: "flex", alignItems: "center", opacity: 0.7 }}>
                    <X size={12} />
                  </span>
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Section 3 — Expériences */}
        <div style={sectionStyle}>
          <h2 style={{ fontSize: "15px", fontWeight: "700", color: c.sectionTitreColor, marginBottom: "16px", paddingBottom: "10px", borderBottom: `1px solid ${c.cardBorder}` }}>
            3. Expériences professionnelles
          </h2>
          {experiences.map((exp, i) => (
            <div key={i} style={{
              backgroundColor: c.itemBg, border: `1px solid ${c.itemBorder}`,
              borderRadius: "12px", padding: "1rem", marginBottom: "12px",
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "12px" }}>
                <span style={{ fontSize: "13px", fontWeight: "600", color: c.texteSecondaire }}>
                  Expérience {i + 1}
                </span>
                {experiences.length > 1 && (
                    <button onClick={() => setExperiences(experiences.filter((_, x) => x !== i))}
                      style={{ padding: "4px 10px", backgroundColor: c.suppressBg,
                        color: c.suppressText, border: "none", borderRadius: "8px",
                        fontSize: "12px", cursor: "pointer", display: "flex", alignItems: "center", gap: "4px" }}>
                      <X size={12} /> Supprimer
                    </button>
                )}
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
                {[
                  { label: "Poste occupé", champ: "poste", ph: "Développeur Frontend" },
                  { label: "Entreprise", champ: "entreprise", ph: "TechMaroc" },
                  { label: "Date début", champ: "debut", type: "month" },
                  { label: "Date fin", champ: "fin", type: "month" },
                ].map(({ label, champ, ph, type }) => (
                  <div key={champ}>
                    <label style={labelStyle}>{label}</label>
                    <input type={type || "text"} placeholder={ph} value={exp[champ]}
                      onChange={(e) => modifierExperience(i, champ, e.target.value)}
                      style={inputStyle}
                      onFocus={(e) => e.target.style.borderColor = "#0E8C8C"}
                      onBlur={(e) => e.target.style.borderColor = c.inputBorder}
                    />
                  </div>
                ))}
              </div>
              <div style={{ marginTop: "10px" }}>
                <label style={labelStyle}>Description</label>
                <textarea placeholder="Décrivez vos responsabilités..." value={exp.description}
                  onChange={(e) => modifierExperience(i, "description", e.target.value)}
                  rows={3} style={{ ...inputStyle, resize: "vertical", fontFamily: "inherit" }}
                  onFocus={(e) => e.target.style.borderColor = "#0E8C8C"}
                  onBlur={(e) => e.target.style.borderColor = c.inputBorder}
                />
              </div>
            </div>
          ))}
          <button onClick={() => setExperiences([...experiences, { poste:"", entreprise:"", debut:"", fin:"", description:"" }])}
            style={{ padding: "10px 18px", backgroundColor: "transparent",
              color: c.sectionTitreColor, border: `1.5px solid ${c.sectionTitreColor}`,
              borderRadius: "10px", fontSize: "13px", fontWeight: "600", cursor: "pointer",
              display: "flex", alignItems: "center", gap: "8px" }}>
            <Plus size={16} /> Ajouter une expérience
          </button>
        </div>

        {/* Section 4 — Formations */}
        <div style={sectionStyle}>
          <h2 style={{ fontSize: "15px", fontWeight: "700", color: c.sectionTitreColor, marginBottom: "16px", paddingBottom: "10px", borderBottom: `1px solid ${c.cardBorder}` }}>
            4. Formations
          </h2>
          {formations.map((form, i) => (
            <div key={i} style={{
              backgroundColor: c.itemBg, border: `1px solid ${c.itemBorder}`,
              borderRadius: "12px", padding: "1rem", marginBottom: "12px",
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "12px" }}>
                <span style={{ fontSize: "13px", fontWeight: "600", color: c.texteSecondaire }}>
                  Formation {i + 1}
                </span>
                {formations.length > 1 && (
                    <button onClick={() => setFormations(formations.filter((_, x) => x !== i))}
                      style={{ padding: "4px 10px", backgroundColor: c.suppressBg,
                        color: c.suppressText, border: "none", borderRadius: "8px",
                        fontSize: "12px", cursor: "pointer", display: "flex", alignItems: "center", gap: "4px" }}>
                      <X size={12} /> Supprimer
                    </button>
                )}
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
                {[
                  { label: "Diplôme", champ: "diplome", ph: "Licence IASD" },
                  { label: "Établissement", champ: "etablissement", ph: "FSS Marrakech" },
                  { label: "Année", champ: "annee", ph: "2026", type: "number" },
                  { label: "Domaine", champ: "domaine", ph: "Informatique / IA" },
                ].map(({ label, champ, ph, type }) => (
                  <div key={champ}>
                    <label style={labelStyle}>{label}</label>
                    <input type={type || "text"} placeholder={ph} value={form[champ]}
                      onChange={(e) => modifierFormation(i, champ, e.target.value)}
                      style={inputStyle}
                      onFocus={(e) => e.target.style.borderColor = "#0E8C8C"}
                      onBlur={(e) => e.target.style.borderColor = c.inputBorder}
                    />
                  </div>
                ))}
              </div>
            </div>
          ))}
          <button onClick={() => setFormations([...formations, { diplome:"", etablissement:"", annee:"", domaine:"" }])}
            style={{ padding: "10px 18px", backgroundColor: "transparent",
              color: c.sectionTitreColor, border: `1.5px solid ${c.sectionTitreColor}`,
              borderRadius: "10px", fontSize: "13px", fontWeight: "600", cursor: "pointer",
              display: "flex", alignItems: "center", gap: "8px" }}>
            <Plus size={16} /> Ajouter une formation
          </button>
        </div>

          <button onClick={handleSubmit}
            style={{
              width: "100%", padding: "16px",
              background: loading ? "#888" : c.boutonBg,
              color: "white", border: "none", borderRadius: "14px",
              fontSize: "16px", fontWeight: "700", cursor: loading ? "not-allowed" : "pointer",
              boxShadow: "0 8px 24px rgba(14,140,140,0.35)", marginBottom: "2rem",
              display: "flex", alignItems: "center", justifyContent: "center", gap: "10px"
            }}
            disabled={loading}
          >
            {loading ? "Enregistrement..." : <>Enregistrer et continuer <Save size={18} /></>}
          </button>
      </div>
    </div>
  );
}

export default CVFormPage;