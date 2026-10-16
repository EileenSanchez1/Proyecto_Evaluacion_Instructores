/**
 * Resuelve el periodo operativo del aprendiz:
 * - Preferir su id_periodo si sigue Activo Y tiene instructores asignados
 * - Si no, el primer periodo Activo que tenga instructores en su ficha
 * - Fallback: listar todas las asignaciones activas de la ficha y filtrar por periodos activos
 * - Si no hay asignaciones, el primer periodo Activo (para mostrar mensaje)
 */
import { listarPeriodosActivos } from "../services/PeriodoService";
import {
  listarInstructoresPorFicha,
  listarInstructoresPorFichaYPeriodo,
} from "../services/Fichainstructorservice";

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

  const idsActivos = new Set(activos.map((p) => Number(p.id_periodo)));
  const porId = (id) => activos.find((p) => Number(p.id_periodo) === Number(id));

  // 1) Periodo de registro si está activo Y tiene asignaciones
  const registrado = idPeriodoRegistrado ? porId(idPeriodoRegistrado) : null;
  if (registrado) {
    const asignaciones = await listarInstructoresPorFichaYPeriodo(
      idFicha,
      registrado.id_periodo
    ).catch(() => []);
    if (asignaciones && asignaciones.length > 0) {
      return {
        periodo: registrado,
        asignaciones,
        sinPeriodoActivo: false,
        mensaje: null,
      };
    }
    // Si el periodo de registro está activo pero sin asignaciones,
    // seguir buscando otros periodos activos con instructores.
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

  // 3) Fallback: todas las asignaciones activas de la ficha, filtradas por periodo activo
  try {
    const todas = await listarInstructoresPorFicha(idFicha);
    const enPeriodoActivo = (todas || []).filter(
      (a) =>
        a &&
        a.activo !== false &&
        a.activo !== 0 &&
        idsActivos.has(Number(a.id_periodo))
    );
    if (enPeriodoActivo.length > 0) {
      const idPeriodoPreferido = Number(enPeriodoActivo[0].id_periodo);
      const periodo = porId(idPeriodoPreferido) || activos[0];
      const delPeriodo = enPeriodoActivo.filter(
        (a) => Number(a.id_periodo) === idPeriodoPreferido
      );
      return {
        periodo,
        asignaciones: delPeriodo,
        sinPeriodoActivo: false,
        mensaje: null,
      };
    }
  } catch (e) {
    console.error("Fallback listarInstructoresPorFicha falló", e);
  }

  // 4) Activo sin asignaciones aún
  return {
    periodo: activos[0],
    asignaciones: [],
    sinPeriodoActivo: false,
    mensaje: null,
  };
}
