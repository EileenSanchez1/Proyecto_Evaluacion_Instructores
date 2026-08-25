import axios from "axios";

// Poner sin la barra al final
const API_URL = "http://localhost:8000/preguntas";

export const listarPreguntas = async () => {
  const response = await axios.get(API_URL);
  return response.data;
};

// Solo las preguntas habilitadas para responder (estado = true)
export const listarPreguntasActivas = async () => {
  const response = await axios.get(`${API_URL}/activas`);
  return response.data;
};

export const obtenerPregunta = async (id) => {
  const response = await axios.get(`${API_URL}/${id}`);
  return response.data;
};

export const crearPregunta = async (datos) => {
  const response = await axios.post(`${API_URL}/`, datos);
  return response.data;
};

export const actualizarPregunta = async (id, datos) => {
  const response = await axios.put(`${API_URL}/${id}`, datos);
  return response.data;
};

export const eliminarPregunta = async (id) => {
  const response = await axios.delete(`${API_URL}/${id}`);
  return response.data;
};