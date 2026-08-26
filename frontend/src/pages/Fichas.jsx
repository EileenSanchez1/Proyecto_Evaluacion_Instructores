import { useEffect, useState } from "react";
import { listarFichas, obtenerFicha } from "../services/fichaService";
import "../styles/Fichas.css";

function Fichas() {
  const [fichas, setFichas] = useState([]);
  const [fichasFiltradas, setFichasFiltradas] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [busqueda, setBusqueda] = useState("");
  const [fichaDetalle, setFichaDetalle] = useState(null);
  const [cargandoDetalle, setCargandoDetalle] = useState(false);

  const cargarFichas = async () => {
    try {
      setCargando(true);
      setError("");
      const datos = await listarFichas();
      setFichas(datos);
      setFichasFiltradas(datos);
    } catch (err) {
      console.error(err);
      setError("No se pudieron cargar las fichas.");
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarFichas();
  }, []);

  // Búsqueda / filtro (cliente)
  useEffect(() => {
    const query = busqueda.toLowerCase().trim();

    if (!query) {
      setFichasFiltradas(fichas);
      return;
    }

    const filtradas = fichas.filter(
      (f) =>
        f.numero_ficha.toLowerCase().includes(query) ||
        f.programa.toLowerCase().includes(query) ||
        (f.descripcion && f.descripcion.toLowerCase().includes(query))
    );

    setFichasFiltradas(filtradas);
  }, [busqueda, fichas]);

  const verDetalle = async (id) => {
    try {
      setCargandoDetalle(true);
      const data = await obtenerFicha(id);
      setFichaDetalle(data);
    } catch (err) {
      console.error(err);
      alert("No se pudo cargar el detalle de la ficha.");
    } finally {
      setCargandoDetalle(false);
    }
  };

  const cerrarDetalle = () => {
    setFichaDetalle(null);
  };

  return (
    <div className="pagina-fichas">
      {/* Encabezado */}
      <div className="encabezado-fichas">
        <div>
          <h1>Gestión de Fichas</h1>
          <p className="subtitulo">Consulta las fichas de formación registradas</p>
        </div>
      </div>

      {/* Buscador */}
      <div className="barra-busqueda">
        <input
          type="text"
          placeholder="Buscar por número de ficha o programa..."
          value={busqueda}
          onChange={(e) => setBusqueda(e.target.value)}
          className="input-busqueda"
        />
      </div>

      <p className="contador">
        {fichasFiltradas.length}{" "}
        {fichasFiltradas.length === 1 ? "ficha encontrada" : "fichas encontradas"}
      </p>

      {/* Estados de carga / error */}
      {cargando && <p className="mensaje">Cargando fichas...</p>}
      {error && <p className="mensaje error">{error}</p>}

      {!cargando && !error && fichasFiltradas.length === 0 && (
        <div className="sin-resultados">
          <h4>No se encontraron fichas</h4>
          <p>Intenta con otro término de búsqueda</p>
        </div>
      )}

      {/* Grid de tarjetas */}
      {!cargando && fichasFiltradas.length > 0 && (
        <div className="grid-fichas">
          {fichasFiltradas.map((ficha) => (
            <div key={ficha.id_ficha} className="tarjeta-ficha">
              <div className="tarjeta-header">
                <span className="numero-ficha">#{ficha.numero_ficha}</span>
              </div>

              <h3 className="programa">{ficha.programa}</h3>

              {ficha.descripcion && (
                <p className="descripcion">{ficha.descripcion}</p>
              )}

              <div className="tarjeta-acciones">
                <button
                  className="btn-ver"
                  onClick={() => verDetalle(ficha.id_ficha)}
                  disabled={cargandoDetalle}
                >
                  Ver detalle
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal Detalle */}
      {fichaDetalle && (
        <div className="modal-overlay" onClick={cerrarDetalle}>
          <div className="modal-contenido" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Detalle de la Ficha</h2>
              <button className="btn-cerrar" onClick={cerrarDetalle}>
                ×
              </button>
            </div>

            <div className="modal-body">
              <p>
                <strong>Número:</strong> {fichaDetalle.numero_ficha}
              </p>
              <p>
                <strong>Programa:</strong> {fichaDetalle.programa}
              </p>
              <p>
                <strong>Descripción:</strong>{" "}
                {fichaDetalle.descripcion || "Sin descripción"}
              </p>
              <p>
                <strong>ID:</strong> {fichaDetalle.id_ficha}
              </p>
            </div>

            <div className="modal-footer">
              <button className="btn-cerrar-modal" onClick={cerrarDetalle}>
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Fichas;