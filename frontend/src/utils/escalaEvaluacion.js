/**
 * Escala oficial de evaluación de instructores SENA (3 opciones).
 * En BD se guarda como entero: 5 = Siempre, 3 = Algunas veces, 1 = Nunca.
 * Porcentaje oficial (coordinación): Siempre=100%, Algunas veces=50%, Nunca=0%.
 */

export const OPCIONES_ESCALA = [
  { valor: 5, etiqueta: "Siempre", porcentaje: 100 },
  { valor: 3, etiqueta: "Algunas veces", porcentaje: 50 },
  { valor: 1, etiqueta: "Nunca", porcentaje: 0 },
];

/** Convierte valor numérico (5|3|1 u otros) a etiqueta legible */
export function etiquetaDesdeValor(valor) {
  const v = Number(valor);
  if (v >= 4.5) return "Siempre";
  if (v >= 2.5) return "Algunas veces";
  if (v > 0) return "Nunca";
  return "Sin respuesta";
}

/**
 * Porcentaje 0–100 a partir del valor guardado (5/3/1).
 * Siempre→100, Algunas veces→50, Nunca→0.
 */
export function porcentajeDesdeValor(valor) {
  const v = Number(valor);
  if (!v || v <= 0) return 0;
  if (v > 5) return Math.min(100, Math.round(v));
  if (v >= 5) return 100;
  if (v >= 3) return 50;
  return 0;
}

/**
 * Texto para una respuesta individual en detalle de evaluación.
 * Ej: "Siempre · 100%"
 */
export function formatearRespuesta(valor) {
  const etiqueta = etiquetaDesdeValor(valor);
  const pct = porcentajeDesdeValor(valor);
  if (etiqueta === "Sin respuesta") return "Sin respuesta";
  return `${etiqueta} · ${pct}%`;
}

/**
 * Promedio numérico interno (1–5, opciones 5/3/1)
 * → porcentaje oficial: (promedio - 1) / 4 * 100
 *  → 5→100%, 3→50%, 1→0%
 */
export function porcentajeDesdePromedio(promedio) {
  const p = Number(promedio);
  if (p == null || Number.isNaN(p) || p <= 0) return 0;
  if (p > 5) return Math.min(100, Math.round(p));
  return Math.round(((p - 1) / 4) * 100);
}

/** Descripción cualitativa del promedio (para resúmenes) */
export function interpretacionPromedio(promedio) {
  const p = Number(promedio);
  if (!p || p <= 0) return "Sin datos";
  const pct = porcentajeDesdePromedio(p);
  if (pct >= 80) return "Desempeño excelente (predominio de «Siempre»)";
  if (pct >= 50) return "Desempeño regular (mezcla de respuestas)";
  return "Desempeño a mejorar (predominio de «Nunca» o «Algunas veces»)";
}

/** Color de apoyo según porcentaje */
export function colorDesdePorcentaje(porcentaje) {
  const p = Number(porcentaje);
  if (p >= 80) return { clave: "verde", fondo: "#d1fae5", texto: "#065f46", borde: "#a7f3d0" };
  if (p >= 50) return { clave: "amarillo", fondo: "#fef3c7", texto: "#92400e", borde: "#fde68a" };
  return { clave: "rojo", fondo: "#fee2e2", texto: "#991b1b", borde: "#fecaca" };
}
