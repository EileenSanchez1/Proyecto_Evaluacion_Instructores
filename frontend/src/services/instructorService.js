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

export const listarInstructores = async () => {
  const response = await api.get(API_URL);
  return response.data;
};

export const obtenerInstructor = async (id) => {
  const response = await api.get(`${API_URL}${id}`);
  return response.data;
};

export const crearInstructor = async (datos) => {
  const body = prepararFormData(datos);
  const response = await api.post(API_URL, body);
  return response.data;
};

export const actualizarInstructor = async (id, datos) => {
  const body = prepararFormData(datos);
  const response = await api.put(`${API_URL}${id}`, body);
  return response.data;
};

export const eliminarInstructor = async (id) => {
  const response = await api.delete(`${API_URL}${id}`);
  return response.data;
};

/** Admin: fuerza primer acceso (código + crear contraseña) */
export const resetPrimerAccesoInstructor = async (id) => {
  const response = await api.post(`${API_URL}${id}/reset-primer-acceso`);
  return response.data;
};
