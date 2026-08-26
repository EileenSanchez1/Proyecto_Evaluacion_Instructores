import axios from "axios";

// Poner sin la barra al final
const API_URL = "http://localhost:8000/aprendices";

export const obtenerAprendiz = async (id) => {
  const response = await axios.get(`${API_URL}/${id}`);
  return response.data;
};

// Registro público de un nuevo aprendiz (crea la cuenta)
export const crearAprendiz = async (datos) => {
  const response = await axios.post(`${API_URL}/`, datos);
  return response.data;
};

// Se usa en Fichas.jsx para contar aprendices por ficha.
// El backend solo expone GET /aprendices/, así que el filtrado
// por id_ficha se hace del lado del frontend.
export const listarAprendices = async () => {
  const response = await axios.get(`${API_URL}/`);
  return response.data;
};