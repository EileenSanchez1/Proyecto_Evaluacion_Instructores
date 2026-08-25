import axios from "axios";

// Poner sin la barra al final
const API_URL = "http://localhost:8000/reportes";

export const obtenerReporteEvaluacion = async (evaluacionId) => {
  const response = await axios.get(API_URL, {
    params: { evaluacion_id: evaluacionId },
  });
  return response.data;
};

export const obtenerReportePorInstructor = async (evaluacionId, instructorId) => {
  const response = await axios.get(`${API_URL}/instructor`, {
    params: {
      evaluacion_id: evaluacionId,
      instructor_id: instructorId,
    },
  });
  return response.data;
};