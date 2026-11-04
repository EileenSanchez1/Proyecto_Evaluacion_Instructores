/**
 * Construye la URL absoluta de un recurso de media (foto, uploads).
 * Usa VITE_API_URL si está definido; si no, el mismo origen del API (axios baseURL).
 * Así las fotos se ven en cualquier PC que apunte al mismo backend de red.
 */
import api from "../api/axiosConfig";

export function mediaUrl(ruta) {
  if (!ruta) return "";
  if (typeof ruta === "string" && (ruta.startsWith("http://") || ruta.startsWith("https://") || ruta.startsWith("data:"))) {
    return ruta;
  }
  const base =
    (typeof import.meta !== "undefined" && import.meta.env?.VITE_API_URL) ||
    api?.defaults?.baseURL ||
    "http://127.0.0.1:8000";
  const path = ruta.startsWith("/") ? ruta : `/${ruta}`;
  return `${String(base).replace(/\/$/, "")}${path}`;
}

export default mediaUrl;
