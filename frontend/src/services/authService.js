import api from "../api/axiosConfig";

// Login general (Aprendiz / Administrador)
export const login = async (datos) => {
  const respuesta = await api.post("/login/", datos);
  return respuesta.data;
};

// ---- Instructor ----

/** Paso 0: solo correo → indica si debe crear contraseña y envía código */
export const instructorIniciar = async (correo) => {
  const respuesta = await api.post("/login/instructor/iniciar", { correo });
  return respuesta.data;
};

/** Primer acceso: código + nueva contraseña → entra al sistema */
export const instructorCrearPassword = async ({ correo, codigo, nueva_contrasena }) => {
  const respuesta = await api.post("/login/instructor/crear-password", {
    correo,
    codigo,
    nueva_contrasena,
  });
  return respuesta.data;
};

/** Login normal instructor: correo + contraseña → envía código */
export const loginInstructorPaso1 = async (datos) => {
  const payload = typeof datos === "object" ? datos : { correo: arguments[0], contrasena: arguments[1] };
  const respuesta = await api.post("/login/instructor", payload);
  return respuesta.data;
};

/** Verificar OTP del instructor (login normal) */
export const verificarCodigoInstructor = async (datos) => {
  const payload = typeof datos === "object" ? datos : { correo: arguments[0], codigo: arguments[1] };
  const respuesta = await api.post("/login/instructor/verificar", payload);
  return respuesta.data;
};

// ---- Recuperación ----

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
