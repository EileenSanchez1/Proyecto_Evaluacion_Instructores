import api from "../api/axiosConfig";

const API_URL = "/evaluaciones";

export const listarEvaluaciones = async () => {
  const response = await api.get(`${API_URL}/`);
  return response.data;
};

export const obtenerEvaluacion = async (id) => {
  const response = await api.get(`${API_URL}/${id}`);
  return response.data;
};

export const crearEvaluacion = async (datos) => {
  const response = await api.post(`${API_URL}/`, datos);
  return response.data;
};

// Iniciar evaluación de un aprendiz a un instructor en un periodo
export const iniciarEvaluacion = async (idAprendiz, idInstructor, idPeriodo) => {
  const response = await api.post(`${API_URL}/iniciar`, null, {
    params: { id_aprendiz: idAprendiz, id_instructor: idInstructor, id_periodo: idPeriodo }
  });
  return response.data;
};

export const actualizarEvaluacion = async (id, datos) => {
  const response = await api.put(`${API_URL}/${id}`, datos);
  return response.data;
};

export const actualizarEstadoEvaluacion = async (id, estado) => {
  const response = await api.put(`${API_URL}/${id}/estado`, null, {
    params: { estado }
  });
  return response.data;
};

export const eliminarEvaluacion = async (id) => {
  const response = await api.delete(`${API_URL}/${id}`);
  return response.data;
};
