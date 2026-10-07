import api from "../api/axiosConfig";

const API_URL = "/aprendices";

export const obtenerAprendiz = async (id) => {
  const response = await api.get(`${API_URL}/${id}`);
  return response.data;
};

export const crearAprendiz = async (datos) => {
  const response = await api.post(`${API_URL}/`, datos);
  return response.data;
};

export const listarAprendices = async () => {
  const response = await api.get(`${API_URL}/`);
  return response.data;
};

export const listarAprendicesPorFicha = async (idFicha) => {
  const response = await api.get(`${API_URL}/por-ficha/${idFicha}`);
  return response.data;
};

export const actualizarAprendiz = async (id, datos) => {
  const response = await api.put(`${API_URL}/${id}`, datos);
  return response.data;
};

export const desactivarAprendiz = async (id) => {
  const response = await api.post(`${API_URL}/${id}/desactivar`);
  return response.data;
};

export const reactivarAprendiz = async (id) => {
  const response = await api.post(`${API_URL}/${id}/reactivar`);
  return response.data;
};

/**
 * Carga masiva desde CSV (coordinación).
 * FormData: archivo, id_periodo (opcional), enviar_correo (true/false)
 */
export const cargaMasivaAprendices = async (formData) => {
  const response = await api.post(`${API_URL}/carga-masiva`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};

export const reenviarCorreosFicha = async (idFicha) => {
  const response = await api.post(`${API_URL}/por-ficha/${idFicha}/reenviar-correos`);
  return response.data;
};
