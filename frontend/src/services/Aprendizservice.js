import axios from "axios";

// Poner sin la barra al final
const API_URL = "http://localhost:8000/aprendices";

export const listarAprendices = async () => {
  const response = await axios.get(API_URL, {
    params: { limit: 1000 },
  });
  return response.data;
};

export const obtenerAprendiz = async (id) => {
  const response = await axios.get(`${API_URL}/${id}`);
  return response.data;
};