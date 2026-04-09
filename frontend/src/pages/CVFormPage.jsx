import { useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../services/api";

function CVFormPage() {
  const navigate = useNavigate();

  // ── Section 1 : Infos personnelles ──
  const [nom, setNom]             = useState("");
  const [email, setEmail]         = useState("");
  const [telephone, setTelephone] = useState("");
  const [ville, setVille]         = useState("");
  const [titre, setTitre]         = useState("");

  // ── Section 2 : Compétences ──
  const [hardSkillInput, setHardSkillInput] = useState("");
  const [softSkillInput, setSoftSkillInput] = useState("");
  const [hardSkills, setHardSkills]         = useState([]);
  const [softSkills, setSoftSkills]         = useState([]);

  // ── Section 3 : Expériences ──
  const [experiences, setExperiences] = useState([
    { poste: "", entreprise: "", debut: "", fin: "", description: "" }
  ]);

  // ── Section 4 : Formations ──
  const [formations, setFormations] = useState([
    { diplome: "", etablissement: "", annee: "", domaine: "" }
  ]);

  const [erreur, setErreur]   = useState("");
  const [loading, setLoading] = useState(false);

  // ── Ajouter un tag skill ──
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

  const supprimerHardSkill = (skill) =>
    setHardSkills(hardSkills.filter((s) => s !== skill));

  const supprimerSoftSkill = (skill) =>
    setSoftSkills(softSkills.filter((s) => s !== skill));

  // ── Gérer les expériences ──
  const modifierExperience = (index, champ, valeur) => {
    const copie = [...experiences];
    copie[index][champ] = valeur;
    setExperiences(copie);
  };

  const ajouterExperience = () =>
    setExperiences([...experiences,
      { poste: "", entreprise: "", debut: "", fin: "", description: "" }
    ]);

  const supprimerExperience = (index) =>
    setExperiences(experiences.filter((_, i) => i !== index));

  // ── Gérer les formations ──
  const modifierFormation = (index, champ, valeur) => {
    const copie = [...formations];
    copie[index][champ] = valeur;
    setFormations(copie);
  };

  const ajouterFormation = () =>
    setFormations([...formations,
      { diplome: "", etablissement: "", annee: "", domaine: "" }
    ]);

  const supprimerFormation = (index) =>
    setFormations(formations.filter((_, i) => i !== index));

  // ── Soumettre le formulaire ──
 const handleSubmit = async () => {
  setErreur("");

  if (!nom || !email || !titre) {
    setErreur("Veuillez remplir au minimum : nom, email et titre.");
    return;
  }
  if (hardSkills.length === 0) {
    setErreur("Ajoutez au moins une compétence technique.");
    return;
  }

  // ── MODE TEST (sans backend) ──
  navigate("/dashboard");

  // ── MODE PRODUCTION (décommenter quand Hanane finit le backend) ──
  // setLoading(true);
  // try {
  //   await API.post("/profile/cv/", {
  //     personal_info: { nom, email, telephone, ville, titre },
  //     hard_skills: hardSkills,
  //     soft_skills: softSkills,
  //     experiences,
  //     formations,
  //   });
  //   navigate("/dashboard");
  // } catch (error) {
  //   setErreur("Erreur lors de l'enregistrement. Réessayez.");
  // } finally {
  //   setLoading(false);
  // }
};

  return (
    <div style={styles.page}>
      <div style={styles.container}>

        <h1 style={styles.titre}>Mon Profil CV</h1>
        <p style={styles.sousTitre}>
          Remplissez vos informations pour trouver les offres qui vous correspondent
        </p>

        {erreur && <p style={styles.erreur}>{erreur}</p>}

        {/* ───────── SECTION 1 ───────── */}
        <div style={styles.section}>
          <h2 style={styles.sectionTitre}>1. Informations personnelles</h2>

          <div style={styles.grille2}>
            <div style={styles.groupe}>
              <label style={styles.label}>Nom complet *</label>
              <input style={styles.input} value={nom}
                onChange={(e) => setNom(e.target.value)}
                placeholder="Rachid Alami" />
            </div>
            <div style={styles.groupe}>
              <label style={styles.label}>Email *</label>
              <input style={styles.input} type="email" value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="rachid@email.com" />
            </div>
            <div style={styles.groupe}>
              <label style={styles.label}>Téléphone</label>
              <input style={styles.input} value={telephone}
                onChange={(e) => setTelephone(e.target.value)}
                placeholder="+212 6XX XXX XXX" />
            </div>
            <div style={styles.groupe}>
              <label style={styles.label}>Ville</label>
              <input style={styles.input} value={ville}
                onChange={(e) => setVille(e.target.value)}
                placeholder="Casablanca" />
            </div>
          </div>

          <div style={styles.groupe}>
            <label style={styles.label}>Titre du poste recherché *</label>
            <input style={styles.input} value={titre}
              onChange={(e) => setTitre(e.target.value)}
              placeholder="Développeur Frontend React" />
          </div>
        </div>

        {/* ───────── SECTION 2 ───────── */}
        <div style={styles.section}>
          <h2 style={styles.sectionTitre}>2. Compétences</h2>

          {/* Hard Skills */}
          <div style={styles.groupe}>
            <label style={styles.label}>Compétences techniques (Hard Skills)</label>
            <div style={styles.tagInput}>
              <input
                style={{ ...styles.input, flex: 1, marginBottom: 0 }}
                value={hardSkillInput}
                onChange={(e) => setHardSkillInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && ajouterHardSkill()}
                placeholder="ex: React, Python, SQL... puis Entrée"
              />
              <button onClick={ajouterHardSkill} style={styles.boutonAjouter}>
                Ajouter
              </button>
            </div>
            <div style={styles.tags}>
              {hardSkills.map((s) => (
                <span key={s} style={styles.tagViolet}>
                  {s}
                  <span onClick={() => supprimerHardSkill(s)} style={styles.x}>✕</span>
                </span>
              ))}
            </div>
          </div>

          {/* Soft Skills */}
          <div style={styles.groupe}>
            <label style={styles.label}>Compétences humaines (Soft Skills)</label>
            <div style={styles.tagInput}>
              <input
                style={{ ...styles.input, flex: 1, marginBottom: 0 }}
                value={softSkillInput}
                onChange={(e) => setSoftSkillInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && ajouterSoftSkill()}
                placeholder="ex: Communication, Travail en équipe..."
              />
              <button onClick={ajouterSoftSkill} style={styles.boutonAjouter}>
                Ajouter
              </button>
            </div>
            <div style={styles.tags}>
              {softSkills.map((s) => (
                <span key={s} style={styles.tagVert}>
                  {s}
                  <span onClick={() => supprimerSoftSkill(s)} style={styles.x}>✕</span>
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* ───────── SECTION 3 ───────── */}
        <div style={styles.section}>
          <h2 style={styles.sectionTitre}>3. Expériences professionnelles</h2>

          {experiences.map((exp, index) => (
            <div key={index} style={styles.carteItem}>
              <div style={styles.carteHeader}>
                <span style={styles.carteNumero}>Expérience {index + 1}</span>
                {experiences.length > 1 && (
                  <button onClick={() => supprimerExperience(index)}
                    style={styles.boutonSupprimer}>
                    Supprimer
                  </button>
                )}
              </div>
              <div style={styles.grille2}>
                <div style={styles.groupe}>
                  <label style={styles.label}>Poste occupé</label>
                  <input style={styles.input} value={exp.poste}
                    onChange={(e) => modifierExperience(index, "poste", e.target.value)}
                    placeholder="Développeur Frontend" />
                </div>
                <div style={styles.groupe}>
                  <label style={styles.label}>Entreprise</label>
                  <input style={styles.input} value={exp.entreprise}
                    onChange={(e) => modifierExperience(index, "entreprise", e.target.value)}
                    placeholder="TechMaroc" />
                </div>
                <div style={styles.groupe}>
                  <label style={styles.label}>Date début</label>
                  <input style={styles.input} type="month" value={exp.debut}
                    onChange={(e) => modifierExperience(index, "debut", e.target.value)} />
                </div>
                <div style={styles.groupe}>
                  <label style={styles.label}>Date fin</label>
                  <input style={styles.input} type="month" value={exp.fin}
                    onChange={(e) => modifierExperience(index, "fin", e.target.value)} />
                </div>
              </div>
              <div style={styles.groupe}>
                <label style={styles.label}>Description des tâches</label>
                <textarea style={styles.textarea} value={exp.description}
                  onChange={(e) => modifierExperience(index, "description", e.target.value)}
                  placeholder="Décrivez vos responsabilités et réalisations..."
                  rows={3} />
              </div>
            </div>
          ))}

          <button onClick={ajouterExperience} style={styles.boutonSecondaire}>
            + Ajouter une expérience
          </button>
        </div>

        {/* ───────── SECTION 4 ───────── */}
        <div style={styles.section}>
          <h2 style={styles.sectionTitre}>4. Formations</h2>

          {formations.map((form, index) => (
            <div key={index} style={styles.carteItem}>
              <div style={styles.carteHeader}>
                <span style={styles.carteNumero}>Formation {index + 1}</span>
                {formations.length > 1 && (
                  <button onClick={() => supprimerFormation(index)}
                    style={styles.boutonSupprimer}>
                    Supprimer
                  </button>
                )}
              </div>
              <div style={styles.grille2}>
                <div style={styles.groupe}>
                  <label style={styles.label}>Diplôme</label>
                  <input style={styles.input} value={form.diplome}
                    onChange={(e) => modifierFormation(index, "diplome", e.target.value)}
                    placeholder="Licence IASD" />
                </div>
                <div style={styles.groupe}>
                  <label style={styles.label}>Établissement</label>
                  <input style={styles.input} value={form.etablissement}
                    onChange={(e) => modifierFormation(index, "etablissement", e.target.value)}
                    placeholder="FSS Marrakech" />
                </div>
                <div style={styles.groupe}>
                  <label style={styles.label}>Année d'obtention</label>
                  <input style={styles.input} type="number"
                    min="1990" max="2030" value={form.annee}
                    onChange={(e) => modifierFormation(index, "annee", e.target.value)}
                    placeholder="2026" />
                </div>
                <div style={styles.groupe}>
                  <label style={styles.label}>Domaine d'étude</label>
                  <input style={styles.input} value={form.domaine}
                    onChange={(e) => modifierFormation(index, "domaine", e.target.value)}
                    placeholder="Informatique / IA" />
                </div>
              </div>
            </div>
          ))}

          <button onClick={ajouterFormation} style={styles.boutonSecondaire}>
            + Ajouter une formation
          </button>
        </div>

        {/* ───────── BOUTON FINAL ───────── */}
        <button
          onClick={handleSubmit}
          style={{ ...styles.boutonPrincipal, opacity: loading ? 0.7 : 1 }}
          disabled={loading}
        >
          {loading ? "Enregistrement..." : "Enregistrer et continuer →"}
        </button>

      </div>
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    backgroundColor: "#f5f5f5",
    padding: "2rem 1rem",
  },
  container: {
    maxWidth: "700px",
    margin: "0 auto",
  },
  titre: {
    fontSize: "26px",
    fontWeight: "500",
    marginBottom: "6px",
  },
  sousTitre: {
    fontSize: "14px",
    color: "#888",
    marginBottom: "28px",
  },
  section: {
    backgroundColor: "white",
    borderRadius: "12px",
    border: "0.5px solid #ddd",
    padding: "1.5rem",
    marginBottom: "20px",
  },
  sectionTitre: {
    fontSize: "16px",
    fontWeight: "500",
    marginBottom: "16px",
    color: "#534AB7",
    borderBottom: "1px solid #EEEDFE",
    paddingBottom: "8px",
  },
  grille2: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "12px",
  },
  groupe: {
    marginBottom: "14px",
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
  textarea: {
    width: "100%",
    padding: "10px",
    borderRadius: "8px",
    border: "1px solid #ddd",
    fontSize: "14px",
    boxSizing: "border-box",
    resize: "vertical",
    fontFamily: "inherit",
  },
  tagInput: {
    display: "flex",
    gap: "8px",
    alignItems: "center",
  },
  tags: {
    display: "flex",
    flexWrap: "wrap",
    gap: "8px",
    marginTop: "10px",
  },
  tagViolet: {
    backgroundColor: "#EEEDFE",
    color: "#534AB7",
    padding: "4px 10px",
    borderRadius: "20px",
    fontSize: "13px",
    display: "flex",
    alignItems: "center",
    gap: "6px",
  },
  tagVert: {
    backgroundColor: "#E1F5EE",
    color: "#0F6E56",
    padding: "4px 10px",
    borderRadius: "20px",
    fontSize: "13px",
    display: "flex",
    alignItems: "center",
    gap: "6px",
  },
  x: {
    cursor: "pointer",
    fontSize: "11px",
    opacity: 0.7,
  },
  carteItem: {
    border: "1px solid #eee",
    borderRadius: "8px",
    padding: "1rem",
    marginBottom: "12px",
    backgroundColor: "#fafafa",
  },
  carteHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "12px",
  },
  carteNumero: {
    fontSize: "13px",
    fontWeight: "500",
    color: "#666",
  },
  boutonAjouter: {
    padding: "10px 16px",
    backgroundColor: "#534AB7",
    color: "white",
    border: "none",
    borderRadius: "8px",
    fontSize: "13px",
    cursor: "pointer",
    whiteSpace: "nowrap",
  },
  boutonSecondaire: {
    padding: "10px 16px",
    backgroundColor: "white",
    color: "#534AB7",
    border: "1px solid #534AB7",
    borderRadius: "8px",
    fontSize: "13px",
    cursor: "pointer",
    marginTop: "4px",
  },
  boutonSupprimer: {
    padding: "4px 10px",
    backgroundColor: "#FCEBEB",
    color: "#A32D2D",
    border: "none",
    borderRadius: "6px",
    fontSize: "12px",
    cursor: "pointer",
  },
  boutonPrincipal: {
    width: "100%",
    padding: "14px",
    backgroundColor: "#534AB7",
    color: "white",
    border: "none",
    borderRadius: "8px",
    fontSize: "16px",
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
};

export default CVFormPage;