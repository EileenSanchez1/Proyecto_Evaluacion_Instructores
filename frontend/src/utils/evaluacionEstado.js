/** Estados que cierran una evaluación (no se puede volver a responder). */
const CERRADOS = new Set([
  "evaluado",
  "completada",
  "completado",
  "finalizada",
  "finalizado",
  "enviada",
  "enviado",
  "respondida",
  "respondido",
]);

export function esEvaluacionCerrada(estado) {
  return CERRADOS.has(String(estado || "").trim().toLowerCase());
}

export function etiquetaEstado(estado) {
  if (esEvaluacionCerrada(estado)) return "Evaluado";
  return "Pendiente";
}

/** Extrae mensaje legible de errores Axios / FastAPI. */
export function mensajeErrorApi(err, fallback = "Ocurrió un error. Intenta de nuevo.") {
  const detail = err?.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((d) => (typeof d === "string" ? d : d?.msg || JSON.stringify(d)))
      .join(" ");
  }
  if (detail && typeof detail === "object" && detail.msg) return detail.msg;
  return err?.message || fallback;
}
