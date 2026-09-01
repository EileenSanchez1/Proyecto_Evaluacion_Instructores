import api from "../api/axiosConfig";

export const listarNotificaciones = async () => {
  const response = await api.get("/notificaciones/");
  return response.data;
};

export const marcarNotificacionLeida = async (id) => {
  const response = await api.patch(`/notificaciones/${id}/leer`);
  return response.data;
};

export const contarNoLeidas = async () => {
  const response = await api.get("/notificaciones/no-leidas/count");
  return response.data;
};
