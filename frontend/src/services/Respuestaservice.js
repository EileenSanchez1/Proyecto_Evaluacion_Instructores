import axios from "axios";

// Poner sin la barra al final
const API_URL = "http://localhost:8000/respuestas";

// El backend no expone un filtro por evaluación, así que se trae
// el listado completo (con un límite alto) y se filtra en el frontend.
export const listarRespuestas = async () => {
  const response = await axios.get(API_URL, {
    params: { limit: 1000 },
  });
  return response.data;
};

export const crearRespuesta = async (datos) => {
  const response = await axios.post(`${API_URL}/`, datos);
  return response.data;
};

export const actualizarRespuesta = async (id, datos) => {
  const response = await axios.put(`${API_URL}/${id}`, datos);
  return response.data;
};

export const eliminarRespuesta = async (id) => {
  const response = await axios.delete(`${API_URL}/${id}`);
  return response.data;
};