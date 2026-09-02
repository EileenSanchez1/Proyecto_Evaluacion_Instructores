import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import Registro from './pages/Registro';
import RecuperarContrasena from './pages/RecuperarContrasena';
import RestablecerContrasena from './pages/RestablecerContrasena';
import Home from './pages/Home';
import Contacto from './pages/Contacto';
import Instructores from './pages/Instructores';
import CrearInstructor from './pages/CrearInstructor';
import ActualizarInstructor from './pages/ActualizarInstructor';
import EliminarInstructor from './pages/EliminarInstructor';
import Evaluaciones from './pages/Evaluaciones';
import ResponderEvaluacion from './pages/Responderevaluacion';
import Preguntas from './pages/Preguntas';
import Fichas from './pages/Fichas';
import Competencias from './pages/Competencias';
import Horarios from './pages/Horarios';
import Reportes from './pages/Reportes';
import Historial from './pages/Historial';
import Periodos from './pages/Periodos';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import AdminRoute from './components/AdminRoute';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* RUTAS PUBLICAS */}
        <Route path='/login' element={<Login />} />
        <Route path='/registro' element={<Registro />} />
        <Route path='/recuperar-contrasena' element={<RecuperarContrasena />} />
        <Route path='/restablecer-contrasena' element={<RestablecerContrasena />} />

        {/* RUTAS PROTEGIDAS */}
        <Route element={<ProtectedRoute />}>
          <Route element={<Layout />}>
            {/* HOME */}
            <Route path='/' element={<Home />} />

            {/* INSTRUCTORES */}
            <Route path='/instructores' element={<Instructores />} />

            {/* Admin/Coordinador */}
            <Route element={<AdminRoute roles={['Administrador', 'Coordinador']} />}>
              <Route path='/instructores/crear' element={<CrearInstructor />} />
              <Route path='/instructores/editar/:id' element={<ActualizarInstructor />} />
              <Route path='/instructores/eliminar/:id' element={<EliminarInstructor />} />
            </Route>

            {/* EVALUACIONES */}
            <Route path='/evaluaciones' element={<Evaluaciones />} />
            <Route path='/evaluaciones/responder/:id' element={<ResponderEvaluacion />} />
            <Route path='/evaluaciones/:id' element={<ResponderEvaluacion />} />

            {/* PREGUNTAS - Solo Admin */}
            <Route element={<AdminRoute />}>
              <Route path='/preguntas' element={<Preguntas />} />
            </Route>

            {/* Admin/Coordinador */}
            <Route element={<AdminRoute roles={['Administrador', 'Coordinador']} />}>
              <Route path='/fichas' element={<Fichas />} />
              <Route path='/competencias' element={<Competencias />} />
              <Route path='/horarios' element={<Horarios />} />
              <Route path='/periodos' element={<Periodos />} />
              <Route path='/reportes' element={<Reportes />} />
              <Route path='/historial' element={<Historial />} />
            </Route>

            {/* CONTACTO */}
            <Route path='/contacto' element={<Contacto />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;