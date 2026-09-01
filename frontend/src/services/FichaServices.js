import api from '../api/axiosConfig';

export const listarFichas = async () => {
  const response = await api.get('/fichas');
  return response.data;
};

export const obtenerFicha = async (id) => {
  const response = await api.get(`/fichas/${id}`);
  return response.data;
};

export const crearFicha = async (datos) => {
  const response = await api.post('/fichas/', datos);
  return response.data;
};

export const actualizarFicha = async (id, datos) => {
  const response = await api.put(`/fichas/${id}`, datos);
  return response.data;
};

export const eliminarFicha = async (id) => {
  const response = await api.delete(`/fichas/${id}`);
  return response.data;
};