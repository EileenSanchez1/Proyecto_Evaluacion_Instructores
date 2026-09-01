import api from "../api/axiosConfig";

export const listarPeriodos = async () => {
  const response = await api.get("/periodos/");
  return response.data;
};

export const listarPeriodosActivos = async () => {
  const response = await api.get("/periodos/activos");
  return response.data;
};

export const crearPeriodo = async (datos) => {
  const response = await api.post("/periodos/", datos);
  return response.data;
};

export const actualizarPeriodo = async (id, datos) => {
  const response = await api.put(`/periodos/${id}`, datos);
  return response.data;
};

export const eliminarPeriodo = async (id) => {
  const response = await api.delete(`/periodos/${id}`);
  return response.data;
};
