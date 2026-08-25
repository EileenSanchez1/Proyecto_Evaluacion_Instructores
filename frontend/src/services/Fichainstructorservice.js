import axios from "axios";

// Poner sin la barra al final
const API_URL = "http://localhost:8000/ficha-instructores";

// Instructores asignados a la ficha del aprendiz que está evaluando
export const listarInstructoresPorFicha = async (idFicha) => {
  const response = await axios.get(`${API_URL}/ficha/${idFicha}`);
  return response.data;
};