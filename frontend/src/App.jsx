import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import CVFormPage from "./pages/CVFormPage";
import DashboardPage from "./pages/DashboardPage";
import ResultsPage from "./pages/ResultsPage";

// Composant PrivateRoute pour protéger les routes authentifiées
const PrivateRoute = ({ children }) => {
  const token = localStorage.getItem("token");
  return token ? children : <Navigate to="/login" replace />;
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Page d'accueil → redirige vers login */}
        <Route path="/" element={<Navigate to="/login" />} />

        {/* Routes publiques - pas de protection */}
        <Route path="/login"     element={<LoginPage />} />
        <Route path="/register"  element={<RegisterPage />} />

        {/* Routes protégées - nécessitent un token */}
        <Route path="/cv-form"   element={<PrivateRoute><CVFormPage /></PrivateRoute>} />   {}
        <Route path="/dashboard" element={<PrivateRoute><DashboardPage /></PrivateRoute>} /> {}
        <Route path="/results"   element={<PrivateRoute><ResultsPage /></PrivateRoute>} />   {}
      </Routes>
    </BrowserRouter>
  );
}

export default App;