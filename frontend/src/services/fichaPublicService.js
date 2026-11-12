import axios from "axios";

// Mismo origen de API que el resto del frontend (VITE_API_URL)
const BASE_URL =
  (typeof import.meta !== "undefined" && import.meta.env?.VITE_API_URL) ||
  "http://127.0.0.1:8000";

export const listarFichasPublico = async () => {
  const response = await axios.get(`${BASE_URL}/fichas/`);
  return response.data;
};
