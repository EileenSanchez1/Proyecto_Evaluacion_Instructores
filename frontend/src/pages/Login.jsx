import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { login } from "../services/authService";
import "../styles/Login.css";

function Login() {
  const [correo, setCorreo] = useState("");
  const [contrasena, setContrasena] = useState("");
  const [mostrarPass, setMostrarPass] = useState(false);
  const [mensaje, setMensaje] = useState("");
  const [esError, setEsError] = useState(false);
  const [cargando, setCargando] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMensaje("");
    setEsError(false);

    if (!correo.trim() || !contrasena) {
      setEsError(true);
      setMensaje("Ingresa correo y contraseña.");
      return;
    }

    setCargando(true);
    try {
      const respuesta = await login({ correo: correo.trim(), contrasena });
      localStorage.setItem("token", respuesta.access_token);
      localStorage.setItem("usuario", JSON.stringify(respuesta.usuario));
      setMensaje("Inicio de sesión exitoso");
      setTimeout(() => navigate("/"), 400);
    } catch (error) {
      setEsError(true);
      setMensaje(
        error.response?.data?.detail || "Correo o contraseña incorrectos"
      );
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="contenedor-login">
      <div className="tarjeta-login">
        <div className="lado-imagen">
          <img src="/imgs/logo-sena.png" alt="Logo SENA" className="logo-sena" />
          <h2>Bienvenido/a</h2>
          <p>Plataforma de acceso</p>
        </div>

        <div className="lado-formulario">
          <h1>Login</h1>
          <p className="subtitulo">
            Usa el correo y la contraseña que te enviaron al inicio del periodo.
          </p>

          {mensaje && (
            <div className={`mensaje-login ${esError ? "error" : "exito"}`}>
              {mensaje}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div>
              <label>Correo</label>
              <input
                type="email"
                placeholder="Ingrese su correo"
                value={correo}
                onChange={(e) => setCorreo(e.target.value)}
                required
              />
            </div>

            <div className="password-field">
              <label>Contraseña</label>
              <div className="password-input-wrapper">
                <input
                  type={mostrarPass ? "text" : "password"}
                  placeholder="Ingrese su contraseña"
                  value={contrasena}
                  onChange={(e) => setContrasena(e.target.value)}
                  required
                />
                <button
                  type="button"
                  className="btn-ojito"
                  onClick={() => setMostrarPass(!mostrarPass)}
                  title={mostrarPass ? "Ocultar" : "Mostrar"}
                >
                  <i className={`bi ${mostrarPass ? "bi-eye-slash" : "bi-eye"}`}></i>
                </button>
              </div>
            </div>

            <button type="submit" disabled={cargando}>
              {cargando ? "Ingresando..." : "Ingresar"}
            </button>
          </form>

          <div className="recuperar">
            <Link to="/recuperar-contrasena">¿Olvidaste tu contraseña?</Link>
          </div>

          <div style={{ marginTop: "1.25rem", textAlign: "center" }}>
            <Link
              to="/login-instructor"
              style={{
                display: "inline-block",
                padding: "0.6rem 1.2rem",
                background: "#39a900",
                color: "#fff",
                borderRadius: "8px",
                textDecoration: "none",
                fontWeight: 600,
              }}
            >
              <i className="bi bi-person-workspace"></i> Soy Instructor
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;
