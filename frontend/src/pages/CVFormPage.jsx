import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { AlertTriangle, X, Plus, Save } from "lucide-react";
import API from "../services/api";
import AppShell from "../components/AppShell";
import { Button } from "../components/ui/Button";
import toast from "react-hot-toast";

function CVFormPage() {
  const navigate = useNavigate();
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

  const c = {
    pageBg:      "var(--bg-main)",
    cardBg:      "var(--bg-surface)",
    cardBorder:  "var(--border-color)",
    navBg:       "var(--bg-surface)",
    textePrimaire:   "var(--text-main)",
    texteSecondaire: "var(--text-muted)",
    texteLabel:      "var(--text-muted)",
    sectionTitreColor: "var(--color-primary)",
    inputBg:     "var(--bg-main)",
    inputBorder: "var(--border-color)",
    inputTexte:  "var(--text-main)",
    toggleBg:    "var(--color-neutral-100)",
    boutonBg:    "linear-gradient(135deg, var(--color-primary), #4F46E5)",
    accent:      "var(--color-warning)",
    tagTealBg:   "var(--color-primary-light)",
    tagTealText: "var(--color-primary)",
    tagOrangeBg: "rgba(245, 158, 11, 0.1)",
    tagOrangeText: "var(--color-warning)",
    erreurBg:    "rgba(239, 68, 68, 0.08)",
    erreurBorder:"rgba(239, 68, 68, 0.3)",
    erreurTexte: "var(--color-danger)",
    itemBg:      "var(--bg-main)",
    itemBorder:  "var(--border-color)",
    suppressBg:  "rgba(239, 68, 68, 0.08)",
    suppressText:"var(--color-danger)",
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
      const msg = "Veuillez remplir : nom, email et titre.";
      setErreur(msg); toast.error(msg); return;
    }
    if (hardSkills.length === 0) {
      const msg = "Ajoutez au moins une compétence technique.";
      setErreur(msg); toast.error(msg); return;
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
      toast.success("Profil enregistré avec succès !");
      navigate("/dashboard");
    } catch (error) {
      const msg = "Erreur: " + JSON.stringify(error.response?.data);
      setErreur(msg); toast.error("Échec de l'enregistrement.");
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
    boxShadow: "var(--shadow-md)",
  };

  return (
    <AppShell title="Mon Profil CV" breadcrumb="Dashboard / Mon Profil">
      <p style={{ fontSize: "14px", color: "var(--text-muted)", marginBottom: "24px" }}>
        Remplissez vos informations pour trouver les offres qui vous correspondent.
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
                  border: `1px solid rgba(14,140,140,0.25)`,
                }}>
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
                  border: `1px solid rgba(255,107,71,0.25)`,
                }}>
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
              background: loading ? "var(--text-muted)" : "linear-gradient(135deg, var(--color-primary), #4F46E5)",
              color: "white", border: "none", borderRadius: "14px",
              fontSize: "16px", fontWeight: "700", cursor: loading ? "not-allowed" : "pointer",
              boxShadow: loading ? "none" : "0 6px 20px rgba(37,99,235,0.35)", marginBottom: "2rem",
              display: "flex", alignItems: "center", justifyContent: "center", gap: "10px",
              transition: "all 0.2s ease", fontFamily: "inherit",
            }}
            disabled={loading}
            onMouseEnter={e => { if (!loading) e.currentTarget.style.transform = "translateY(-1px)"; }}
            onMouseLeave={e => { e.currentTarget.style.transform = "translateY(0)"; }}
          >
            {loading ? (
              <>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" style={{ animation: "spin 1s linear infinite" }}>
                  <circle cx="12" cy="12" r="10" stroke="rgba(255,255,255,0.3)" strokeWidth="3" />
                  <path d="M12 2a10 10 0 0 1 10 10" stroke="white" strokeWidth="3" strokeLinecap="round" />
                </svg>
                Enregistrement en cours…
              </>
            ) : (
              <>Enregistrer le profil <Save size={18} /></>
            )}
          </button>
          <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </AppShell>
  );
}

export default CVFormPage;