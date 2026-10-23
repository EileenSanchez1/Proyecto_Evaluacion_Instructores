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
 * Carga masiva. Por defecto NO envía correos (enviar_correo=false en backend).
 * FormData: archivo, id_periodo (opcional), id_ficha (opcional)
 */
export const cargaMasivaAprendices = async (formData) => {
  if (!formData.has("enviar_correo")) {
    formData.append("enviar_correo", "false");
  }
  const response = await api.post(`${API_URL}/carga-masiva`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};

/** Enviar correos de la ficha (solo activos y pendientes por defecto) */
export const reenviarCorreosFicha = async (idFicha, params = {}) => {
  const response = await api.post(
    `${API_URL}/por-ficha/${idFicha}/reenviar-correos`,
    null,
    { params }
  );
  return response.data;
};

/** Enviar correo solo a un aprendiz */
export const reenviarCorreoAprendiz = async (idFicha, idAprendiz) => {
  const response = await api.post(
    `${API_URL}/por-ficha/${idFicha}/reenviar-correos`,
    null,
    { params: { id_aprendiz: idAprendiz } }
  );
  return response.data;
};
