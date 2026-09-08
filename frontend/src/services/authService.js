import api from "../api/axiosConfig";

// Login general (Aprendiz / Administrador)
export const login = async (datos) => {
  const respuesta = await api.post("/login/", datos);
  return respuesta.data;
};

// Paso 1: Login de Instructor (Valida correo @sena.edu.co y contraseña, e inicia/envía el código)
export const loginInstructorPaso1 = async (correo, contrasena) => {
  const respuesta = await api.post("/login/instructor", {
    correo,
    contrasena,
  });
  return respuesta.data;
};

// Paso 2: Verificar el código OTP que le llegó al correo al instructor
export const verificarCodigoInstructor = async (correo, codigo) => {
  const respuesta = await api.post("/login/verificar-codigo", {
    correo,
    codigo,
  });
  return respuesta.data;
};

// Paso 1 Recuperación: solicitar enlace de recuperación
export const solicitarRecuperacion = async (correo) => {
  const respuesta = await api.post("/login/recuperar", { correo });
  return respuesta.data;
};

// Paso 2 Recuperación: definir nueva contraseña
export const restablecerContrasena = async (token, nuevaContrasena) => {
  const respuesta = await api.post("/login/restablecer", {
    token,
    nueva_contrasena: nuevaContrasena,
  });
  return respuesta.data;
};