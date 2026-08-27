import { BrowserRouter, Routes, Route } from "react-router-dom";

import Login from "./pages/Login";
import Registro from "./pages/Registro";
import RecuperarContrasena from "./pages/RecuperarContrasena";
import RestablecerContrasena from "./pages/RestablecerContrasena";
import Home from "./pages/Home";
import Contacto from "./pages/Contacto";

import Instructores from "./pages/Instructores";
import CrearInstructor from "./pages/CrearInstructor";
import ActualizarInstructor from "./pages/ActualizarInstructor";
import EliminarInstructor from "./pages/EliminarInstructor";

import Evaluaciones from "./pages/Evaluaciones";
import ResponderEvaluacion from "./pages/Responderevaluacion";
import Preguntas from "./pages/Preguntas";
import Fichas from "./pages/Fichas";
import Competencias from "./pages/Competencias";
import Horarios from "./pages/Horarios";

import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";
import AdminRoute from "./components/AdminRoute";

function Reportes() {
  return <h1>Reportes</h1>;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* RUTAS PÚBLICAS */}
        <Route path="/login" element={<Login />} />
        <Route path="/registro" element={<Registro />} />
        <Route path="/recuperar-contrasena" element={<RecuperarContrasena />} />
        <Route path="/restablecer-contrasena" element={<RestablecerContrasena />} />

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

            {/* Instructores/Fichas/Competencias/Horarios: el backend permite
                Administrador y Coordinador (require_roles("Administrador","Coordinador")).
                Se alinea el frontend a lo mismo para no bloquear al Coordinador
                de algo que la API sí le permite. */}
            <Route element={<AdminRoute roles={["Administrador", "Coordinador"]} />}>
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
            </Route>

            {/* EVALUACIONES */}
            <Route
              path="/evaluaciones"
              element={<Evaluaciones />}
            />

            <Route
              path="/evaluaciones/:id"
              element={<ResponderEvaluacion />}
            />

            {/* Preguntas sigue exclusivo de Administrador (edición de
                banco de preguntas de evaluación). Fichas/Competencias/
                Horarios se abren también a Coordinador, igual que el backend. */}
            <Route element={<AdminRoute />}>
              {/* PREGUNTAS */}
              <Route
                path="/preguntas"
                element={<Preguntas />}
              />
            </Route>

            <Route element={<AdminRoute roles={["Administrador", "Coordinador"]} />}>
              {/* FICHAS */}
              <Route
                path="/fichas"
                element={<Fichas />}
              />

              {/* COMPETENCIAS (Etapa 2 / HU-007) */}
              <Route
                path="/competencias"
                element={<Competencias />}
              />

              {/* HORARIOS (Etapa 2 / HU-010) */}
              <Route
                path="/horarios"
                element={<Horarios />}
              />

              {/* REPORTES */}
              <Route
                path="/reportes"
                element={<Reportes />}
              />
            </Route>

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