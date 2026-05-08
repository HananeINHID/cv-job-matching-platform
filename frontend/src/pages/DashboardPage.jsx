import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Briefcase, Search, ArrowRight, Zap, Users,
  GraduationCap, Edit2, Database, Globe, RefreshCw,
  TrendingUp, Star, Clock, CheckCircle2
} from "lucide-react";
import API, { getHistory } from "../services/api";
import AppShell from "../components/AppShell";
import { Card, CardHeader, CardBody } from "../components/ui/Card";
import { Badge } from "../components/ui/Badge";
import { SkeletonKPI } from "../components/ui/Skeleton";
import { EmptyHistory } from "../components/ui/EmptyState";
import { Button } from "../components/ui/Button";
import toast from "react-hot-toast";
const SOURCES = [
  { value: "dataset",       label: "Dataset local",  icon: Database },
  { value: "rekrute",       label: "Rekrute",        icon: Globe },
  { value: "emploima",      label: "Emploi.ma",      icon: Globe },
  { value: "marocannonces", label: "MarocAnnonces",  icon: Globe },
  { value: "linkedin",      label: "LinkedIn",       icon: Globe },
];

/** Calcule un score de complétude de profil (0-100) */
function calculerCompletion(profil) {
  if (!profil) return 0;
  const items = [
    { done: !!profil.personal_info?.nom,      label: "Nom" },
    { done: !!profil.personal_info?.email,    label: "Email" },
    { done: !!profil.personal_info?.titre,    label: "Titre" },
    { done: !!profil.personal_info?.ville,    label: "Ville" },
    { done: (profil.hard_skills_list?.length || profil.hard_skills?.length || 0) > 0, label: "Compétences" },
    { done: (profil.experiences?.length || 0) > 0, label: "Expériences" },
    { done: (profil.formations?.length || 0)  > 0, label: "Formations" },
  ];
  const done = items.filter(i => i.done).length;
  return { score: Math.round((done / items.length) * 100), items };
}

/** Extrait le prénom du token JWT ou localStorage */
function getPrenom() {
  const saved = localStorage.getItem("userNom");
  if (saved) return saved.split(" ")[0];
  const token = localStorage.getItem("token");
  if (!token) return "Utilisateur";
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return (payload.username || "Utilisateur").split(" ")[0];
  } catch { return "Utilisateur"; }
}

// ──────────────────────────────────────────────────────────────────────────────

function DashboardPage() {
  const navigate = useNavigate();
  const [profil, setProfil] = useState(null);
  const [loading, setLoading] = useState(true);
  const [historique, setHistorique] = useState([]);
  const [recherche, setRecherche] = useState("");
  const [source, setSource] = useState("dataset");
  const [location, setLocation] = useState("Morocco");

  // Chargement profil + historique
  useEffect(() => {
    const charger = async () => {
      const token = localStorage.getItem("token");
      if (!token) { setLoading(false); return; }

      try {
        const response = await API.get("/profile/");
        const data = response.data;
        if (data?.personal_info?.nom) {
          localStorage.setItem("userNom", data.personal_info.nom);
        }
        setProfil({
          ...data,
          hard_skills_list: Array.isArray(data.hard_skills_list) ? data.hard_skills_list
                           : Array.isArray(data.hard_skills) ? data.hard_skills : [],
          soft_skills_list: Array.isArray(data.soft_skills_list) ? data.soft_skills_list
                           : Array.isArray(data.soft_skills) ? data.soft_skills : [],
        });
      } catch {
        // Backend non disponible — mode silencieux
      }

      try {
        const hist = await getHistory();
        const histData = hist.data?.history || hist.data;
        setHistorique(Array.isArray(histData) ? histData : []);
      } catch {
        setHistorique([]);
      }

      setLoading(false);
    };
    charger();
  }, []);

  // Lancer une recherche
  const lancerRecherche = () => {
    if (!recherche.trim()) {
      toast.error("Veuillez saisir un mot-clé.");
      return;
    }
    navigate("/results", { state: { recherche, source, locationParam: location } });
  };

  // Données dérivées
  const hardSkills = profil?.hard_skills_list || profil?.hard_skills || [];
  const softSkills = profil?.soft_skills_list || profil?.soft_skills || [];
  const nbExperiences = profil?.experiences?.length || 0;
  const nbFormations  = profil?.formations?.length || 0;

  // Meilleur score historique
  const meilleurScore = historique.length > 0
    ? Math.max(...historique.map(h => h.best_score || 0), 0)
    : 0;

  // Dernière recherche
  const derniereRecherche = historique[0]?.keyword || historique[0]?.query || null;

  // Completion
  const { score: completionScore, items: completionItems } = calculerCompletion(profil);

  // KPIs
  const kpis = [
    {
      label: "Offres matchées",
      value: historique.reduce((s, h) => s + (h.nb_results || 0), 0) || "—",
      icon: <Briefcase size={20} />,
      color: "var(--color-primary)",
      bg: "rgba(37, 99, 235, 0.1)",
    },
    {
      label: "Meilleur score",
      value: meilleurScore > 0 ? `${meilleurScore}%` : "—",
      icon: <Star size={20} />,
      color: "var(--color-warning)",
      bg: "rgba(245, 158, 11, 0.1)",
    },
    {
      label: "Compétences",
      value: hardSkills.length + softSkills.length,
      icon: <Zap size={20} />,
      color: "var(--color-success)",
      bg: "rgba(16, 185, 129, 0.1)",
    },
    {
      label: "Dernière recherche",
      value: derniereRecherche ? `« ${derniereRecherche} »` : "—",
      icon: <Clock size={20} />,
      color: "#8B5CF6",
      bg: "rgba(139, 92, 246, 0.1)",
      small: true,
    },
  ];

  return (
    <AppShell title={`Bonjour ${getPrenom()} 👋`} breadcrumb="Accueil / Dashboard">
      {/* ── KPI Cards ────────────────────────────── */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
        gap: "16px",
        marginBottom: "24px",
      }}>
        {loading
          ? [1,2,3,4].map(i => <SkeletonKPI key={i} />)
          : kpis.map(({ label, value, icon, color, bg, small }) => (
            <Card key={label} style={{ padding: "1.25rem" }}>
              <div style={{
                width: "40px", height: "40px",
                borderRadius: "var(--radius-md)",
                backgroundColor: bg,
                display: "flex", alignItems: "center", justifyContent: "center",
                color, marginBottom: "12px",
              }}>
                {icon}
              </div>
              <p style={{ margin: "0 0 4px", fontSize: "12px", color: "var(--text-muted)", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.5px" }}>
                {label}
              </p>
              <p style={{
                margin: 0, fontSize: small ? "15px" : "26px",
                fontWeight: 700, color: "var(--text-main)",
                overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap",
              }}>
                {value}
              </p>
            </Card>
          ))
        }
      </div>

      {/* ── Grid : Recherche + Completion ────────── */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "1fr 340px",
        gap: "20px",
        marginBottom: "20px",
      }}
        className="dashboard-grid"
      >
        <style>{`
          @media (max-width: 1024px) {
            .dashboard-grid { grid-template-columns: 1fr !important; }
          }
        `}</style>

        {/* ── Bloc de recherche ── */}
        <Card>
          <CardHeader
            title="Trouver des offres"
            subtitle="Lancez une recherche par mot-clé"
            icon={<Search size={18} />}
          />
          <CardBody>
            {/* Input + bouton */}
            <div style={{ display: "flex", gap: "10px", marginBottom: "16px" }}>
              <input
                value={recherche}
                onChange={e => setRecherche(e.target.value)}
                onKeyDown={e => e.key === "Enter" && lancerRecherche()}
                placeholder="Ex: Développeur React, Data Scientist..."
                style={{
                  flex: 1, padding: "12px 16px",
                  borderRadius: "var(--radius-md)",
                  border: "1.5px solid var(--border-color)",
                  backgroundColor: "var(--bg-main)",
                  color: "var(--text-main)",
                  fontSize: "14px", outline: "none",
                  fontFamily: "inherit",
                  transition: "border-color 0.2s",
                }}
                onFocus={e => e.target.style.borderColor = "var(--color-primary)"}
                onBlur={e => e.target.style.borderColor = "var(--border-color)"}
              />
              <Button variant="primary" onClick={lancerRecherche} icon={<ArrowRight size={16} />}>
                Lancer
              </Button>
            </div>

            {/* Sélecteur source */}
            <div style={{ marginBottom: "8px" }}>
              <p style={{ fontSize: "12px", fontWeight: 600, color: "var(--text-muted)", marginBottom: "8px", textTransform: "uppercase", letterSpacing: "0.5px" }}>
                Source
              </p>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
                {SOURCES.map(({ value, label, icon: Icon }) => (
                  <button
                    key={value}
                    onClick={() => setSource(value)}
                    style={{
                      display: "flex", alignItems: "center", gap: "6px",
                      padding: "6px 14px", borderRadius: "var(--radius-full)",
                      fontSize: "12px", fontWeight: 600,
                      cursor: "pointer", fontFamily: "inherit",
                      transition: "all 0.2s",
                      border: source === value
                        ? "1.5px solid var(--color-primary)"
                        : "1.5px solid var(--border-color)",
                      backgroundColor: source === value
                        ? "var(--color-primary-light)"
                        : "transparent",
                      color: source === value
                        ? "var(--color-primary)"
                        : "var(--text-muted)",
                    }}
                  >
                    <Icon size={13} />
                    {label}
                  </button>
                ))}
              </div>
            </div>

            {/* Champ localisation LinkedIn */}
            {source === "linkedin" && (
              <div style={{ marginTop: "12px", display: "flex", alignItems: "center", gap: "10px" }}>
                <span style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-muted)", whiteSpace: "nowrap" }}>
                  📍 Localisation :
                </span>
                <input
                  value={location}
                  onChange={e => setLocation(e.target.value)}
                  placeholder="Ex: Morocco, Casablanca..."
                  style={{
                    flex: 1, padding: "10px 14px",
                    borderRadius: "var(--radius-md)",
                    border: "1.5px solid var(--border-color)",
                    backgroundColor: "var(--bg-main)",
                    color: "var(--text-main)",
                    fontSize: "13px", outline: "none", fontFamily: "inherit",
                  }}
                />
              </div>
            )}

            {/* Avertissement scraping temps-réel */}
            {source !== "dataset" && (
              <div style={{
                marginTop: "12px", padding: "10px 14px",
                borderRadius: "var(--radius-md)",
                backgroundColor: "rgba(245, 158, 11, 0.08)",
                border: "1px solid rgba(245, 158, 11, 0.3)",
                fontSize: "12px", color: "var(--color-warning)",
                display: "flex", alignItems: "center", gap: "8px",
              }}>
                ⚡ Source temps-réel — le navigateur s'ouvrira en arrière-plan (~30–60 s).
              </div>
            )}
          </CardBody>
        </Card>

        {/* ── Completion du profil ── */}
        <Card>
          <CardHeader
            title="Profil complété"
            subtitle={`${completionScore}% des informations renseignées`}
            icon={<TrendingUp size={18} />}
            action={
              <Button variant="ghost" size="sm" onClick={() => navigate("/cv-form")} icon={<Edit2 size={13} />}>
                Modifier
              </Button>
            }
          />
          <CardBody>
            {/* Barre de progression */}
            <div style={{ marginBottom: "16px" }}>
              <div style={{
                height: "8px", borderRadius: "var(--radius-full)",
                backgroundColor: "var(--color-neutral-200)",
                overflow: "hidden",
              }}>
                <div style={{
                  height: "100%",
                  width: `${completionScore}%`,
                  borderRadius: "var(--radius-full)",
                  background: completionScore >= 80
                    ? "var(--color-success)"
                    : completionScore >= 50
                    ? "var(--color-warning)"
                    : "var(--color-danger)",
                  transition: "width 0.8s ease",
                }} />
              </div>
            </div>

            {/* Checklist */}
            <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
              {loading
                ? [1,2,3,4,5].map(i => (
                  <div key={i} style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <div style={{ width: 16, height: 16, borderRadius: "50%", backgroundColor: "var(--color-neutral-200)" }} />
                    <div style={{ height: "12px", backgroundColor: "var(--color-neutral-200)", borderRadius: "4px", flex: 1 }} />
                  </div>
                ))
                : (completionItems || []).map(({ label, done }) => (
                  <div key={label} style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <CheckCircle2
                      size={16}
                      color={done ? "var(--color-success)" : "var(--color-neutral-300)"}
                      fill={done ? "rgba(16, 185, 129, 0.15)" : "transparent"}
                    />
                    <span style={{
                      fontSize: "13px",
                      color: done ? "var(--text-main)" : "var(--text-muted)",
                      fontWeight: done ? 500 : 400,
                    }}>
                      {label}
                    </span>
                    {!done && (
                      <Badge variant="warning" size="sm">Manquant</Badge>
                    )}
                  </div>
                ))
              }
            </div>
          </CardBody>
        </Card>
      </div>

      {/* ── Profil : Compétences + Expériences ─── */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "1fr 1fr",
        gap: "20px",
        marginBottom: "20px",
      }}
        className="profile-grid"
      >
        <style>{`
          @media (max-width: 768px) {
            .profile-grid { grid-template-columns: 1fr !important; }
          }
        `}</style>

        {/* Compétences */}
        <Card>
          <CardHeader title="Compétences" icon={<Zap size={18} />} />
          <CardBody>
            {loading ? (
              <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
                {[80, 100, 70, 90, 60, 110].map(w => (
                  <div key={w} style={{ height: "28px", width: `${w}px`, borderRadius: "var(--radius-full)", backgroundColor: "var(--color-neutral-200)" }} />
                ))}
              </div>
            ) : (
              <>
                <p style={{ fontSize: "11px", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: "8px" }}>
                  Hard Skills
                </p>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "6px", marginBottom: "16px" }}>
                  {hardSkills.length > 0
                    ? hardSkills.map(s => <Badge key={s} variant="info">{s}</Badge>)
                    : <span style={{ fontSize: "13px", color: "var(--text-muted)" }}>Aucune compétence ajoutée</span>
                  }
                </div>
                <p style={{ fontSize: "11px", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: "8px" }}>
                  Soft Skills
                </p>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                  {softSkills.length > 0
                    ? softSkills.map(s => <Badge key={s} variant="neutral">{s}</Badge>)
                    : <span style={{ fontSize: "13px", color: "var(--text-muted)" }}>Aucun soft skill ajouté</span>
                  }
                </div>
              </>
            )}
          </CardBody>
        </Card>

        {/* Expériences & Formations */}
        <Card>
          <CardHeader title="Parcours" icon={<Briefcase size={18} />} />
          <CardBody>
            <p style={{ fontSize: "11px", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: "10px" }}>
              Expériences ({nbExperiences})
            </p>
            {nbExperiences > 0
              ? profil.experiences.slice(0, 3).map((exp, i) => (
                <div key={i} style={{
                  borderLeft: "3px solid var(--color-primary)",
                  paddingLeft: "12px", marginBottom: "12px",
                }}>
                  <p style={{ margin: 0, fontSize: "13px", fontWeight: 600, color: "var(--text-main)" }}>{exp.poste || "—"}</p>
                  <p style={{ margin: "2px 0 0", fontSize: "12px", color: "var(--text-muted)" }}>{exp.entreprise || "—"}</p>
                </div>
              ))
              : <p style={{ fontSize: "13px", color: "var(--text-muted)", marginBottom: "16px" }}>Aucune expérience</p>
            }

            <p style={{ fontSize: "11px", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: "10px", marginTop: "16px" }}>
              Formations ({nbFormations})
            </p>
            {nbFormations > 0
              ? profil.formations.slice(0, 2).map((form, i) => (
                <div key={i} style={{
                  borderLeft: "3px solid var(--color-success)",
                  paddingLeft: "12px", marginBottom: "12px",
                }}>
                  <p style={{ margin: 0, fontSize: "13px", fontWeight: 600, color: "var(--text-main)" }}>{form.diplome || "—"}</p>
                  <p style={{ margin: "2px 0 0", fontSize: "12px", color: "var(--text-muted)" }}>{form.etablissement || "—"}</p>
                </div>
              ))
              : <p style={{ fontSize: "13px", color: "var(--text-muted)" }}>Aucune formation</p>
            }
          </CardBody>
        </Card>
      </div>

      {/* ── Historique des recherches ─────────────── */}
      <Card>
        <CardHeader
          title="Recherches récentes"
          icon={<Clock size={18} />}
        />
        <CardBody style={{ padding: historique.length === 0 ? 0 : "1.5rem" }}>
          {loading ? (
            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              {[1,2,3].map(i => (
                <div key={i} style={{ height: "56px", borderRadius: "var(--radius-md)", backgroundColor: "var(--color-neutral-100)" }} />
              ))}
            </div>
          ) : historique.length === 0 ? (
            <EmptyHistory />
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
              {historique.slice(0, 6).map((item, i) => {
                const srcLabel = SOURCES.find(s => s.value === item.source)?.label || item.source || "—";
                const date = item.searched_at
                  ? new Date(item.searched_at).toLocaleDateString("fr-FR", {
                      day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit",
                    })
                  : null;
                return (
                  <div key={i} style={{
                    display: "flex", alignItems: "center",
                    justifyContent: "space-between",
                    padding: "12px 14px",
                    borderRadius: "var(--radius-md)",
                    backgroundColor: "var(--bg-main)",
                    border: "1px solid var(--border-color)",
                    transition: "border-color 0.2s",
                    cursor: "default",
                  }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                      <Search size={15} color="var(--text-muted)" />
                      <div>
                        <p style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-main)", margin: 0 }}>
                          {item.keyword || item.query || "—"}
                        </p>
                        <p style={{ fontSize: "11px", color: "var(--text-muted)", margin: "2px 0 0" }}>
                          {srcLabel}{date ? ` · ${date}` : ""}
                        </p>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      icon={<RefreshCw size={12} />}
                      onClick={() => navigate("/results", {
                        state: { recherche: item.keyword || item.query, source: item.source || "dataset" }
                      })}
                    >
                      Relancer
                    </Button>
                  </div>
                );
              })}
            </div>
          )}
        </CardBody>
      </Card>
    </AppShell>
  );
}

export default DashboardPage;