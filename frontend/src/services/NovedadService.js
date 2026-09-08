import api from "../api/axiosConfig";

const API_URL = "/novedades";

export const enviarNovedad = async (datos) => {
  const response = await api.post(`${API_URL}/`, datos);
  return response.data;
};

export const listarNovedades = async () => {
  const response = await api.get(`${API_URL}/`);
  return response.data;
};

export const marcarNovedadLeida = async (id) => {
  const response = await api.patch(`${API_URL}/${id}/leer`);
  return response.data;
};