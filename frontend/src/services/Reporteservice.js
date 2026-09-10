import api from "../api/axiosConfig";

const API_URL = "/reportes";

export const generarReporte = async (evaluacionId) => {
  const response = await api.get(`${API_URL}/`, {
    params: { evaluacion_id: evaluacionId },
  });
  return response.data;
};

export const generarReporteInstructor = async (evaluacionId, instructorId) => {
  const response = await api.get(`${API_URL}/instructor`, {
    params: { evaluacion_id: evaluacionId, instructor_id: instructorId },
  });
  return response.data;
};

/**
 * Desempeño por pregunta de un instructor.
 * Usado por Admin (Reportes) e Instructor (Mi Promedio).
 */
export const reportePreguntasInstructor = async (instructorId, params = {}) => {
  const response = await api.get(
    `${API_URL}/instructor/${instructorId}/preguntas`,
    { params }
  );
  return response.data;
};

/** Atajo para el instructor logueado */
export const miPromedioInstructor = async (instructorId) => {
  const response = await api.get(`${API_URL}/mi-promedio`, {
    params: { instructor_id: instructorId },
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

/** Evaluaciones recibidas por el instructor (anónimas: ficha, fecha, estado, programa) */
export const misEvaluacionesInstructor = async (instructorId) => {
  const response = await api.get(`${API_URL}/mis-evaluaciones`, {
    params: { instructor_id: instructorId },
  });
  return response.data;
};
