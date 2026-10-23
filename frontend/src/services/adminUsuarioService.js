import api from "../api/axiosConfig";

const API = "/admin-usuarios";

export const listarAdministradores = async () => {
  const res = await api.get(`${API}/administradores`);
  return res.data;
};

/** Invita o promueve a Administrador por correo */
export const promoverAdministrador = async ({ correo, nombre, apellido }) => {
  const res = await api.post(`${API}/promover`, {
    correo,
    nombre: nombre || null,
    apellido: apellido || null,
  });
  return res.data;
};

export const desactivarAdministrador = async (idUsuario) => {
  const res = await api.post(`${API}/${idUsuario}/desactivar`);
  return res.data;
};

export const reactivarAdministrador = async (idUsuario) => {
  const res = await api.post(`${API}/${idUsuario}/reactivar`);
  return res.data;
};

export const degradarACoordinador = async (idUsuario) => {
  const res = await api.post(`${API}/${idUsuario}/degradar-coordinador`);
  return res.data;
};
