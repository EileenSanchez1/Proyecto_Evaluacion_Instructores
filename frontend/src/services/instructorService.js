import axios from "axios";

// Poner sin la barra al final
const API_URL = "http://localhost:8000/instructores"; 

export const listarInstructores = async () => {
  // Petición directa a /instructores sin '/' al final
  const response = await axios.get(API_URL); 
  return response.data;
};

export const obtenerInstructor = async (id) => {
  const response = await axios.get(`${API_URL}/${id}`);
  return response.data;
};

export const crearInstructor = async (datos) => {
  const response = await axios.post(`${API_URL}/`, datos);
  return response.data;
};

export const actualizarInstructor = async (id, datos) => {
  const response = await axios.put(`${API_URL}/${id}`, datos);
  return response.data;
};

export const eliminarInstructor = async (id) => {
  const response = await axios.delete(`${API_URL}/${id}`);
  return response.data;
};