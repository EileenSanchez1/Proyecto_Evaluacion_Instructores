// Utilidad compartida para leer los datos de la sesión guardada en el login.

export function obtenerAprendizSesion() {
  try {
    const datos = JSON.parse(localStorage.getItem("usuario"));
    return datos?.aprendiz || null;
  } catch {
    return null;
  }
}

export function esAdmin() {
  const aprendiz = obtenerAprendizSesion();
  return Boolean(aprendiz?.es_admin);
}
