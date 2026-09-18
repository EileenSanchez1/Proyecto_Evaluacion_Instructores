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
 * Actualiza datos por JSON. Si hay archivo de foto, lo sube en un segundo request.
 * datos puede ser:
 *  - FormData (compat): extrae campos
 *  - objeto { nombre, apellido, correo, telefono, competencias, foto? }
 */
export const actualizarInstructor = async (id, datos) => {
  let payload = {
    nombre: "",
    apellido: "",
    correo: "",
    telefono: "",
    competencias: [],
  };
  let fotoFile = null;

  if (typeof FormData !== "undefined" && datos instanceof FormData) {
    payload.nombre = datos.get("nombre") || "";
    payload.apellido = datos.get("apellido") || "";
    payload.correo = datos.get("correo") || "";
    payload.telefono = datos.get("telefono") || "";
    const comps = datos.get("competencias");
    try {
      payload.competencias = comps ? JSON.parse(comps) : [];
    } catch {
      payload.competencias = [];
    }
    fotoFile = datos.get("foto");
    if (fotoFile && typeof fotoFile === "string") fotoFile = null;
  } else {
    payload = {
      nombre: datos.nombre,
      apellido: datos.apellido,
      correo: datos.correo,
      telefono: datos.telefono,
      competencias: datos.competencias || [],
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
