import axios from "axios";

const API_URL = "http://localhost:8000/competencias";

export const listarCompetencias = async () => {
  const response = await axios.get(API_URL);
  return response.data;
};

export const obtenerCompetencia = async (id) => {
  const response = await axios.get(`${API_URL}/${id}`);
  return response.data;
};

export const crearCompetencia = async (datos) => {
  const response = await axios.post(`${API_URL}/`, datos);
  return response.data;
};

export const actualizarCompetencia = async (id, datos) => {
  const response = await axios.put(`${API_URL}/${id}`, datos);
  return response.data;
};

export const eliminarCompetencia = async (id) => {
  const response = await axios.delete(`${API_URL}/${id}`);
  return response.data;
};
