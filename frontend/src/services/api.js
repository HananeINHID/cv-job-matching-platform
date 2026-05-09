import axios from "axios";

const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000/api",
});

API.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ── Endpoints helpers ──────────────────────────────────────────────────────

/** Historique des recherches de l'utilisateur connecté */
export const getHistory = () => API.get("/profile/history/");

/** Radar CV vs offre : retourne { labels, cv, offre } */
export const getRadar = (jobId) => API.get(`/jobs/${jobId}/radar/`);

/** Compétences les plus demandées : retourne [{ text, value }] */
export const getWordcloud = () => API.get("/stats/wordcloud/");

/** Distribution des scores : retourne { labels, counts } */
export const getScoreDistribution = () => API.get("/stats/score-distribution/");

/** Clusters K-Means : retourne [{ cluster_id, label, points:[{x,y}] }]
 *  OU [{ x, y, cluster, label }] — les deux formats sont gérés côté page */
export const getClusters = () => API.get("/matching/clusters/");

/** Recherche avec choix de source */
export const searchJobs = (q, source = "dataset") =>
  API.get("/jobs/search/", { params: { q, source } });

/** Déclenche le scraper LinkedIn en temps réel */
export const triggerScraper = (keyword) =>
  API.post("/jobs/scrape/", { keyword });

export default API;