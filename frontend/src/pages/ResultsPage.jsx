import { useState, useEffect, useCallback } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Briefcase, List, BarChart2, PieChart, ExternalLink, Filter, ChevronLeft, ChevronRight } from "lucide-react";
import { Chart as ChartJS, RadialLinearScale, PointElement, LineElement, Filler, CategoryScale, LinearScale, BarElement, ScatterController, Tooltip, Legend } from "chart.js";
import { Radar, Bar, Scatter } from "react-chartjs-2";
import API, { getRadar, getWordcloud, getScoreDistribution, getClusters } from "../services/api";
import AppShell from "../components/AppShell";
import { Card, CardHeader, CardBody } from "../components/ui/Card";
import { ScoreBadge, Badge } from "../components/ui/Badge";
import { SkeletonCard } from "../components/ui/Skeleton";
import { EmptyOffers } from "../components/ui/EmptyState";
import { Button } from "../components/ui/Button";
import { PageLoader } from "../components/ui/Spinner";

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, CategoryScale, LinearScale, BarElement, ScatterController, Tooltip, Legend);

const MOCK_OFFRES = [
  { id: 1, titre: "Développeur React Frontend", entreprise: "Capgemini Maroc", ville: "Casablanca", contrat: "CDI", score: 87, competences: ["React", "JavaScript", "CSS", "Git"] },
  { id: 2, titre: "Frontend Engineer", entreprise: "OCP Digital", ville: "Rabat", contrat: "CDI", score: 74, competences: ["React", "TypeScript", "REST API"] },
  { id: 3, titre: "Développeur Full Stack", entreprise: "StartupTech", ville: "Casablanca", contrat: "CDD", score: 65, competences: ["React", "Node.js", "MongoDB"] },
  { id: 4, titre: "UI Developer", entreprise: "Sofrecom", ville: "Casablanca", contrat: "Stage", score: 58, competences: ["HTML", "CSS", "JavaScript"] },
  { id: 5, titre: "Web Developer", entreprise: "Maroc Telecom", ville: "Rabat", contrat: "CDI", score: 45, competences: ["Vue.js", "PHP", "MySQL"] },
];

const MOCK_RADAR = {
  labels: ["React", "JavaScript", "CSS", "Python", "SQL", "Git"],
  datasets: [
    { label: "Votre profil", data: [90, 80, 75, 60, 50, 70], backgroundColor: "rgba(37,99,235,0.15)", borderColor: "var(--color-primary)", borderWidth: 2, pointBackgroundColor: "var(--color-primary)" },
    { label: "Offre sélectionnée", data: [95, 90, 70, 30, 40, 80], backgroundColor: "rgba(245,158,11,0.12)", borderColor: "var(--color-warning)", borderWidth: 2, pointBackgroundColor: "var(--color-warning)" },
  ],
};

const MOCK_COMPETENCES = {
  labels: ["React", "JavaScript", "Python", "Django", "SQL", "Node.js", "CSS", "Git"],
  datasets: [{ label: "Fréquence", data: [95, 88, 75, 70, 65, 60, 58, 55], backgroundColor: "var(--color-primary)", borderRadius: 6 }],
};

const MOCK_DISTRIBUTION = {
  labels: ["0-25", "25-50", "50-75", "75-100"],
  datasets: [{ label: "Nombre d'offres", data: [5, 18, 32, 12], backgroundColor: ["#EF4444", "#F59E0B", "#2563EB", "#10B981"], borderRadius: 6 }],
};

const MOCK_CLUSTERS = {
  datasets: [
    { label: "Frontend", data: [{ x: 20, y: 80 }, { x: 25, y: 75 }], backgroundColor: "#2563EB", pointRadius: 10 },
    { label: "Data", data: [{ x: 70, y: 40 }, { x: 75, y: 35 }], backgroundColor: "#F59E0B", pointRadius: 10 },
    { label: "Fullstack", data: [{ x: 50, y: 60 }, { x: 55, y: 55 }], backgroundColor: "#10B981", pointRadius: 10 },
  ],
};

const CLUSTER_COLORS = ["#2563EB", "#F59E0B", "#10B981", "#8B5CF6", "#EF4444", "#06B6D4"];

function normaliserClusters(raw) {
  if (!Array.isArray(raw) || raw.length === 0) return null;
  if (raw[0]?.points !== undefined) {
    return { datasets: raw.map((cl, i) => ({ label: cl.label || `Cluster ${i}`, data: cl.points, backgroundColor: CLUSTER_COLORS[i % CLUSTER_COLORS.length], pointRadius: 10 })) };
  }
  const groupes = {};
  raw.forEach(pt => {
    const key = pt.cluster ?? 0;
    if (!groupes[key]) groupes[key] = { label: pt.cluster_label || `Cluster ${key}`, points: [] };
    groupes[key].points.push({ x: pt.x, y: pt.y });
  });
  return { datasets: Object.values(groupes).map((g, i) => ({ label: g.label, data: g.points, backgroundColor: CLUSTER_COLORS[i % CLUSTER_COLORS.length], pointRadius: 10 })) };
}

const ITEMS_PER_PAGE = 10;

function ResultsPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const recherche   = location.state?.recherche    || "";
  const source      = location.state?.source       || "dataset";
  const locationParam = location.state?.locationParam || "Morocco";

  const [offres, setOffres]         = useState([]);
  const [offreSelectionnee, setOffre] = useState(null);
  const [loading, setLoading]       = useState(true);
  const [onglet, setOnglet]         = useState("offres");
  const [radarData, setRadarData]   = useState(MOCK_RADAR);
  const [radarLoading, setRadarLoading] = useState(false);
  const [competences, setCompetences] = useState(MOCK_COMPETENCES);
  const [distribution, setDistribution] = useState(MOCK_DISTRIBUTION);
  const [clusters, setClusters]     = useState(MOCK_CLUSTERS);

  // Filtres
  const [minScore, setMinScore]     = useState(0);
  const [filterContrat, setFilterContrat] = useState("");
  const [filterVille, setFilterVille] = useState("");
  const [sortBy, setSortBy]         = useState("score");
  const [page, setPage]             = useState(1);

  // Chargement offres
  useEffect(() => {
    const charger = async () => {
      try {
        if (source !== "dataset") {
          const params = new URLSearchParams({ q: recherche, source });
          if (source === "linkedin") params.set("location", locationParam);
          await API.get(`/jobs/search/?${params.toString()}`);
        }
        const response = await API.get(`/matching/results/?q=${encodeURIComponent(recherche)}&source=${source}`);
        const list = Array.isArray(response.data) ? response.data : [];
        setOffres(list);
        if (list.length > 0) setOffre(list[0]);
      } catch {
        setOffres(MOCK_OFFRES);
        setOffre(MOCK_OFFRES[0]);
      } finally {
        setLoading(false);
      }
    };
    charger();
  }, []);

  // Stats graphiques
  useEffect(() => {
    getWordcloud().then(({ data }) => {
      if (Array.isArray(data) && data.length > 0) {
        const sorted = [...data].sort((a, b) => (b.value ?? b.count ?? 0) - (a.value ?? a.count ?? 0)).slice(0, 12);
        setCompetences({ labels: sorted.map(d => d.text || d.skill || "?"), datasets: [{ label: "Fréquence", data: sorted.map(d => d.value ?? d.count ?? 0), backgroundColor: "var(--color-primary)", borderRadius: 6 }] });
      }
    }).catch(() => {});
    getScoreDistribution().then(({ data }) => {
      if (data?.labels && data?.counts) setDistribution({ labels: data.labels, datasets: [{ label: "Nombre d'offres", data: data.counts, backgroundColor: ["#EF4444","#F59E0B","#2563EB","#10B981"], borderRadius: 6 }] });
    }).catch(() => {});
    getClusters().then(({ data }) => { const n = normaliserClusters(data); if (n) setClusters(n); }).catch(() => {});
  }, []);

  // Radar par offre
  const chargerRadar = useCallback(async (offre) => {
    if (!offre?.id || typeof offre.id !== "number") { setRadarData(MOCK_RADAR); return; }
    setRadarLoading(true);
    try {
      const { data } = await getRadar(offre.id);
      if (data?.labels && data?.cv && data?.offre) {
        setRadarData({ labels: data.labels, datasets: [
          { label: "Votre profil", data: data.cv, backgroundColor: "rgba(37,99,235,0.15)", borderColor: "#2563EB", borderWidth: 2, pointBackgroundColor: "#2563EB" },
          { label: "Offre sélectionnée", data: data.offre, backgroundColor: "rgba(245,158,11,0.12)", borderColor: "#F59E0B", borderWidth: 2, pointBackgroundColor: "#F59E0B" },
        ]});
      }
    } catch { setRadarData(MOCK_RADAR); }
    finally { setRadarLoading(false); }
  }, []);

  useEffect(() => { if (offreSelectionnee) chargerRadar(offreSelectionnee); }, [offreSelectionnee, chargerRadar]);

  // Filtrage + tri + pagination
  const offresFiltrees = offres
    .filter(o => o.score >= minScore)
    .filter(o => filterContrat ? o.contrat === filterContrat : true)
    .filter(o => filterVille   ? o.ville?.toLowerCase().includes(filterVille.toLowerCase()) : true)
    .sort((a, b) => sortBy === "score" ? b.score - a.score : sortBy === "ville" ? (a.ville||"").localeCompare(b.ville||"") : 0);

  const totalPages = Math.ceil(offresFiltrees.length / ITEMS_PER_PAGE);
  const offresPage = offresFiltrees.slice((page - 1) * ITEMS_PER_PAGE, page * ITEMS_PER_PAGE);

  const contrats = [...new Set(offres.map(o => o.contrat).filter(Boolean))];

  const chartOptions = (dm) => ({
    plugins: { legend: { labels: { color: "var(--text-main)" } } },
    scales: {
      x: { ticks: { color: "var(--text-muted)" }, grid: { color: "rgba(128,128,128,0.1)" } },
      y: { ticks: { color: "var(--text-muted)" }, grid: { color: "rgba(128,128,128,0.1)" } },
    },
  });

  const barScoresData = {
    labels: offres.slice(0, 15).map(o => o.entreprise || o.titre?.substring(0, 20)),
    datasets: [{ label: "Score (%)", data: offres.slice(0, 15).map(o => o.score), backgroundColor: offres.slice(0, 15).map(o => o.score >= 70 ? "#10B981" : o.score >= 40 ? "#F59E0B" : "#EF4444"), borderRadius: 8 }],
  };

  if (loading) return (
    <PageLoader message={source !== "dataset" ? `⏳ Scraping ${source} en cours… (~30–60 s)` : "⏳ Analyse en cours…"} />
  );

  return (
    <AppShell
      title={`Résultats${recherche ? ` — « ${recherche} »` : ""}`}
      breadcrumb={`Dashboard / Résultats`}
    >
      {/* Onglets */}
      <div style={{ display: "flex", gap: "8px", marginBottom: "24px", flexWrap: "wrap" }}>
        {[
          { id: "offres",     label: "Offres",      icon: <List size={15} /> },
          { id: "graphiques", label: "Graphiques",  icon: <BarChart2 size={15} /> },
          { id: "clusters",   label: "Clusters",    icon: <PieChart size={15} /> },
        ].map(({ id, label, icon }) => (
          <Button
            key={id}
            variant={onglet === id ? "primary" : "ghost"}
            size="sm"
            icon={icon}
            onClick={() => setOnglet(id)}
          >
            {label}
          </Button>
        ))}
        <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: "8px" }}>
          <Badge variant={offres.length > 0 ? "info" : "neutral"}>
            {offresFiltrees.length} offre{offresFiltrees.length > 1 ? "s" : ""}
          </Badge>
          <Badge variant="neutral">Source : {source}</Badge>
        </div>
      </div>

      {/* ── ONGLET OFFRES ── */}
      {onglet === "offres" && (
        <>
          {/* Barre de filtres */}
          <Card style={{ marginBottom: "20px" }}>
            <CardBody style={{ padding: "1rem 1.5rem" }}>
              <div style={{ display: "flex", gap: "12px", flexWrap: "wrap", alignItems: "center" }}>
                <Filter size={16} color="var(--text-muted)" />

                {/* Slider score min */}
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <label style={{ fontSize: "12px", fontWeight: 600, color: "var(--text-muted)", whiteSpace: "nowrap" }}>
                    Score min : <strong style={{ color: "var(--color-primary)" }}>{minScore}%</strong>
                  </label>
                  <input type="range" min={0} max={100} value={minScore}
                    onChange={e => { setMinScore(Number(e.target.value)); setPage(1); }}
                    style={{ width: "100px", accentColor: "var(--color-primary)" }}
                  />
                </div>

                {/* Filtre contrat */}
                <select
                  value={filterContrat}
                  onChange={e => { setFilterContrat(e.target.value); setPage(1); }}
                  style={{ padding: "6px 10px", borderRadius: "var(--radius-md)", border: "1.5px solid var(--border-color)", backgroundColor: "var(--bg-surface)", color: "var(--text-main)", fontSize: "13px", fontFamily: "inherit" }}
                >
                  <option value="">Tous les contrats</option>
                  {contrats.map(c => <option key={c} value={c}>{c}</option>)}
                </select>

                {/* Filtre ville */}
                <input
                  placeholder="Filtrer par ville…"
                  value={filterVille}
                  onChange={e => { setFilterVille(e.target.value); setPage(1); }}
                  style={{ padding: "6px 12px", borderRadius: "var(--radius-md)", border: "1.5px solid var(--border-color)", backgroundColor: "var(--bg-surface)", color: "var(--text-main)", fontSize: "13px", fontFamily: "inherit", outline: "none" }}
                />

                {/* Tri */}
                <select
                  value={sortBy}
                  onChange={e => { setSortBy(e.target.value); setPage(1); }}
                  style={{ padding: "6px 10px", borderRadius: "var(--radius-md)", border: "1.5px solid var(--border-color)", backgroundColor: "var(--bg-surface)", color: "var(--text-main)", fontSize: "13px", fontFamily: "inherit" }}
                >
                  <option value="score">Tri : Score ↓</option>
                  <option value="ville">Tri : Ville</option>
                </select>
              </div>
            </CardBody>
          </Card>

          {/* Liste d'offres + détail */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }} className="results-grid">
            <style>{`@media(max-width:900px){.results-grid{grid-template-columns:1fr!important;}}`}</style>

            {/* Colonne liste */}
            <div>
              {offresPage.length === 0 ? (
                <Card><EmptyOffers onRetry={() => navigate("/dashboard")} /></Card>
              ) : (
                offresPage.map(offre => {
                  const actif = offreSelectionnee?.id === offre.id;
                  const initiales = (offre.entreprise || "?").substring(0, 2).toUpperCase();
                  return (
                    <Card
                      key={offre.id}
                      hoverable
                      onClick={() => setOffre(offre)}
                      style={{
                        marginBottom: "12px",
                        border: actif ? "2px solid var(--color-primary)" : "1px solid var(--border-color)",
                        boxShadow: actif ? "0 0 0 3px rgba(37,99,235,0.15)" : "var(--shadow-sm)",
                        transition: "all 0.2s",
                        animation: "fadeSlideUp 0.3s ease",
                      }}
                    >
                      <style>{`@keyframes fadeSlideUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}`}</style>
                      <CardBody style={{ padding: "1rem 1.25rem" }}>
                        <div style={{ display: "flex", gap: "12px", alignItems: "flex-start" }}>
                          {/* Logo initiales */}
                          <div style={{
                            width: "44px", height: "44px", borderRadius: "var(--radius-md)",
                            background: "linear-gradient(135deg, var(--color-primary) 0%, #4F46E5 100%)",
                            display: "flex", alignItems: "center", justifyContent: "center",
                            fontSize: "14px", fontWeight: 700, color: "white", flexShrink: 0,
                          }}>
                            {initiales}
                          </div>
                          <div style={{ flex: 1, minWidth: 0 }}>
                            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "8px" }}>
                              <p style={{ margin: 0, fontSize: "14px", fontWeight: 700, color: "var(--text-main)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                                {offre.titre}
                              </p>
                              <ScoreBadge score={offre.score} />
                            </div>
                            <p style={{ margin: "4px 0 8px", fontSize: "12px", color: "var(--text-muted)" }}>
                              {offre.entreprise} · {offre.ville}
                            </p>
                            {/* Tags compétences */}
                            <div style={{ display: "flex", flexWrap: "wrap", gap: "4px" }}>
                              {(offre.competences || []).slice(0, 4).map(comp => (
                                <Badge key={comp} variant="info" size="sm">{comp}</Badge>
                              ))}
                              {offre.contrat && <Badge variant="neutral" size="sm">{offre.contrat}</Badge>}
                            </div>
                          </div>
                        </div>
                        {/* Actions */}
                        <div style={{ display: "flex", gap: "8px", marginTop: "12px", paddingTop: "10px", borderTop: "1px solid var(--border-color)" }}>
                          {offre.source_url && (
                            <a href={offre.source_url} target="_blank" rel="noreferrer">
                              <Button variant="primary" size="sm" icon={<ExternalLink size={12} />}>Voir l'offre</Button>
                            </a>
                          )}
                          <Button variant="ghost" size="sm" icon={<BarChart2 size={12} />} onClick={() => { setOffre(offre); setOnglet("graphiques"); }}>
                            Radar
                          </Button>
                        </div>
                      </CardBody>
                    </Card>
                  );
                })
              )}

              {/* Pagination */}
              {totalPages > 1 && (
                <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px", marginTop: "16px" }}>
                  <Button variant="ghost" size="sm" icon={<ChevronLeft size={14} />} onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} />
                  <span style={{ fontSize: "13px", color: "var(--text-muted)" }}>Page {page} / {totalPages}</span>
                  <Button variant="ghost" size="sm" icon={<ChevronRight size={14} />} onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages} />
                </div>
              )}
            </div>

            {/* Panneau détail offre sélectionnée */}
            {offreSelectionnee && (
              <div style={{ position: "sticky", top: "80px", alignSelf: "flex-start" }}>
                <Card>
                  <CardHeader
                    title={offreSelectionnee.titre}
                    subtitle={`${offreSelectionnee.entreprise} · ${offreSelectionnee.ville}`}
                    action={<ScoreBadge score={offreSelectionnee.score} size="lg" />}
                  />
                  <CardBody>
                    {/* Barre score */}
                    <div style={{ marginBottom: "20px" }}>
                      <p style={{ fontSize: "12px", color: "var(--text-muted)", marginBottom: "6px" }}>Score de compatibilité</p>
                      <p style={{ fontSize: "42px", fontWeight: 800, margin: "0 0 8px", color: offreSelectionnee.score >= 70 ? "var(--color-success)" : offreSelectionnee.score >= 40 ? "var(--color-warning)" : "var(--color-danger)" }}>
                        {offreSelectionnee.score}%
                      </p>
                      <div style={{ height: "8px", borderRadius: "var(--radius-full)", backgroundColor: "var(--color-neutral-200)", overflow: "hidden" }}>
                        <div style={{ height: "100%", width: `${offreSelectionnee.score}%`, borderRadius: "var(--radius-full)", background: "linear-gradient(90deg, var(--color-primary), #4F46E5)", transition: "width 0.6s ease" }} />
                      </div>
                    </div>

                    {/* Compétences matchées */}
                    <p style={{ fontSize: "11px", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: "8px" }}>
                      Compétences requises
                    </p>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: "6px", marginBottom: "20px" }}>
                      {(offreSelectionnee.competences || []).map(comp => (
                        <Badge key={comp} variant="info">{comp}</Badge>
                      ))}
                    </div>

                    {/* Actions */}
                    <div style={{ display: "flex", gap: "10px" }}>
                      {offreSelectionnee.source_url && (
                        <a href={offreSelectionnee.source_url} target="_blank" rel="noreferrer" style={{ flex: 1 }}>
                          <Button variant="primary" fullWidth icon={<ExternalLink size={14} />}>Postuler</Button>
                        </a>
                      )}
                      <Button variant="secondary" icon={<BarChart2 size={14} />} onClick={() => setOnglet("graphiques")}>Radar</Button>
                    </div>
                  </CardBody>
                </Card>
              </div>
            )}
          </div>
        </>
      )}

      {/* ── ONGLET GRAPHIQUES ── */}
      {onglet === "graphiques" && (
        <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
          <Card>
            <CardHeader title="Vos compétences vs l'offre" subtitle={radarLoading ? "Chargement…" : "Teal = votre profil · Orange = offre sélectionnée"} />
            <CardBody>
              <div style={{ maxWidth: "420px", margin: "0 auto" }}>
                <Radar data={radarData} options={{ scales: { r: { beginAtZero: true, max: 100, ticks: { color: "var(--text-muted)" }, grid: { color: "rgba(128,128,128,0.1)" }, pointLabels: { color: "var(--text-main)" } } }, plugins: { legend: { labels: { color: "var(--text-main)" } } } }} />
              </div>
            </CardBody>
          </Card>
          <Card>
            <CardHeader title="Score par offre" subtitle="Vert ≥70% · Orange 40-70% · Rouge <40%" />
            <CardBody><Bar data={barScoresData} options={{ ...chartOptions(), scales: { y: { beginAtZero: true, max: 100, ticks: { color: "var(--text-muted)" }, grid: { color: "rgba(128,128,128,0.1)" } }, x: { ticks: { color: "var(--text-muted)" }, grid: { color: "rgba(128,128,128,0.1)" } } }, plugins: { legend: { display: false } } }} /></CardBody>
          </Card>
          <Card>
            <CardHeader title="Compétences les plus demandées" />
            <CardBody><Bar data={competences} options={{ ...chartOptions(), indexAxis: "y", plugins: { legend: { display: false } }, scales: { x: { beginAtZero: true, max: 100, ticks: { color: "var(--text-muted)" }, grid: { color: "rgba(128,128,128,0.1)" } }, y: { ticks: { color: "var(--text-muted)" }, grid: { color: "rgba(128,128,128,0.1)" } } } }} /></CardBody>
          </Card>
          <Card>
            <CardHeader title="Distribution des scores" />
            <CardBody><Bar data={distribution} options={{ ...chartOptions(), plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { color: "var(--text-muted)" }, grid: { color: "rgba(128,128,128,0.1)" } }, x: { ticks: { color: "var(--text-muted)" }, grid: { color: "rgba(128,128,128,0.1)" } } } }} /></CardBody>
          </Card>
        </div>
      )}

      {/* ── ONGLET CLUSTERS ── */}
      {onglet === "clusters" && (
        <Card>
          <CardHeader title="Clusters K-Means" subtitle="Chaque point = une offre. Couleurs = clusters détectés." />
          <CardBody>
            <Scatter data={clusters} options={{ plugins: { legend: { position: "bottom", labels: { color: "var(--text-main)" } } }, scales: { x: { ticks: { color: "var(--text-muted)" }, grid: { color: "rgba(128,128,128,0.1)" } }, y: { ticks: { color: "var(--text-muted)" }, grid: { color: "rgba(128,128,128,0.1)" } } } }} />
          </CardBody>
        </Card>
      )}
    </AppShell>
  );
}

export default ResultsPage;