import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import CVFormPage from "./pages/CVFormPage";
import DashboardPage from "./pages/DashboardPage";
import ResultsPage from "./pages/ResultsPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Page d'accueil → redirige vers login */}
        <Route path="/" element={<Navigate to="/login" />} />

        <Route path="/login"     element={<LoginPage />} />
        <Route path="/register"  element={<RegisterPage />} />
        <Route path="/cv-form"   element={<CVFormPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/results"   element={<ResultsPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;