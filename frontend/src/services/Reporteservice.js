import api from "../api/axiosConfig";

const API_URL = "/reportes";

export const generarReporte = async (evaluacionId) => {
  const response = await api.get(`${API_URL}/`, { params: { evaluacion_id: evaluacionId } });
  return response.data;
};

export const generarReporteInstructor = async (evaluacionId, instructorId) => {
  const response = await api.get(`${API_URL}/instructor`, {
    params: { evaluacion_id: evaluacionId, instructor_id: instructorId }
  });
  return response.data;
};

export const reporteDashboard = async (params = {}) => {
  const response = await api.get(`${API_URL}/dashboard`, { params });
  return response.data;
};

export const historialEvaluaciones = async (params = {}) => {
  const response = await api.get(`${API_URL}/historial`, { params });
  return response.data;
};
