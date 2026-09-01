import axios from "axios";

const API_URL = "http://localhost:8000/competencias";

// Helper para obtener la cabecera con el token de autenticación
const getAuthHeaders = () => {
  const token = localStorage.getItem("token"); // Asegúrate de que este sea el nombre de la clave en localStorage
  return {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  };
};

export const listarCompetencias = async () => {
  const response = await axios.get(API_URL);
  return response.data;
};

export const obtenerCompetencia = async (id) => {
  const response = await axios.get(`${API_URL}/${id}`);
  return response.data;
};

export const crearCompetencia = async (datos) => {
  const response = await axios.post(`${API_URL}/`, datos, getAuthHeaders());
  return response.data;
};

export const actualizarCompetencia = async (id, datos) => {
  const response = await axios.put(`${API_URL}/${id}`, datos, getAuthHeaders());
  return response.data;
};

export const eliminarCompetencia = async (id) => {
  const response = await axios.delete(`${API_URL}/${id}`, getAuthHeaders());
  return response.data;
};