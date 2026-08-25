import { BrowserRouter, Routes, Route } from "react-router-dom";

import Login from "./pages/Login";
import Home from "./pages/Home";
import Contacto from "./pages/Contacto";

import Instructores from "./pages/Instructores";
import CrearInstructor from "./pages/CrearInstructor";
import ActualizarInstructor from "./pages/ActualizarInstructor";
import EliminarInstructor from "./pages/EliminarInstructor";

import Fichas from "./pages/Fichas";

import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";

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

        {/* RUTA PÚBLICA */}
        <Route path="/login" element={<Login />} />

        {/* RUTAS PROTEGIDAS */}
        <Route element={<ProtectedRoute />}>
          <Route element={<Layout />}>

            {/* HOME */}
            <Route path="/" element={<Home />} />

            {/* INSTRUCTORES */}
            <Route
              path="/instructores"
              element={<Instructores />}
            />

            <Route
              path="/instructores/crear"
              element={<CrearInstructor />}
            />

            <Route
              path="/instructores/editar/:id"
              element={<ActualizarInstructor />}
            />

            <Route
              path="/instructores/eliminar/:id"
              element={<EliminarInstructor />}
            />

            {/* EVALUACIONES */}
            <Route
              path="/evaluaciones"
              element={<Evaluaciones />}
            />

            {/* PREGUNTAS */}
            <Route
              path="/preguntas"
              element={<Preguntas />}
            />

            {/* FICHAS */}
            <Route
              path="/fichas"
              element={<Fichas />}
            />

            {/* REPORTES */}
            <Route
              path="/reportes"
              element={<Reportes />}
            />

            {/* CONTACTO */}
            <Route
              path="/contacto"
              element={<Contacto />}
            />

          </Route>
        </Route>

      </Routes>
    </BrowserRouter>
  );
}

export default App;