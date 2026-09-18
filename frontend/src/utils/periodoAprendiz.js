/**
 * Resuelve el periodo operativo del aprendiz:
 * - Preferir su id_periodo si sigue Activo
 * - Si no, el primer periodo Activo que tenga instructores en su ficha
 * - Si no hay asignaciones, el primer periodo Activo (para mostrar mensaje)
 */
import { listarPeriodosActivos } from "../services/PeriodoService";
import { listarInstructoresPorFichaYPeriodo } from "../services/Fichainstructorservice";

export async function resolverPeriodoOperativoAprendiz(idFicha, idPeriodoRegistrado) {
  const activos = await listarPeriodosActivos().catch(() => []);
  if (!activos || activos.length === 0) {
    return {
      periodo: null,
      asignaciones: [],
      sinPeriodoActivo: true,
      mensaje:
        "No hay un periodo de evaluación activo. Cuando el administrador active el periodo vigente podrás evaluar instructores.",
    };
  }

  const porId = (id) => activos.find((p) => Number(p.id_periodo) === Number(id));

  // 1) Periodo de registro si está activo
  const registrado = idPeriodoRegistrado ? porId(idPeriodoRegistrado) : null;
  if (registrado) {
    const asignaciones = await listarInstructoresPorFichaYPeriodo(
      idFicha,
      registrado.id_periodo
    ).catch(() => []);
    return {
      periodo: registrado,
      asignaciones: asignaciones || [],
      sinPeriodoActivo: false,
      mensaje: null,
    };
  }

  // 2) Cualquier activo con instructores en la ficha
  for (const p of activos) {
    const asignaciones = await listarInstructoresPorFichaYPeriodo(
      idFicha,
      p.id_periodo
    ).catch(() => []);
    if (asignaciones && asignaciones.length > 0) {
      return {
        periodo: p,
        asignaciones,
        sinPeriodoActivo: false,
        mensaje: null,
      };
    }
  }

  // 3) Activo sin asignaciones aún
  return {
    periodo: activos[0],
    asignaciones: [],
    sinPeriodoActivo: false,
    mensaje: null,
  };
}
