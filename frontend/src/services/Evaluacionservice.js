import axios from "axios";

// Poner sin la barra al final
const API_URL = "http://localhost:8000/evaluaciones";

export const listarEvaluaciones = async () => {
  const response = await axios.get(API_URL);
  return response.data;
};

export const obtenerEvaluacion = async (id) => {
  const response = await axios.get(`${API_URL}/${id}`);
  return response.data;
};

export const crearEvaluacion = async (datos) => {
  const response = await axios.post(`${API_URL}/`, datos);
  return response.data;
};

export const actualizarEvaluacion = async (id, datos) => {
  const response = await axios.put(`${API_URL}/${id}`, datos);
  return response.data;
};

// El backend recibe el estado como query param (?estado=...)
export const cambiarEstadoEvaluacion = async (id, estado) => {
  const response = await axios.patch(
    `${API_URL}/${id}/estado`,
    null,
    { params: { estado } }
  );
  return response.data;
};

export const eliminarEvaluacion = async (id) => {
  const response = await axios.delete(`${API_URL}/${id}`);
  return response.data;
};