import { BrowserRouter, Routes, Route } from "react-router-dom";

import Login from "./pages/Login";
import Home from "./pages/Home";
import Contacto from "./pages/Contacto";
import Layout from "./components/Layout";

// Componentes temporales
function Instructores() {
  return <h1>Instructores</h1>;
}

function Evaluaciones() {
  return <h1>Evaluaciones</h1>;
}

function Preguntas() {
  return <h1>Preguntas</h1>;
}

function Fichas() {
  return <h1>Fichas</h1>;
}

function Reportes() {
  return <h1>Reportes</h1>;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* Login sin Layout */}
        <Route path="/login" element={<Login />} />

        {/* Todas las demás páginas con el Layout (sidebar + header) */}
        <Route element={<Layout />}>
          <Route path="/" element={<Home usuario={true} rol="aprendiz" />} />
          <Route path="/home" element={<Home usuario={true} rol="aprendiz" />} />
          <Route path="/instructores" element={<Instructores />} />
          <Route path="/evaluaciones" element={<Evaluaciones />} />
          <Route path="/preguntas" element={<Preguntas />} />
          <Route path="/fichas" element={<Fichas />} />
          <Route path="/reportes" element={<Reportes />} />
          <Route path="/contacto" element={<Contacto />} />
        </Route>

      </Routes>
    </BrowserRouter>
  );
}

export default App;