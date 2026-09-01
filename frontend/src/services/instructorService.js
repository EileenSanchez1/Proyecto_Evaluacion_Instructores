import api from "../api/axiosConfig";

// Se añade '/' al final para evitar la redirección 307 de FastAPI
const API_URL = "/instructores/";

/**
 * Convierte un objeto plano de JavaScript a FormData
 * cuando se requiere enviar archivos o formularios 'multipart/form-data'.
 */
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
  const response = await api.post(API_URL, body, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return response.data;
};

export const actualizarInstructor = async (id, datos) => {
  const body = prepararFormData(datos);
  const response = await api.put(`${API_URL}${id}`, body, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return response.data;
};

export const eliminarInstructor = async (id) => {
  const response = await api.delete(`${API_URL}${id}`);
  return response.data;
};