import api from "../api/axiosConfig";

export const login = async (datos) => {
  const respuesta = await api.post("/login/", datos);
  return respuesta.data;
};

/** Paso 0 instructor: solo correo */
export const instructorIniciar = async (correo) => {
  const respuesta = await api.post("/login/instructor/iniciar", { correo });
  return respuesta.data;
};

/** Primer acceso: código + contraseña nueva */
export const instructorCrearPassword = async ({ correo, codigo, nueva_contrasena }) => {
  const respuesta = await api.post("/login/instructor/crear-password", {
    correo,
    codigo,
    nueva_contrasena,
  });
  return respuesta.data;
};

/** Login normal instructor: correo + contraseña → token directo */
export const loginInstructorPaso1 = async (datos) => {
  const payload = typeof datos === "object" ? datos : { correo: arguments[0], contrasena: arguments[1] };
  const respuesta = await api.post("/login/instructor", payload);
  return respuesta.data;
};

export const verificarCodigoInstructor = async (datos) => {
  const payload = typeof datos === "object" ? datos : { correo: arguments[0], codigo: arguments[1] };
  const respuesta = await api.post("/login/instructor/verificar", payload);
  return respuesta.data;
};

export const solicitarRecuperacion = async (correo) => {
  const respuesta = await api.post("/login/recuperar", { correo });
  return respuesta.data;
};

export const verificarCodigoRecuperacion = async (correo, codigo) => {
  const respuesta = await api.post("/login/verificar-codigo", { correo, codigo });
  return respuesta.data;
};

export const restablecerContrasena = async ({ correo, codigo, nueva_contrasena }) => {
  const respuesta = await api.post("/login/restablecer", {
    correo,
    codigo,
    nueva_contrasena,
  });
  return respuesta.data;
};
