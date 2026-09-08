import { Navigate, Outlet } from "react-router-dom";
import { tieneRol, esInstructor } from "../utils/sesion";

// Protección de UI. La seguridad real está en el backend (require_roles).
function AdminRoute({ roles = ["Administrador"] }) {
  if (!tieneRol(...roles)) {
    // Instructores van a su home; otros roles a una ruta segura
    if (esInstructor()) {
      return <Navigate to="/" replace />;
    }
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
}

export default AdminRoute;
