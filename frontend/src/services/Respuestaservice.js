import api from "../api/axiosConfig";

const API_URL = "/respuestas";

export const listarRespuestas = async () => {
  const response = await api.get(`${API_URL}/`);
  return response.data;
};

export const obtenerRespuesta = async (id) => {
  const response = await api.get(`${API_URL}/${id}`);
  return response.data;
};

export const crearRespuesta = async (datos) => {
  const response = await api.post(`${API_URL}/`, datos);
  return response.data;
};

// Enviar múltiples respuestas de una sola vez
export const crearRespuestasBulk = async (respuestas) => {
  const response = await api.post(`${API_URL}/bulk`, respuestas);
  return response.data;
};

export const actualizarRespuesta = async (id, datos) => {
  const response = await api.put(`${API_URL}/${id}`, datos);
  return response.data;
};

export const eliminarRespuesta = async (id) => {
  const response = await api.delete(`${API_URL}/${id}`);
  return response.data;
};
