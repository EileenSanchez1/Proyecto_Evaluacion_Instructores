import { Navigate, Outlet } from "react-router-dom";

function ProtectedRoute() {
  const usuario = localStorage.getItem("usuario");

  if (!usuario) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}

export default ProtectedRoute;