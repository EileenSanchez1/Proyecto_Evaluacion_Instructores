import api from "../api/axiosConfig";

const API_URL = "/preguntas";

export const listarPreguntas = async () => {
  const response = await api.get(API_URL);
  return response.data;
};

// Solo las preguntas habilitadas para responder (estado = true)
export const listarPreguntasActivas = async () => {
  const response = await api.get(`${API_URL}/activas`);
  return response.data;
};

export const obtenerPregunta = async (id) => {
  const response = await api.get(`${API_URL}/${id}`);
  return response.data;
};

export const crearPregunta = async (datos) => {
  const response = await api.post(`${API_URL}/`, datos);
  return response.data;
};

export const actualizarPregunta = async (id, datos) => {
  const response = await api.put(`${API_URL}/${id}`, datos);
  return response.data;
};

export const eliminarPregunta = async (id) => {
  const response = await api.delete(`${API_URL}/${id}`);
  return response.data;
};

/** Carga las 19 preguntas del formato oficial SENA (evaluación en aula) */
export const cargarPreguntasOficiales = async (reemplazar = false) => {
  const response = await api.post(`${API_URL}/cargar-oficiales`, null, {
    params: { reemplazar },
  });
  return response.data;
};
