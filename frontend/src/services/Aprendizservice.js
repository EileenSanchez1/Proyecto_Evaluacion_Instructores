import api from "../api/axiosConfig";

const API_URL = "/aprendices";

export const obtenerAprendiz = async (id) => {
  const response = await api.get(`${API_URL}/${id}`);
  return response.data;
};

export const crearAprendiz = async (datos) => {
  const response = await api.post(`${API_URL}/`, datos);
  return response.data;
};

export const listarAprendices = async () => {
  const response = await api.get(`${API_URL}/`);
  return response.data;
};
