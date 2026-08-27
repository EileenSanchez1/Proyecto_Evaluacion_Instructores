// Utilidad compartida para leer los datos de la sesión guardada en el login.
// Desde la migración a JWT + roles, la sesión ya no guarda "es_admin";
// guarda el usuario real (con su rol) devuelto por /login/.

export function obtenerUsuarioSesion() {
  try {
    return JSON.parse(localStorage.getItem("usuario")) || null;
  } catch {
    return null;
  }
}

export function obtenerRol() {
  const usuario = obtenerUsuarioSesion();
  return usuario?.rol || null;
}

export function tieneRol(...rolesPermitidos) {
  const rol = obtenerRol();
  return rolesPermitidos.includes(rol);
}

export function esAdmin() {
  return tieneRol("Administrador");
}

export function cerrarSesion() {
  localStorage.removeItem("usuario");
  localStorage.removeItem("token");
}
