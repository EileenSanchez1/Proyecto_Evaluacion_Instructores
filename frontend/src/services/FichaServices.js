import api from '../api/axiosConfig';

export const listarFichas = async () => {
  const response = await api.get('/fichas');
  return response.data;
};

export const obtenerFicha = async (id) => {
  const response = await api.get(`/fichas/${id}`);
  return response.data;
};