import api from "../api/axiosConfig";

const API_URL = "/resultados-aprendizaje";

export const listarResultadosAprendizaje = async () => {
  const response = await api.get(API_URL);
  return response.data;
};

export const obtenerResultadoAprendizaje = async (id) => {
  const response = await api.get(`${API_URL}/${id}`);
  return response.data;
};

export const crearResultadoAprendizaje = async (datos) => {
  const response = await api.post(`${API_URL}/`, datos);
  return response.data;
};

export const actualizarResultadoAprendizaje = async (id, datos) => {
  const response = await api.put(`${API_URL}/${id}`, datos);
  return response.data;
};

export const eliminarResultadoAprendizaje = async (id) => {
  const response = await api.delete(`${API_URL}/${id}`);
  return response.data;
};

export const reactivarResultadoAprendizaje = async (id) => {
  const response = await api.post(`${API_URL}/${id}/reactivar`, {});
  return response.data;
};

// Alias de compatibilidad
export const listarCompetencias = listarResultadosAprendizaje;
export const crearCompetencia = crearResultadoAprendizaje;
export const actualizarCompetencia = actualizarResultadoAprendizaje;
export const eliminarCompetencia = eliminarResultadoAprendizaje;
export const reactivarCompetencia = reactivarResultadoAprendizaje;
