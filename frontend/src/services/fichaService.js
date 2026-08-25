import axios from "axios";

const API_URL = "http://localhost:8000/fichas";

export const listarFichas = async (offset = 0, limit = 100) => {
  const response = await axios.get(API_URL, {
    params: { offset, limit },
  });
  return response.data;
};

export const obtenerFicha = async (id) => {
  const response = await axios.get(`${API_URL}/${id}`);
  return response.data;
};