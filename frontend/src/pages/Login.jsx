import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { login } from "../services/authService";
import "../styles/Login.css";

function Login() {
  const [correo, setCorreo] = useState("");
  const [contrasena, setContrasena] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [esError, setEsError] = useState(false);
  const [cargando, setCargando] = useState(false);

  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    setMensaje("");
    setEsError(false);
    setCargando(true);

    try {
      const datos = { correo, contrasena };
      const respuesta = await login(datos);

      // Guardar la sesión del usuario
      localStorage.setItem("usuario", JSON.stringify(respuesta));

      setMensaje("Inicio de sesión exitoso");

      // Ir al sistema después de iniciar sesión
      setTimeout(() => {
        navigate("/");
      }, 500);
    } catch (error) {
      console.error("Error en login:", error);
      setEsError(true);

      if (error.response) {
        setMensaje(
          error.response.data?.detail || "Correo o contraseña incorrectos"
        );
      } else {
        setMensaje("No se pudo conectar con el servidor");
      }
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
          <p className="subtitulo">Ingresa tus credenciales para continuar</p>

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

            <div>
              <label>Contraseña</label>
              <input
                type="password"
                placeholder="Ingrese su contraseña"
                value={contrasena}
                onChange={(e) => setContrasena(e.target.value)}
                required
              />
            </div>

            <button type="submit" disabled={cargando}>
              {cargando ? "Ingresando..." : "Ingresar"}
            </button>
          </form>

          <div className="registro-link">
            <p>
              ¿No tienes una cuenta?{" "}
              <Link to="/registro">Regístrate aquí</Link>
            </p>
          </div>

          <div className="recuperar">
            <Link to="/recuperar-contrasena">¿Olvidaste tu contraseña?</Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;
