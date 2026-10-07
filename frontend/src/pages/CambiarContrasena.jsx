import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { cambiarPassword } from "../services/authService";
import "../styles/Login.css";
import "../styles/Estructura.css";

function validarContrasenaSegura(contrasena) {
  if (contrasena.length < 8) return "La contraseña debe tener al menos 8 caracteres.";
  if (!/[A-Z]/.test(contrasena)) return "Debe contener al menos una mayúscula.";
  if (!/[a-z]/.test(contrasena)) return "Debe contener al menos una minúscula.";
  if (!/\d/.test(contrasena)) return "Debe contener al menos un número.";
  if (!/[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/.test(contrasena))
    return "Debe contener al menos un carácter especial (!@#$%^&* etc.).";
  return null;
}

function CambiarContrasena() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    contrasena_actual: "",
    nueva_contrasena: "",
    confirmar: "",
  });
  const [mostrar, setMostrar] = useState({ a: false, n: false, c: false });
  const [mensaje, setMensaje] = useState("");
  const [esError, setEsError] = useState(false);
  const [cargando, setCargando] = useState(false);

  const onChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMensaje("");
    setEsError(false);

    const err = validarContrasenaSegura(form.nueva_contrasena);
    if (err) {
      setEsError(true);
      setMensaje(err);
      return;
    }
    if (form.nueva_contrasena !== form.confirmar) {
      setEsError(true);
      setMensaje("La confirmación no coincide con la nueva contraseña.");
      return;
    }

    setCargando(true);
    try {
      await cambiarPassword({
        contrasena_actual: form.contrasena_actual,
        nueva_contrasena: form.nueva_contrasena,
      });
      setMensaje("Contraseña actualizada. Ya puedes usarla en el próximo ingreso.");
      setEsError(false);
      setForm({ contrasena_actual: "", nueva_contrasena: "", confirmar: "" });
      setTimeout(() => navigate("/"), 1500);
    } catch (error) {
      setEsError(true);
      setMensaje(
        error.response?.data?.detail || "No se pudo cambiar la contraseña."
      );
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="pagina-estructura">
      <div className="encabezado">
        <div>
          <h1 className="titulo">Cambiar contraseña</h1>
          <p className="subtitulo">
            Tras el primer acceso con la contraseña temporal del correo, define una
            contraseña propia y segura.
          </p>
        </div>
      </div>

      <div className="form-inline-card" style={{ maxWidth: 480 }}>
        {mensaje && (
          <div className={`mensaje-login ${esError ? "error" : "exito"}`}>
            {mensaje}
          </div>
        )}
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: 12 }}>
            <label>Contraseña actual (la del correo)</label>
            <div className="password-input-wrapper">
              <input
                type={mostrar.a ? "text" : "password"}
                name="contrasena_actual"
                value={form.contrasena_actual}
                onChange={onChange}
                required
              />
              <button
                type="button"
                className="btn-ojito"
                onClick={() => setMostrar({ ...mostrar, a: !mostrar.a })}
              >
                <i className={`bi ${mostrar.a ? "bi-eye-slash" : "bi-eye"}`}></i>
              </button>
            </div>
          </div>
          <div style={{ marginBottom: 12 }}>
            <label>Nueva contraseña</label>
            <div className="password-input-wrapper">
              <input
                type={mostrar.n ? "text" : "password"}
                name="nueva_contrasena"
                value={form.nueva_contrasena}
                onChange={onChange}
                required
              />
              <button
                type="button"
                className="btn-ojito"
                onClick={() => setMostrar({ ...mostrar, n: !mostrar.n })}
              >
                <i className={`bi ${mostrar.n ? "bi-eye-slash" : "bi-eye"}`}></i>
              </button>
            </div>
            <small className="hint-pass">
              Mín. 8 caracteres, mayúscula, minúscula, número y carácter especial.
            </small>
          </div>
          <div style={{ marginBottom: 16 }}>
            <label>Confirmar nueva contraseña</label>
            <div className="password-input-wrapper">
              <input
                type={mostrar.c ? "text" : "password"}
                name="confirmar"
                value={form.confirmar}
                onChange={onChange}
                required
              />
              <button
                type="button"
                className="btn-ojito"
                onClick={() => setMostrar({ ...mostrar, c: !mostrar.c })}
              >
                <i className={`bi ${mostrar.c ? "bi-eye-slash" : "bi-eye"}`}></i>
              </button>
            </div>
          </div>
          <button type="submit" className="btn-submit-form" disabled={cargando}>
            {cargando ? "Guardando..." : "Guardar nueva contraseña"}
          </button>
        </form>
      </div>
    </div>
  );
}

export default CambiarContrasena;
