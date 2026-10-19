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

export const reportePreguntasInstructor = async (instructorId, params = {}) => {
  const response = await api.get(
    `${API_URL}/instructor/${instructorId}/preguntas`,
    { params }
  );
  return response.data;
};

/** Promedio del instructor. params: { periodo_id?: number } */
export const miPromedioInstructor = async (instructorId, params = {}) => {
  const response = await api.get(`${API_URL}/mi-promedio`, {
    params: { instructor_id: instructorId, ...params },
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

/** Evaluaciones recibidas (anónimas). params: { periodo_id?: number } */
export const misEvaluacionesInstructor = async (instructorId, params = {}) => {
  const response = await api.get(`${API_URL}/mis-evaluaciones`, {
    params: { instructor_id: instructorId, ...params },
  });
  return response.data;
};

export const detalleEvaluacion = async (evaluacionId) => {
  const response = await api.get(
    `${API_URL}/evaluacion/${evaluacionId}/detalle`
  );
  return response.data;
};

/** Aprendices con instructores pendientes de evaluar */
export const listarPendientesEvaluacion = async (params = {}) => {
  const response = await api.get(`${API_URL}/pendientes-evaluacion`, { params });
  return response.data;
};

/** Instructores sin foto de perfil */
export const listarInstructoresSinFoto = async () => {
  const response = await api.get(`${API_URL}/instructores-sin-foto`);
  return response.data;
};

/** Envía recordatorio 24h a aprendices pendientes */
export const enviarRecordatorioPendientes = async (params = {}) => {
  const response = await api.post(`${API_URL}/enviar-recordatorio-pendientes`, null, {
    params,
  });
  return response.data;
};

/** Envía advertencia a instructores sin foto */
export const enviarAdvertenciaSinFoto = async () => {
  const response = await api.post(`${API_URL}/enviar-advertencia-sin-foto`);
  return response.data;
};

/** Descarga Excel de pendientes (blob) */
export const descargarPendientesExcel = async (params = {}) => {
  const response = await api.get(`${API_URL}/exportar-pendientes-excel`, {
    params,
    responseType: "blob",
  });
  return response.data;
};

/** Descarga Excel de instructores sin foto (blob) */
export const descargarSinFotoExcel = async () => {
  const response = await api.get(`${API_URL}/exportar-sin-foto-excel`, {
    responseType: "blob",
  });
  return response.data;
};
