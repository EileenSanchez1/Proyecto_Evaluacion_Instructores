import api from "../api/axiosConfig";

export const login = async (datos) => {
  const respuesta = await api.post("/login/", datos);
  return respuesta.data;
};

// Paso 1: el usuario pide el enlace de recuperación (solo correo).
export const solicitarRecuperacion = async (correo) => {
  const respuesta = await api.post("/login/recuperar", { correo });
  return respuesta.data;
};

// Paso 2: el usuario llega desde el enlace del correo con un token
// y define su nueva contraseña.
export const restablecerContrasena = async (token, nuevaContrasena) => {
  const respuesta = await api.post("/login/restablecer", {
    token,
    nueva_contrasena: nuevaContrasena,
  });
  return respuesta.data;
};
