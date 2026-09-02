import axios from "axios";

const BASE_URL = "http://127.0.0.1:8000";

export const listarFichasPublico = async () => {
  const response = await axios.get(`${BASE_URL}/fichas/`);
  return response.data;
};
