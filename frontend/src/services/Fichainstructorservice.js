import api from "../api/axiosConfig";

const API_URL = "/ficha-instructores";

export const listarFichaInstructores = async () => {
  const response = await api.get(`${API_URL}/`);
  return response.data;
};

export const listarInstructoresPorFicha = async (idFicha) => {
  const response = await api.get(`${API_URL}/ficha/${idFicha}`);
  return response.data;
};

export const listarInstructoresPorFichaYPeriodo = async (idFicha, idPeriodo) => {
  const response = await api.get(`${API_URL}/ficha/${idFicha}/periodo/${idPeriodo}`);
  return response.data;
};

export const crearFichaInstructor = async (datos) => {
  const response = await api.post(`${API_URL}/`, datos);
  return response.data;
};

export const eliminarFichaInstructor = async (idRelacion) => {
  const response = await api.delete(`${API_URL}/${idRelacion}`);
  return response.data;
};
