import { Navigate, Outlet } from "react-router-dom";
import { tieneRol } from "../utils/sesion";

// Ojo: esto es solo conveniencia de UI (ocultar/redirigir en React).
// La protección real vive en el backend con require_roles(...),
// así que aunque alguien manipule el localStorage no puede hacer
// nada porque FastAPI vuelve a validar el rol con cada request.
function AdminRoute({ roles = ["Administrador"] }) {
  if (!tieneRol(...roles)) {
    return <Navigate to="/instructores" replace />;
  }

  return <Outlet />;
}

export default AdminRoute;
