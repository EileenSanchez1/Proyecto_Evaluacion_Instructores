import { Navigate, Outlet } from "react-router-dom";
import { esAdmin } from "../utils/sesion";

// Igual que ProtectedRoute, pero además exige que el usuario sea admin.
// Si un aprendiz intenta entrar por URL directa, lo devolvemos a Instructores.
function AdminRoute() {
  if (!esAdmin()) {
    return <Navigate to="/instructores" replace />;
  }

  return <Outlet />;
}

export default AdminRoute;
