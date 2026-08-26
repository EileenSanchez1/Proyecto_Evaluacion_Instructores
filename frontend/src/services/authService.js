import axios from "axios";

const API_URL = "http://127.0.0.1:8000";

export const login = async (datos) => {
  const respuesta = await axios.post(
    `${API_URL}/login/`,
    datos
  );

  return respuesta.data;
};

export const recuperarContrasena = async (correo, nuevaContrasena) => {
  const respuesta = await axios.post(
    `${API_URL}/login/recuperar`,
    { correo, nueva_contrasena: nuevaContrasena }
  );

  return respuesta.data;
};