import axios from "axios";

const API_URL = "http://localhost:8000/horarios";

export const listarHorarios = async () => {
  const response = await axios.get(API_URL);
  return response.data;
};

export const listarHorariosPorInstructor = async (idInstructor) => {
  const response = await axios.get(`${API_URL}/instructor/${idInstructor}`);
  return response.data;
};

export const listarHorariosPorFicha = async (idFicha) => {
  const response = await axios.get(`${API_URL}/ficha/${idFicha}`);
  return response.data;
};

export const crearHorario = async (datos) => {
  const response = await axios.post(`${API_URL}/`, datos);
  return response.data;
};

export const actualizarHorario = async (id, datos) => {
  const response = await axios.put(`${API_URL}/${id}`, datos);
  return response.data;
};

export const eliminarHorario = async (id) => {
  const response = await axios.delete(`${API_URL}/${id}`);
  return response.data;
};
