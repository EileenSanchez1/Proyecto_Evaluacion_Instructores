import axios from "axios";

// Poner sin la barra al final
const API_URL = "http://localhost:8000/aprendices";

export const obtenerAprendiz = async (id) => {
  const response = await axios.get(`${API_URL}/${id}`);
  return response.data;
};