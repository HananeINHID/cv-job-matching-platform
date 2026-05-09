import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LoginPage    from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import CVFormPage   from "./pages/CVFormPage";
import DashboardPage from "./pages/DashboardPage";
import ResultsPage  from "./pages/ResultsPage";

// Protège les routes : redirige vers /login si non authentifié
const PrivateRoute = ({ children }) => {
  const token = localStorage.getItem("token");
  return token ? children : <Navigate to="/login" replace />;
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/"         element={<Navigate to="/dashboard" />} />
        <Route path="/login"    element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/cv-form"  element={<PrivateRoute><CVFormPage /></PrivateRoute>} />
        <Route path="/dashboard" element={<PrivateRoute><DashboardPage /></PrivateRoute>} />
        <Route path="/results"  element={<PrivateRoute><ResultsPage /></PrivateRoute>} />
        {/* Fallback */}
        <Route path="*"         element={<Navigate to="/dashboard" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;