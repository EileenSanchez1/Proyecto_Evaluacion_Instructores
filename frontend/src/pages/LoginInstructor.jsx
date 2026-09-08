import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  loginInstructorPaso1,
  verificarCodigoInstructor,
} from "../services/authService";
import "../styles/Login.css";

function LoginInstructor() {
  const [correo, setCorreo] = useState("");
  const [contrasena, setContrasena] = useState("");
  const [codigo, setCodigo] = useState("");
  const [paso, setPaso] = useState(1); // 1: credenciales, 2: código
  const [mostrarPass, setMostrarPass] = useState(false);
  const [mensaje, setMensaje] = useState("");
  const [esError, setEsError] = useState(false);
  const [cargando, setCargando] = useState(false);

  const navigate = useNavigate();

  const handlePaso1 = async (e) => {
    e.preventDefault();
    setMensaje("");
    setEsError(false);

    if (!correo.endsWith("@sena.edu.co")) {
      setEsError(true);
      setMensaje("El correo debe ser institucional (@sena.edu.co).");
      return;
    }

    try {
      setCargando(true);
      await loginInstructorPaso1({ correo, contrasena });
      setPaso(2);
      setEsError(false);
      setMensaje("Código enviado a tu correo. Revisa tu bandeja.");
    } catch (error) {
      setEsError(true);
      setMensaje(
        error.response?.data?.detail || "Error al iniciar sesión."
      );
    } finally {
      setCargando(false);
    }
  };

  const handlePaso2 = async (e) => {
    e.preventDefault();
    setMensaje("");
    setEsError(false);

    try {
      setCargando(true);
      const respuesta = await verificarCodigoInstructor({
        correo,
        codigo,
      });

      localStorage.setItem("token", respuesta.access_token);
      localStorage.setItem("usuario", JSON.stringify(respuesta.usuario));

      setMensaje("Inicio de sesión exitoso");
      setTimeout(() => navigate("/"), 500);
    } catch (error) {
      setEsError(true);
      setMensaje(error.response?.data?.detail || "Código inválido.");
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="contenedor-login">
      <div className="tarjeta-login">
        <div className="lado-imagen">
          <img
            src="/imgs/logo-sena.png"
            alt="Logo SENA"
            className="logo-sena"
          />
          <h2>Acceso Instructor</h2>
          <p>Plataforma de evaluación SENA</p>
        </div>

        <div className="lado-formulario">
          <h1>Soy Instructor</h1>
          <p className="subtitulo">
            Ingresa con tu correo institucional
          </p>

          {mensaje && (
            <div className={`mensaje-login ${esError ? "error" : "exito"}`}>
              {mensaje}
            </div>
          )}

          {paso === 1 ? (
            <form onSubmit={handlePaso1}>
              <div>
                <label>Correo institucional</label>
                <input
                  type="email"
                  placeholder="tu.correo@sena.edu.co"
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
                    className="toggle-password"
                    onClick={() => setMostrarPass(!mostrarPass)}
                  >
                    {mostrarPass ? "🙈" : "👁️"}
                  </button>
                </div>
              </div>

              <button type="submit" disabled={cargando}>
                {cargando ? "Verificando..." : "Enviar código"}
              </button>
            </form>
          ) : (
            <form onSubmit={handlePaso2}>
              <div>
                <label>Código de verificación</label>
                <input
                  type="text"
                  placeholder="123456"
                  value={codigo}
                  onChange={(e) => setCodigo(e.target.value)}
                  maxLength={6}
                  required
                />
              </div>
              <button type="submit" disabled={cargando}>
                {cargando ? "Verificando..." : "Verificar e ingresar"}
              </button>
              <button
                type="button"
                className="btn-secundario"
                onClick={() => setPaso(1)}
              >
                Volver
              </button>
            </form>
          )}

          <div className="registro-link">
            <p>
              <Link to="/login">← Volver al login principal</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LoginInstructor;