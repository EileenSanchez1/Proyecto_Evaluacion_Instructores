import api from "../api/axiosConfig";

const API_URL = "/instructores/";

const prepararFormData = (datos) => {
  if (datos instanceof FormData) return datos;
  const formData = new FormData();
  Object.keys(datos).forEach((key) => {
    if (datos[key] !== null && datos[key] !== undefined) {
      formData.append(key, datos[key]);
    }
  });
  return formData;
};

export const listarInstructores = async (incluirInactivos = false) => {
  const response = await api.get(API_URL, {
    params: incluirInactivos ? { incluir_inactivos: true } : {},
  });
  return response.data;
};

export const obtenerInstructor = async (id) => {
  const response = await api.get(`${API_URL}${id}`);
  return response.data;
};

export const crearInstructor = async (datos) => {
  const body = prepararFormData(datos);
  const response = await api.post(API_URL, body, {
    headers: { "Content-Type": undefined },
  });
  return response.data;
};

/**
 * Actualiza datos por JSON.
 * datos: { nombre, apellido, correo, telefono, planta_contrato, resultados_aprendizaje, foto? }
 */
export const actualizarInstructor = async (id, datos) => {
  let payload = {
    nombre: "",
    apellido: "",
    correo: "",
    telefono: "",
    planta_contrato: null,
    resultados_aprendizaje: [],
  };
  let fotoFile = null;

  if (typeof FormData !== "undefined" && datos instanceof FormData) {
    payload.nombre = datos.get("nombre") || "";
    payload.apellido = datos.get("apellido") || "";
    payload.correo = datos.get("correo") || "";
    payload.telefono = datos.get("telefono") || "";
    payload.planta_contrato = datos.get("planta_contrato") || null;
    const ra = datos.get("resultados_aprendizaje") || datos.get("competencias");
    try {
      payload.resultados_aprendizaje = ra ? JSON.parse(ra) : [];
    } catch {
      payload.resultados_aprendizaje = [];
    }
    fotoFile = datos.get("foto");
    if (fotoFile && typeof fotoFile === "string") fotoFile = null;
  } else {
    payload = {
      nombre: datos.nombre,
      apellido: datos.apellido,
      correo: datos.correo,
      telefono: datos.telefono,
      planta_contrato: datos.planta_contrato ?? null,
      resultados_aprendizaje:
        datos.resultados_aprendizaje || datos.competencias || [],
    };
    fotoFile = datos.fotoArchivo || datos.foto || null;
    if (fotoFile && !(fotoFile instanceof File) && !(fotoFile instanceof Blob)) {
      fotoFile = null;
    }
  }

  const response = await api.put(`${API_URL}${id}`, payload);
  const actualizado = response.data;

  if (fotoFile) {
    const fd = new FormData();
    fd.append("foto", fotoFile);
    const fotoRes = await api.post(`${API_URL}${id}/foto`, fd, {
      headers: { "Content-Type": undefined },
    });
    return fotoRes.data;
  }

  return actualizado;
};

export const eliminarInstructor = async (id) => {
  const response = await api.delete(`${API_URL}${id}`);
  return response.data;
};

export const resetPrimerAccesoInstructor = async (id) => {
  const response = await api.post(`${API_URL}${id}/reset-primer-acceso`);
  return response.data;
};

export const reactivarInstructor = async (id) => {
  const response = await api.post(`${API_URL}${id}/reactivar`);
  return response.data;
};

export const cargaMasivaInstructores = async (formData) => {
  const response = await api.post(`${API_URL}carga-masiva`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};

/** Envía credenciales a instructores pendientes (o a uno) */
export const reenviarCorreosInstructores = async (params = {}) => {
  const response = await api.post(`${API_URL}reenviar-correos`, null, { params });
  return response.data;
};

export const reenviarCorreoInstructor = async (idInstructor) => {
  const response = await api.post(`${API_URL}reenviar-correos`, null, {
    params: { id_instructor: idInstructor },
  });
  return response.data;
};
