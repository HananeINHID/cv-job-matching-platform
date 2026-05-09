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

// Interceptor for responses to handle 401 Unauthorized globally
API.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    // Si l'erreur est 401 et ce n'est pas déjà une tentative de retry
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem("refresh_token");

      if (refreshToken) {
        try {
          // Demander un nouveau token d'accès
          const response = await axios.post(`${API.defaults.baseURL}/token/refresh/`, {
            refresh: refreshToken,
          });
          const newToken = response.data.access;
          localStorage.setItem("token", newToken);
          
          // Mettre à jour le header Authorization de la requête originale et relancer
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          return API(originalRequest);
        } catch (refreshError) {
          // Si le refresh token est expiré ou invalide
          localStorage.removeItem("token");
          localStorage.removeItem("refresh_token");
          window.location.href = "/login";
        }
      } else {
        // Pas de refresh token disponible
        localStorage.removeItem("token");
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

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

/** Déclenche le scraper explicitement */
export const triggerScraper = (q, source) => {
  if (source === "linkedin") {
    return API.post("/jobs/scrape/", { keyword: q });
  }
  return API.get("/jobs/search/", { params: { q, source } });
};

export default API;