import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { crearAprendiz } from "../services/Aprendizservice";
import { listarFichasPublico } from "../services/fichaPublicService";
import "../styles/Login.css";

function Registro() {
  const navigate = useNavigate();

  const [fichas, setFichas] = useState([]);
  const [cargandoFichas, setCargandoFichas] = useState(true);
  const [errorFichas, setErrorFichas] = useState("");

  const [formulario, setFormulario] = useState({
    nombre: "",
    apellido: "",
    correo: "",
    contrasena: "",
    confirmarContrasena: "",
    id_ficha: "",
  });

  const [mensaje, setMensaje] = useState("");
  const [esError, setEsError] = useState(false);
  const [cargando, setCargando] = useState(false);

  useEffect(() => {
    const cargarFichas = async () => {
      try {
        setCargandoFichas(true);
        setErrorFichas("");
        const datos = await listarFichasPublico();
        setFichas(datos);
        if (datos.length === 0) {
          setErrorFichas("No hay fichas disponibles. Contacta al administrador.");
        }
      } catch (error) {
        console.error("Error al cargar fichas:", error);
        setErrorFichas("No se pudieron cargar las fichas. Verifica que el servidor esté activo.");
      } finally {
        setCargandoFichas(false);
      }
    };

    cargarFichas();
  }, []);

  const manejarCambio = (e) => {
    const { name, value } = e.target;
    setFormulario({ ...formulario, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMensaje("");
    setEsError(false);

    if (
      !formulario.nombre.trim() ||
      !formulario.apellido.trim() ||
      !formulario.correo.trim() ||
      !formulario.contrasena ||
      !formulario.id_ficha
    ) {
      setEsError(true);
      setMensaje("Todos los campos son obligatorios.");
      return;
    }

    if (formulario.contrasena.length < 6) {
      setEsError(true);
      setMensaje("La contraseña debe tener al menos 6 caracteres.");
      return;
    }

    if (formulario.contrasena !== formulario.confirmarContrasena) {
      setEsError(true);
      setMensaje("Las contraseñas no coinciden.");
      return;
    }

    try {
      setCargando(true);

      await crearAprendiz({
        nombre: formulario.nombre.trim(),
        apellido: formulario.apellido.trim(),
        correo: formulario.correo.trim(),
        contrasena: formulario.contrasena,
        id_ficha: Number(formulario.id_ficha),
      });

      setEsError(false);
      setMensaje("Cuenta creada correctamente. Ya puedes iniciar sesión.");

      setTimeout(() => {
        navigate("/login");
      }, 1200);
    } catch (error) {
      console.error("Error en registro:", error);
      setEsError(true);

      const detalle = error.response?.data?.detail;

      if (typeof detalle === "string") {
        setMensaje(detalle);
      } else if (Array.isArray(detalle)) {
        setMensaje(detalle[0]?.msg || "Revisa los datos ingresados.");
      } else {
        setMensaje("No se pudo conectar con el servidor.");
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
          <h2>Únete</h2>
          <p>Crea tu cuenta de aprendiz para evaluar a tus instructores</p>
        </div>

        <div className="lado-formulario">
          <h1>Crear cuenta</h1>
          <p className="subtitulo">Completa tus datos para registrarte</p>

          {mensaje && (
            <div className={`mensaje-login ${esError ? "error" : "exito"}`}>
              {mensaje}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div style={{ display: "flex", gap: "10px" }}>
              <div style={{ flex: 1 }}>
                <label>Nombre</label>
                <input
                  type="text"
                  name="nombre"
                  placeholder="Ej: Juan"
                  value={formulario.nombre}
                  onChange={manejarCambio}
                  required
                />
              </div>
              <div style={{ flex: 1 }}>
                <label>Apellido</label>
                <input
                  type="text"
                  name="apellido"
                  placeholder="Ej: Pérez"
                  value={formulario.apellido}
                  onChange={manejarCambio}
                  required
                />
              </div>
            </div>

            <label>Correo</label>
            <input
              type="email"
              name="correo"
              placeholder="Ingresa tu correo"
              value={formulario.correo}
              onChange={manejarCambio}
              required
            />

            <label>Ficha</label>
            {errorFichas ? (
              <p style={{ color: "#dc3545", fontSize: "0.9rem", marginBottom: 10 }}>
                {errorFichas}
              </p>
            ) : (
              <select
                name="id_ficha"
                value={formulario.id_ficha}
                onChange={manejarCambio}
                required
                disabled={cargandoFichas || fichas.length === 0}
                style={{
                  width: "100%",
                  padding: "14px",
                  border: "1px solid #dcdcdc",
                  borderRadius: "10px",
                  marginBottom: "10px",
                  fontFamily: "inherit",
                  fontSize: "0.95rem",
                  background: "white",
                }}
              >
                <option value="" disabled>
                  {cargandoFichas ? "Cargando fichas..." : "Selecciona tu ficha"}
                </option>
                {fichas.map((f) => (
                  <option key={f.id_ficha} value={f.id_ficha}>
                    {f.numero_ficha} - {f.programa}
                  </option>
                ))}
              </select>
            )}

            <div style={{ display: "flex", gap: "10px" }}>
              <div style={{ flex: 1 }}>
                <label>Contraseña</label>
                <input
                  type="password"
                  name="contrasena"
                  placeholder="Mínimo 6 caracteres"
                  value={formulario.contrasena}
                  onChange={manejarCambio}
                  required
                />
              </div>
              <div style={{ flex: 1 }}>
                <label>Confirmar contraseña</label>
                <input
                  type="password"
                  name="confirmarContrasena"
                  placeholder="Repite tu contraseña"
                  value={formulario.confirmarContrasena}
                  onChange={manejarCambio}
                  required
                />
              </div>
            </div>

            <button type="submit" disabled={cargando || cargandoFichas || fichas.length === 0}>
              {cargando ? "Creando cuenta..." : "Registrarme"}
            </button>
          </form>

          <div className="registro-link">
            <p>
              ¿Ya tienes una cuenta? <Link to="/login">Inicia sesión aquí</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Registro;
