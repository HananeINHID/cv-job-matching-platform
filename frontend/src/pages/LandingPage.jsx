import { useNavigate } from "react-router-dom";
import { 
  CheckCircle, 
  Cpu, 
  Layers, 
  Search, 
  BarChart3, 
  ShieldCheck, 
  Zap, 
  Database, 
  Code2, 
  ArrowRight,
  Target
} from "lucide-react";
import { Button } from "../components/ui/Button";

// Helper components
const Globe = ({ size = 20 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
);

const LandingPage = () => {
  const navigate = useNavigate();

  const techStack = [
    { name: "React 18", icon: <Layers size={20} />, desc: "Interface moderne & réactive" },
    { name: "Django 6.0", icon: <Cpu size={20} />, desc: "Backend robuste & API REST" },
    { name: "Scikit-Learn", icon: <BarChart3 size={20} />, desc: "Matching IA (TF-IDF & K-Means)" },
    { name: "BeautifulSoup, Selenium , Scrapy", icon: <Search size={20} />, desc: "Multi-Source Scraping" },
    { name: "MYSQL", icon: <Database size={20} />, desc: "Persistance des données" },
    { name: "Lucide Icons", icon: <ShieldCheck size={20} />, desc: "Design professionnel" },
  ];

  const features = [
    { title: "Analyse Intelligente", desc: "Comparaison sémantique entre votre CV et les offres via NLP.", icon: <Zap /> },
    { title: "Multi-Source", desc: "Scraping en temps réel de LinkedIn, Rekrute, Emploi.ma et MarocAnnonces.", icon: <Globe /> },
    { title: "Score de Matching", desc: "Un score précis basé sur les compétences, l'expérience et la localisation.", icon: <Target /> },
  ];

  return (
    <div style={{ backgroundColor: "var(--bg-main)", minHeight: "100vh", color: "var(--text-main)" }}>
      {/* Navigation */}
      <nav style={{ 
        display: "flex", justifyContent: "space-between", alignItems: "center", 
        padding: "20px 5%", borderBottom: "1px solid var(--border-color)", 
        backgroundColor: "var(--bg-surface)", position: "sticky", top: 0, zIndex: 100 
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px", fontWeight: 800, fontSize: "20px" }}>
          <Target color="var(--color-primary)" size={28} />
          <span>Talent<span style={{ color: "var(--color-primary)" }}>Match</span></span>
        </div>
        <div style={{ display: "flex", gap: "15px" }}>
          <Button variant="ghost" onClick={() => navigate("/login")}>Connexion</Button>
          <Button variant="primary" onClick={() => navigate("/register")}>S'inscrire</Button>
        </div>
      </nav>

      {/* Hero Section */}
      <section style={{ 
        padding: "100px 5%", textAlign: "center", background: "var(--gradient-primary)", color: "white" 
      }}>
        <h1 style={{ fontSize: "56px", fontWeight: 800, marginBottom: "20px", lineHeight: 1.1 }}>
          Propulsez votre carrière avec <br/> l'Intelligence Artificielle
        </h1>
        <p style={{ fontSize: "18px", opacity: 0.9, maxWidth: "700px", margin: "0 auto 40px", lineHeight: 1.6 }}>
          Notre plateforme analyse votre profil en profondeur pour vous connecter 
          aux meilleures opportunités d'emploi sur le marché marocain.
        </p>
        <div style={{ display: "flex", justifyContent: "center", gap: "20px" }}>
          <Button 
            variant="secondary" 
            size="lg" 
            onClick={() => navigate("/register")}
            style={{ padding: "15px 40px", fontSize: "16px", fontWeight: 700 }}
          >
            Commencer maintenant
          </Button>
        </div>
      </section>

      {/* About Project */}
      <section style={{ padding: "80px 10%" }}>
        <div style={{ textAlign: "center", marginBottom: "60px" }}>
          <h2 style={{ fontSize: "32px", fontWeight: 700, marginBottom: "15px" }}>À propos du projet</h2>
          <div style={{ width: "60px", height: "4px", backgroundColor: "var(--color-primary)", margin: "0 auto" }} />
        </div>
        
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "30px" }}>
          <div className="glass" style={{ padding: "40px", borderRadius: "var(--radius-lg)" }}>
            <h3 style={{ marginBottom: "15px", display: "flex", alignItems: "center", gap: "10px" }}>
              <Zap color="var(--color-warning)" /> La Vision
            </h3>
            <p style={{ color: "var(--text-muted)", lineHeight: 1.6 }}>
              TalentMatch est née de la volonté de simplifier la recherche d'emploi au Maroc. 
              Au lieu de parcourir manuellement des dizaines de sites, notre plateforme centralise 
              et filtre les offres selon votre véritable potentiel.
            </p>
          </div>
          <div className="glass" style={{ padding: "40px", borderRadius: "var(--radius-lg)" }}>
            <h3 style={{ marginBottom: "15px", display: "flex", alignItems: "center", gap: "10px" }}>
              <CheckCircle color="var(--color-success)" /> Le Fonctionnement
            </h3>
            <p style={{ color: "var(--text-muted)", lineHeight: 1.6 }}>
              Le système utilise un algorithme de matching pondéré qui combine la similarité 
              TF-IDF (texte), l'analyse Jaccard (compétences), l'adéquation d'expérience 
              et la proximité géographique.
            </p>
          </div>
        </div>
      </section>

      {/* Tech Stack */}
      <section style={{ padding: "80px 10%", backgroundColor: "var(--bg-surface)" }}>
        <div style={{ textAlign: "center", marginBottom: "60px" }}>
          <h2 style={{ fontSize: "32px", fontWeight: 700, marginBottom: "15px" }}>Stack Technique</h2>
          <p style={{ color: "var(--text-muted)" }}>Les outils et technologies qui propulsent la plateforme</p>
        </div>
        
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "20px" }}>
          {techStack.map((tech, i) => (
            <div key={i} style={{ 
              display: "flex", alignItems: "center", gap: "15px", padding: "20px",
              border: "1px solid var(--border-color)", borderRadius: "var(--radius-md)"
            }}>
              <div style={{ 
                color: "var(--color-primary)", backgroundColor: "var(--color-primary-light)",
                padding: "10px", borderRadius: "10px" 
              }}>
                {tech.icon}
              </div>
              <div>
                <h4 style={{ margin: 0, fontSize: "16px" }}>{tech.name}</h4>
                <p style={{ margin: 0, fontSize: "13px", color: "var(--text-muted)" }}>{tech.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer style={{ 
        padding: "60px 10%", borderTop: "1px solid var(--border-color)", 
        textAlign: "center", backgroundColor: "var(--bg-surface)" 
      }}>
        <div style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: "10px", fontWeight: 800, marginBottom: "20px" }}>
          <Target color="var(--color-primary)" size={24} />
          <span>Talent<span style={{ color: "var(--color-primary)" }}>Match</span></span>
        </div>
        <p style={{ color: "var(--text-muted)", fontSize: "14px" }}>
          © 2026 TalentMatch Maroc. Tous droits réservés. <br/>
          Une plateforme intelligente dédiée à l'emploi.
        </p>
      </footer>
    </div>
  );
};


export default LandingPage;
