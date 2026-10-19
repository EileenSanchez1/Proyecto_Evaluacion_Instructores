import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  login,
  instructorIniciar,
  instructorCrearPassword,
  loginInstructorPaso1,
  adminIniciar,
  adminVerificar,
} from "../services/authService";
import "../styles/Login.css";

function validarContrasenaSegura(contrasena) {
  if (contrasena.length < 8) return "La contraseña debe tener al menos 8 caracteres.";
  if (!/[A-Z]/.test(contrasena)) return "Debe contener al menos una mayúscula.";
  if (!/[a-z]/.test(contrasena)) return "Debe contener al menos una minúscula.";
  if (!/\d/.test(contrasena)) return "Debe contener al menos un número.";
  if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(contrasena))
    return "Debe contener al menos un carácter especial (!@#$%^&* etc.).";
  return null;
}

function Login() {
  const navigate = useNavigate();
  const [rol, setRol] = useState("aprendiz");
  const [correo, setCorreo] = useState("");
  const [contrasena, setContrasena] = useState("");
  const [mostrarPass, setMostrarPass] = useState(false);
  const [mensaje, setMensaje] = useState("");
  const [esError, setEsError] = useState(false);
  const [cargando, setCargando] = useState(false);
  const [pasoInstructor, setPasoInstructor] = useState(1);
  const [codigo, setCodigo] = useState("");
  const [confirmPass, setConfirmPass] = useState("");
  const [pasoAdmin, setPasoAdmin] = useState(1);

  const guardarSesion = (respuesta) => {
    localStorage.setItem("token", respuesta.access_token);
    localStorage.setItem("usuario", JSON.stringify(respuesta.usuario));
  };

  const resetMensajes = () => {
    setMensaje("");
    setEsError(false);
  };

  const cambiarRol = (nuevo) => {
    setRol(nuevo);
    resetMensajes();
    setCorreo("");
    setContrasena("");
    setCodigo("");
    setConfirmPass("");
    setPasoInstructor(1);
    setPasoAdmin(1);
  };

  const handleAprendiz = async (e) => {
    e.preventDefault();
    resetMensajes();
    if (!correo.trim() || !contrasena) {
      setEsError(true);
      setMensaje("Ingresa correo y contraseña.");
      return;
    }
    setCargando(true);
    try {
      const respuesta = await login({ correo: correo.trim(), contrasena });
      guardarSesion(respuesta);
      setMensaje("Inicio de sesión exitoso");
      setTimeout(() => navigate("/"), 400);
    } catch (error) {
      setEsError(true);
      setMensaje(error.response?.data?.detail || "Correo o contraseña incorrectos");
    } finally {
      setCargando(false);
    }
  };

  const handleInstructorCorreo = async (e) => {
    e.preventDefault();
    resetMensajes();
    const c = correo.trim().toLowerCase();
    if (!c.endsWith("@sena.edu.co")) {
      setEsError(true);
      setMensaje("El correo debe ser institucional (@sena.edu.co).");
      return;
    }
    try {
      setCargando(true);
      const res = await instructorIniciar(c);
      if (res.requiere_crear_password) {
        setPasoInstructor(2);
        setMensaje(res.mensaje || "Se envió un código a tu correo. Créa tu contraseña.");
      } else {
        setPasoInstructor(3);
        setMensaje(res.mensaje || "Ingresa tu contraseña.");
      }
    } catch (err) {
      setEsError(true);
      setMensaje(err.response?.data?.detail || "No se pudo iniciar el proceso.");
    } finally {
      setCargando(false);
    }
  };

  const handleInstructorCrearPassword = async (e) => {
    e.preventDefault();
    resetMensajes();
    const errPass = validarContrasenaSegura(contrasena);
    if (errPass) {
      setEsError(true);
      setMensaje(errPass);
      return;
    }
    if (contrasena !== confirmPass) {
      setEsError(true);
      setMensaje("Las contraseñas no coinciden.");
      return;
    }
    if (!codigo.trim()) {
      setEsError(true);
      setMensaje("Ingresa el código recibido por correo.");
      return;
    }
    try {
      setCargando(true);
      const res = await instructorCrearPassword({
        correo: correo.trim().toLowerCase(),
        codigo: codigo.trim(),
        nueva_contrasena: contrasena,
      });
      guardarSesion(res);
      setMensaje("Contraseña creada. Bienvenido/a.");
      setTimeout(() => navigate("/"), 400);
    } catch (err) {
      setEsError(true);
      setMensaje(err.response?.data?.detail || "No se pudo crear la contraseña.");
    } finally {
      setCargando(false);
    }
  };

  const handleInstructorLogin = async (e) => {
    e.preventDefault();
    resetMensajes();
    if (!contrasena) {
      setEsError(true);
      setMensaje("Ingresa tu contraseña.");
      return;
    }
    try {
      setCargando(true);
      const res = await loginInstructorPaso1({
        correo: correo.trim().toLowerCase(),
        contrasena,
      });
      guardarSesion(res);
      setMensaje("Inicio de sesión exitoso");
      setTimeout(() => navigate("/"), 400);
    } catch (err) {
      setEsError(true);
      setMensaje(err.response?.data?.detail || "Correo o contraseña incorrectos");
    } finally {
      setCargando(false);
    }
  };

  const handleAdminPaso1 = async (e) => {
    e.preventDefault();
    resetMensajes();
    if (!correo.trim() || !contrasena) {
      setEsError(true);
      setMensaje("Ingresa correo y contraseña de administrador.");
      return;
    }
    try {
      setCargando(true);
      const res = await adminIniciar({
        correo: correo.trim().toLowerCase(),
        contrasena,
      });
      setPasoAdmin(2);
      setMensaje(res.mensaje || "Se envió un código a tu correo. Ingrésalo para continuar.");
    } catch (err) {
      setEsError(true);
      setMensaje(err.response?.data?.detail || "Credenciales incorrectas o no eres administrador.");
    } finally {
      setCargando(false);
    }
  };

  const handleAdminCodigo = async (e) => {
    e.preventDefault();
    resetMensajes();
    if (!codigo.trim()) {
      setEsError(true);
      setMensaje("Ingresa el código recibido por correo.");
      return;
    }
    try {
      setCargando(true);
      const res = await adminVerificar({
        correo: correo.trim().toLowerCase(),
        codigo: codigo.trim(),
      });
      guardarSesion(res);
      setMensaje("Acceso de administrador concedido.");
      setTimeout(() => navigate("/"), 400);
    } catch (err) {
      setEsError(true);
      setMensaje(err.response?.data?.detail || "Código inválido o expirado.");
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
          <p>Plataforma de Evaluación de Instructores</p>
        </div>

        <div className="lado-formulario">
          <h1>Iniciar sesión</h1>

          <div className="login-tabs" style={{
            display: "flex",
            gap: "0.35rem",
            marginBottom: "1.25rem",
            flexWrap: "wrap",
          }}>
            {[
              { id: "aprendiz", label: "Soy Aprendiz" },
              { id: "instructor", label: "Soy Instructor" },
              { id: "admin", label: "Soy Admin" },
            ].map((t) => (
              <button
                key={t.id}
                type="button"
                onClick={() => cambiarRol(t.id)}
                style={{
                  flex: 1,
                  minWidth: "100px",
                  padding: "0.55rem 0.75rem",
                  border: "none",
                  borderRadius: "8px",
                  cursor: "pointer",
                  fontWeight: 600,
                  fontSize: "0.9rem",
                  background: rol === t.id ? "#0d7377" : "#d1d5db",
                  color: rol === t.id ? "#fff" : "#374151",
                  transition: "background 0.2s",
                }}
              >
                {t.label}
              </button>
            ))}
          </div>

          <p className="subtitulo">
            {rol === "aprendiz" &&
              "Usa el correo y la contraseña que te enviaron al inicio del periodo."}
            {rol === "instructor" &&
              "Correo institucional @sena.edu.co. En el primer acceso crearás tu contraseña."}
            {rol === "admin" &&
              "Acceso restringido. Tras validar la contraseña se enviará un código a tu Gmail."}
          </p>

          {mensaje && (
            <div className={`mensaje-login ${esError ? "error" : "exito"}`}>
              {mensaje}
            </div>
          )}

          {rol === "aprendiz" && (
            <form onSubmit={handleAprendiz}>
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
                    placeholder="Contraseña"
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
                {cargando ? "Ingresando..." : "Iniciar sesión"}
              </button>
            </form>
          )}

          {rol === "instructor" && pasoInstructor === 1 && (
            <form onSubmit={handleInstructorCorreo}>
              <div>
                <label>Correo institucional</label>
                <input
                  type="email"
                  placeholder="nombre.apellido@sena.edu.co"
                  value={correo}
                  onChange={(e) => setCorreo(e.target.value)}
                  required
                />
              </div>
              <button type="submit" disabled={cargando}>
                {cargando ? "Verificando..." : "Continuar"}
              </button>
            </form>
          )}

          {rol === "instructor" && pasoInstructor === 2 && (
            <form onSubmit={handleInstructorCrearPassword}>
              <div>
                <label>Código recibido por correo</label>
                <input
                  type="text"
                  placeholder="Código de 6 dígitos"
                  value={codigo}
                  onChange={(e) => setCodigo(e.target.value)}
                  required
                />
              </div>
              <div className="password-field">
                <label>Nueva contraseña</label>
                <div className="password-input-wrapper">
                  <input
                    type={mostrarPass ? "text" : "password"}
                    placeholder="Mín. 8 caracteres, mayúscula, número y símbolo"
                    value={contrasena}
                    onChange={(e) => setContrasena(e.target.value)}
                    required
                  />
                  <button
                    type="button"
                    className="btn-ojito"
                    onClick={() => setMostrarPass(!mostrarPass)}
                  >
                    <i className={`bi ${mostrarPass ? "bi-eye-slash" : "bi-eye"}`}></i>
                  </button>
                </div>
              </div>
              <div>
                <label>Confirmar contraseña</label>
                <input
                  type="password"
                  placeholder="Repite la contraseña"
                  value={confirmPass}
                  onChange={(e) => setConfirmPass(e.target.value)}
                  required
                />
              </div>
              <button type="submit" disabled={cargando}>
                {cargando ? "Creando..." : "Crear contraseña e ingresar"}
              </button>
              <button
                type="button"
                style={{ marginTop: "0.5rem", background: "#6b7280" }}
                onClick={() => {
                  setPasoInstructor(1);
                  setCodigo("");
                  setContrasena("");
                  setConfirmPass("");
                  resetMensajes();
                }}
              >
                Volver
              </button>
            </form>
          )}

          {rol === "instructor" && pasoInstructor === 3 && (
            <form onSubmit={handleInstructorLogin}>
              <div>
                <label>Correo</label>
                <input type="email" value={correo} disabled />
              </div>
              <div className="password-field">
                <label>Contraseña</label>
                <div className="password-input-wrapper">
                  <input
                    type={mostrarPass ? "text" : "password"}
                    placeholder="Tu contraseña"
                    value={contrasena}
                    onChange={(e) => setContrasena(e.target.value)}
                    required
                  />
                  <button
                    type="button"
                    className="btn-ojito"
                    onClick={() => setMostrarPass(!mostrarPass)}
                  >
                    <i className={`bi ${mostrarPass ? "bi-eye-slash" : "bi-eye"}`}></i>
                  </button>
                </div>
              </div>
              <button type="submit" disabled={cargando}>
                {cargando ? "Ingresando..." : "Iniciar sesión"}
              </button>
              <button
                type="button"
                style={{ marginTop: "0.5rem", background: "#6b7280" }}
                onClick={() => {
                  setPasoInstructor(1);
                  setContrasena("");
                  resetMensajes();
                }}
              >
                Cambiar correo
              </button>
            </form>
          )}

          {rol === "admin" && pasoAdmin === 1 && (
            <form onSubmit={handleAdminPaso1}>
              <div>
                <label>Correo de administrador</label>
                <input
                  type="email"
                  placeholder="admin@..."
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
                    placeholder="Contraseña"
                    value={contrasena}
                    onChange={(e) => setContrasena(e.target.value)}
                    required
                  />
                  <button
                    type="button"
                    className="btn-ojito"
                    onClick={() => setMostrarPass(!mostrarPass)}
                  >
                    <i className={`bi ${mostrarPass ? "bi-eye-slash" : "bi-eye"}`}></i>
                  </button>
                </div>
              </div>
              <button type="submit" disabled={cargando}>
                {cargando ? "Validando..." : "Continuar"}
              </button>
            </form>
          )}

          {rol === "admin" && pasoAdmin === 2 && (
            <form onSubmit={handleAdminCodigo}>
              <div>
                <label>Código enviado a tu correo</label>
                <input
                  type="text"
                  placeholder="Código de 6 dígitos"
                  value={codigo}
                  onChange={(e) => setCodigo(e.target.value)}
                  required
                  autoFocus
                />
              </div>
              <button type="submit" disabled={cargando}>
                {cargando ? "Verificando..." : "Verificar e ingresar"}
              </button>
              <button
                type="button"
                style={{ marginTop: "0.5rem", background: "#6b7280" }}
                onClick={() => {
                  setPasoAdmin(1);
                  setCodigo("");
                  resetMensajes();
                }}
              >
                Volver
              </button>
            </form>
          )}

          <div style={{ marginTop: "1rem", textAlign: "center" }}>
            <Link to="/recuperar-contrasena">Recuperar contraseña</Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;
