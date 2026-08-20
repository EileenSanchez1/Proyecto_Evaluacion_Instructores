import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../services/authService";

function Login() {
  const [correo, setCorreo] = useState("");
  const [contrasena, setContrasena] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [cargando, setCargando] = useState(false);

  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    setMensaje("");
    setCargando(true);

    try {
      const datos = {
        correo,
        contrasena,
      };

     console.log("Datos enviados:", datos);
      const respuesta = await login(datos);

      console.log("Respuesta del backend:", respuesta);

      // Guardar la sesión del usuario
      localStorage.setItem("usuario", JSON.stringify(respuesta));

      setMensaje("Inicio de sesión exitoso");

      // Ir al sistema después de iniciar sesión
      setTimeout(() => {
        navigate("/");
      }, 500);

    } catch (error) {
      console.error("Error en login:", error);

      if (error.response) {
        setMensaje(
          error.response.data?.detail ||
          "Correo o contraseña incorrectos"
        );
      } else {
        setMensaje("No se pudo conectar con el servidor");
      }
    } finally {
      setCargando(false);
    }
  };

  return (
    <div>
      <h1>Iniciar sesión</h1>

      <form onSubmit={handleSubmit}>
        <div>
          <label>Correo</label>

          <input
            type="email"
            value={correo}
            onChange={(e) => setCorreo(e.target.value)}
            required
          />
        </div>

        <div>
          <label>Contraseña</label>

          <input
            type="password"
            value={contrasena}
            onChange={(e) => setContrasena(e.target.value)}
            required
          />
        </div>

        <button type="submit" disabled={cargando}>
          {cargando ? "Ingresando..." : "Iniciar sesión"}
        </button>
      </form>

      {mensaje && <p>{mensaje}</p>}
    </div>
  );
}

export default Login;