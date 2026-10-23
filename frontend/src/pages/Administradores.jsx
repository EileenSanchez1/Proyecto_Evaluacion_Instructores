import { useEffect, useState } from "react";
import {
  listarAdministradores,
  promoverAdministrador,
  desactivarAdministrador,
  reactivarAdministrador,
  degradarACoordinador,
} from "../services/adminUsuarioService";
import { obtenerUsuarioSesion } from "../utils/sesion";
import "../styles/Instructores.css";

function Administradores() {
  const yo = obtenerUsuarioSesion();
  const [admins, setAdmins] = useState([]);
  const [activos, setActivos] = useState(0);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [exito, setExito] = useState("");
  const [guardando, setGuardando] = useState(false);
  const [passwordTemporal, setPasswordTemporal] = useState("");

  const [form, setForm] = useState({
    correo: "",
    nombre: "",
    apellido: "",
  });

  const cargar = async () => {
    try {
      setCargando(true);
      setError("");
      const data = await listarAdministradores();
      setAdmins(data?.administradores || []);
      setActivos(data?.activos || 0);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "No se pudo cargar la lista de administradores."
      );
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargar();
  }, []);

  const limpiarMensajes = () => {
    setError("");
    setExito("");
    setPasswordTemporal("");
  };

  const onPromover = async (e) => {
    e.preventDefault();
    limpiarMensajes();
    const correo = form.correo.trim().toLowerCase();
    if (!correo) {
      setError("Ingresa el correo del nuevo administrador.");
      return;
    }
    if (!correo.includes("@")) {
      setError("Correo inválido.");
      return;
    }
    try {
      setGuardando(true);
      const res = await promoverAdministrador({
        correo,
        nombre: form.nombre.trim() || undefined,
        apellido: form.apellido.trim() || undefined,
      });
      setExito(res.mensaje || "Operación exitosa.");
      if (res.password_temporal) {
        setPasswordTemporal(res.password_temporal);
      }
      setForm({ correo: "", nombre: "", apellido: "" });
      await cargar();
    } catch (err) {
      setError(
        err.response?.data?.detail || "No se pudo promover / crear el administrador."
      );
    } finally {
      setGuardando(false);
    }
  };

  const onDesactivar = async (admin) => {
    limpiarMensajes();
    if (
      !window.confirm(
        `¿Desactivar a ${admin.correo}? Ya no podrá iniciar sesión como administrador.`
      )
    ) {
      return;
    }
    try {
      const res = await desactivarAdministrador(admin.id_usuario);
      setExito(res.mensaje || "Administrador desactivado.");
      await cargar();
    } catch (err) {
      setError(err.response?.data?.detail || "No se pudo desactivar.");
    }
  };

  const onReactivar = async (admin) => {
    limpiarMensajes();
    try {
      const res = await reactivarAdministrador(admin.id_usuario);
      setExito(res.mensaje || "Administrador reactivado.");
      await cargar();
    } catch (err) {
      setError(err.response?.data?.detail || "No se pudo reactivar.");
    }
  };

  const onDegradar = async (admin) => {
    limpiarMensajes();
    if (
      !window.confirm(
        `¿Quitar el rol de Administrador a ${admin.correo} y dejarlo como Coordinador?\n\n` +
          "Podrá seguir gestionando fichas e instructores, pero ya no podrá administrar roles."
      )
    ) {
      return;
    }
    try {
      const res = await degradarACoordinador(admin.id_usuario);
      setExito(res.mensaje || "Usuario degradado a Coordinador.");
      await cargar();
    } catch (err) {
      setError(err.response?.data?.detail || "No se pudo degradar.");
    }
  };

  return (
    <div className="pagina-instructores">
      <div className="encabezado">
        <div>
          <h1 className="titulo">
            <i className="bi bi-shield-lock"></i> Gestión de Administradores
          </h1>
          <p className="subtitulo">
            Transfiere el rol de administrador sin tocar la base de datos ni el
            código. Siempre debe quedar al menos un administrador activo.
          </p>
        </div>
      </div>

      {error && (
        <div
          className="alert alert-danger"
          role="alert"
          style={{ marginBottom: 16 }}
        >
          {error}
        </div>
      )}
      {exito && (
        <div
          className="alert alert-success"
          role="alert"
          style={{ marginBottom: 16 }}
        >
          {exito}
        </div>
      )}

      {passwordTemporal && (
        <div
          style={{
            marginBottom: 16,
            padding: "14px 16px",
            borderRadius: 10,
            border: "1px solid #f59e0b",
            background: "#fffbeb",
            color: "#92400e",
          }}
        >
          <strong>Contraseña temporal (solo se muestra una vez):</strong>
          <div
            style={{
              marginTop: 8,
              fontFamily: "monospace",
              fontSize: "1.1rem",
              fontWeight: 700,
              letterSpacing: "0.04em",
            }}
          >
            {passwordTemporal}
          </div>
          <p style={{ margin: "8px 0 0", fontSize: "0.85rem" }}>
            Compártela de forma segura con el nuevo administrador. Debe entrar
            en la pestaña <strong>Soy Admin</strong> y luego podrá usar
            «Recuperar contraseña» si necesita cambiarla.
          </p>
        </div>
      )}

      {/* Formulario invitar / promover */}
      <div
        className="form-inline-card"
        style={{
          marginBottom: "1.5rem",
          padding: "16px 18px",
          border: "1px solid #e5e7eb",
          borderRadius: 12,
          background: "#f9fafb",
        }}
      >
        <h4 style={{ margin: "0 0 6px", fontSize: "1rem" }}>
          <i className="bi bi-person-plus"></i> Invitar o promover administrador
        </h4>
        <p style={{ margin: "0 0 12px", fontSize: "0.85rem", color: "#6b7280" }}>
          Si el correo ya existe en el sistema, se le asigna el rol
          Administrador. Si no existe, se crea la cuenta con una contraseña
          temporal.
        </p>
        <form onSubmit={onPromover}>
          <div
            style={{
              display: "flex",
              flexWrap: "wrap",
              gap: 10,
              alignItems: "flex-end",
            }}
          >
            <div style={{ flex: "1 1 220px" }}>
              <label className="form-label" style={{ fontSize: 13 }}>
                Correo institucional *
              </label>
              <input
                type="email"
                className="form-control form-control-sm"
                placeholder="juanhernandez@sena.edu.co"
                value={form.correo}
                onChange={(e) =>
                  setForm((f) => ({ ...f, correo: e.target.value }))
                }
                required
              />
            </div>
            <div style={{ flex: "1 1 140px" }}>
              <label className="form-label" style={{ fontSize: 13 }}>
                Nombre
              </label>
              <input
                type="text"
                className="form-control form-control-sm"
                placeholder="Juan"
                value={form.nombre}
                onChange={(e) =>
                  setForm((f) => ({ ...f, nombre: e.target.value }))
                }
              />
            </div>
            <div style={{ flex: "1 1 140px" }}>
              <label className="form-label" style={{ fontSize: 13 }}>
                Apellido
              </label>
              <input
                type="text"
                className="form-control form-control-sm"
                placeholder="Hernández"
                value={form.apellido}
                onChange={(e) =>
                  setForm((f) => ({ ...f, apellido: e.target.value }))
                }
              />
            </div>
            <button
              type="submit"
              className="btn btn-success btn-sm"
              disabled={guardando}
              style={{ minWidth: 140 }}
            >
              {guardando ? "Guardando…" : "Promover / Crear"}
            </button>
          </div>
        </form>
      </div>

      <div style={{ marginBottom: 12, color: "#6b7280", fontSize: "0.9rem" }}>
        Administradores activos: <strong>{activos}</strong>
        {yo?.correo && (
          <>
            {" "}
            · Sesión actual: <strong>{yo.correo}</strong>
          </>
        )}
      </div>

      {cargando ? (
        <p className="text-muted">Cargando…</p>
      ) : admins.length === 0 ? (
        <div className="home-vacio">
          <p>No hay administradores registrados.</p>
        </div>
      ) : (
        <div style={{ overflowX: "auto" }}>
          <table
            style={{
              width: "100%",
              borderCollapse: "collapse",
              fontSize: "0.9rem",
              background: "#fff",
              borderRadius: 12,
              overflow: "hidden",
              border: "1px solid #e5e7eb",
            }}
          >
            <thead>
              <tr style={{ background: "#f3f4f6", textAlign: "left" }}>
                <th style={{ padding: "12px 14px" }}>Nombre</th>
                <th style={{ padding: "12px 14px" }}>Correo</th>
                <th style={{ padding: "12px 14px" }}>Estado</th>
                <th style={{ padding: "12px 14px" }}>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {admins.map((a) => {
                const esYo =
                  yo?.correo &&
                  a.correo &&
                  yo.correo.toLowerCase() === a.correo.toLowerCase();
                return (
                  <tr
                    key={a.id_usuario}
                    style={{ borderTop: "1px solid #f3f4f6" }}
                  >
                    <td style={{ padding: "12px 14px", fontWeight: 600 }}>
                      {a.nombre} {a.apellido}
                      {esYo && (
                        <span
                          style={{
                            marginLeft: 8,
                            fontSize: "0.75rem",
                            color: "#0d7377",
                            fontWeight: 600,
                          }}
                        >
                          (tú)
                        </span>
                      )}
                    </td>
                    <td style={{ padding: "12px 14px" }}>{a.correo}</td>
                    <td style={{ padding: "12px 14px" }}>
                      <span
                        style={{
                          display: "inline-block",
                          padding: "4px 10px",
                          borderRadius: 999,
                          fontSize: "0.78rem",
                          fontWeight: 700,
                          background: a.activo ? "#d1fae5" : "#f3f4f6",
                          color: a.activo ? "#065f46" : "#6b7280",
                        }}
                      >
                        {a.activo ? "Activo" : "Inactivo"}
                      </span>
                    </td>
                    <td style={{ padding: "12px 14px" }}>
                      <div
                        style={{
                          display: "flex",
                          flexWrap: "wrap",
                          gap: 6,
                        }}
                      >
                        {a.activo ? (
                          <>
                            <button
                              type="button"
                              className="btn btn-sm btn-outline-danger"
                              onClick={() => onDesactivar(a)}
                              title="Desactivar"
                            >
                              Desactivar
                            </button>
                            <button
                              type="button"
                              className="btn btn-sm btn-outline-secondary"
                              onClick={() => onDegradar(a)}
                              title="Dejar como Coordinador"
                            >
                              → Coordinador
                            </button>
                          </>
                        ) : (
                          <button
                            type="button"
                            className="btn btn-sm btn-outline-success"
                            onClick={() => onReactivar(a)}
                          >
                            Reactivar
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      <p
        style={{
          marginTop: 20,
          fontSize: "0.82rem",
          color: "#6b7280",
          maxWidth: 720,
        }}
      >
        <strong>Cómo transferir el admin cuando alguien se va:</strong> el
        administrador actual invita el correo del nuevo (ej.{" "}
        <code>juanhernandez@sena.edu.co</code>), verifica que pueda entrar y
        luego desactiva o degrada a Coordinador la cuenta anterior. Nadie
        necesita editar la base de datos.
      </p>
    </div>
  );
}

export default Administradores;
