import api from "../api/axiosConfig";

// CORREGIDO: usa la instancia 'api' (con token JWT automático)
// en vez de axios directo. Se añade '/' al final para evitar
// redirección 307 de FastAPI.
const API_URL = "/horarios/";

export const listarHorarios = async () => {
  const response = await api.get(API_URL);
  return response.data;
};

export const listarHorariosPorInstructor = async (idInstructor) => {
  const response = await api.get(`${API_URL}instructor/${idInstructor}`);
  return response.data;
};

export const listarHorariosPorFicha = async (idFicha) => {
  const response = await api.get(`${API_URL}ficha/${idFicha}`);
  return response.data;
};

export const crearHorario = async (datos) => {
  const response = await api.post(API_URL, datos);
  return response.data;
};

export const actualizarHorario = async (id, datos) => {
  const response = await api.put(`${API_URL}${id}`, datos);
  return response.data;
};

export const eliminarHorario = async (id) => {
  const response = await api.delete(`${API_URL}${id}`);
  return response.data;
};
