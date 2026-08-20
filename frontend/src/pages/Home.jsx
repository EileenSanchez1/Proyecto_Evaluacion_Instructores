import "../styles/Home.css";
import { Link } from "react-router-dom";

function Home() {
  return (
    <div className="dashboard-content">

      {/* Welcome Section */}
      <div className="welcome-section">
        <h1>¡Bienvenido!</h1>
        <p>Este es el resumen general del sistema.</p>
      </div>

      {/* Hero Banner */}
      <section className="hero-banner">

        <div className="hero-text">
          <h2>
            Evalúa. Aprende.
            <br />
            Mejora juntos.
          </h2>

          <p>
            Tu opinión ayuda a fortalecer la calidad de nuestros instructores.
          </p>

          <Link to="/evaluaciones" className="btn-primary">
            <span>▶</span>
            Realizar evaluación
          </Link>
        </div>

        <div className="hero-image">
          <img
            src="https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=500&h=300&fit=crop"
            alt="Estudiantes colaborando"
          />
        </div>

      </section>

      {/* Info Section */}
      <section className="info-section">

        <div className="info-row">

          <div className="info-card">
            <h2>Bienvenido/a</h2>

            <p>
              Bienvenido al sistema institucional de evaluación de
              instructores del SENA. Esta plataforma permite gestionar
              evaluaciones académicas de forma organizada, segura y eficiente
              mediante acceso por roles.
            </p>
          </div>

          <div className="info-card">
            <h2>Descripción del Sistema</h2>

            <p>
              El sistema permite que los aprendices evalúen únicamente a los
              instructores correspondientes a su ficha de formación,
              garantizando confiabilidad en los resultados, control de acceso
              y administración académica centralizada.
            </p>
          </div>

        </div>

      </section>

      {/* Stats Cards */}
      <section className="stats-section">

        <div className="stat-card">
          <div className="stat-header">
            <div className="stat-icon green">
              ✓
            </div>

            <span className="stat-label">
              Evaluaciones realizadas
            </span>
          </div>

          <div className="stat-number">150</div>

          <div className="stat-trend up">
            ↑
            <span>+12% desde el mes pasado</span>
          </div>
        </div>


        <div className="stat-card">
          <div className="stat-header">
            <div className="stat-icon blue">
              👤
            </div>

            <span className="stat-label">
              Instructores registrados
            </span>
          </div>

          <div className="stat-number">25</div>

          <div className="stat-trend up">
            ↑
            <span>+8% desde el mes pasado</span>
          </div>
        </div>


        <div className="stat-card">
          <div className="stat-header">
            <div className="stat-icon teal">
              ▣
            </div>

            <span className="stat-label">
              Fichas activas
            </span>
          </div>

          <div className="stat-number">12</div>

          <div className="stat-trend up">
            ↑
            <span>+5% desde el mes pasado</span>
          </div>
        </div>


        <div className="stat-card">
          <div className="stat-header">
            <div className="stat-icon orange">
              ▤
            </div>

            <span className="stat-label">
              Reportes generados
            </span>
          </div>

          <div className="stat-number">18</div>

          <div className="stat-trend up">
            ↑
            <span>+15% desde el mes pasado</span>
          </div>
        </div>

      </section>


      {/* Charts Section */}
      <section className="charts-section">

        {/* Bar Chart */}
        <div className="chart-card bar-chart">

          <div className="chart-header">
            <h3>Resumen de evaluaciones</h3>

            <div className="chart-filter">
              <span>Este año</span>
              <span>⌄</span>
            </div>
          </div>

          <div className="chart-body">

            <div className="bar-chart-container">

              <div className="y-axis">
                <span>100</span>
                <span>80</span>
                <span>60</span>
                <span>40</span>
                <span>20</span>
                <span>0</span>
              </div>


              <div className="bars-container">

                <div className="bar-group">
                  <div className="bar" style={{ height: "45%" }}>
                    <span className="bar-tooltip">45</span>
                  </div>
                  <span className="bar-label">Ene</span>
                </div>

                <div className="bar-group">
                  <div className="bar" style={{ height: "60%" }}>
                    <span className="bar-tooltip">60</span>
                  </div>
                  <span className="bar-label">Feb</span>
                </div>

                <div className="bar-group">
                  <div className="bar" style={{ height: "55%" }}>
                    <span className="bar-tooltip">55</span>
                  </div>
                  <span className="bar-label">Mar</span>
                </div>

                <div className="bar-group">
                  <div className="bar" style={{ height: "75%" }}>
                    <span className="bar-tooltip">75</span>
                  </div>
                  <span className="bar-label">Abr</span>
                </div>

                <div className="bar-group">
                  <div className="bar" style={{ height: "65%" }}>
                    <span className="bar-tooltip">65</span>
                  </div>
                  <span className="bar-label">May</span>
                </div>

                <div className="bar-group">
                  <div className="bar" style={{ height: "85%" }}>
                    <span className="bar-tooltip">85</span>
                  </div>
                  <span className="bar-label">Jun</span>
                </div>

                <div className="bar-group">
                  <div className="bar" style={{ height: "70%" }}>
                    <span className="bar-tooltip">70</span>
                  </div>
                  <span className="bar-label">Jul</span>
                </div>

                <div className="bar-group">
                  <div className="bar" style={{ height: "90%" }}>
                    <span className="bar-tooltip">90</span>
                  </div>
                  <span className="bar-label">Ago</span>
                </div>

                <div className="bar-group">
                  <div className="bar" style={{ height: "80%" }}>
                    <span className="bar-tooltip">80</span>
                  </div>
                  <span className="bar-label">Sep</span>
                </div>

                <div className="bar-group">
                  <div className="bar" style={{ height: "95%" }}>
                    <span className="bar-tooltip">95</span>
                  </div>
                  <span className="bar-label">Oct</span>
                </div>

                <div className="bar-group">
                  <div className="bar" style={{ height: "85%" }}>
                    <span className="bar-tooltip">85</span>
                  </div>
                  <span className="bar-label">Nov</span>
                </div>

                <div className="bar-group">
                  <div className="bar" style={{ height: "70%" }}>
                    <span className="bar-tooltip">70</span>
                  </div>
                  <span className="bar-label">Dic</span>
                </div>

              </div>

            </div>

          </div>

        </div>


        {/* Donut */}
        <div className="chart-card donut-chart">

          <div className="chart-header">
            <h3>Promedio general</h3>
          </div>

          <div className="chart-body">

            <div className="donut-container">

              <svg
                viewBox="0 0 200 200"
                className="donut-svg"
              >
                <circle
                  cx="100"
                  cy="100"
                  r="80"
                  fill="none"
                  stroke="#e8e8e8"
                  strokeWidth="18"
                />

                <circle
                  cx="100"
                  cy="100"
                  r="80"
                  fill="none"
                  stroke="#ffc107"
                  strokeWidth="18"
                  strokeDasharray="60 502"
                  strokeDashoffset="0"
                  strokeLinecap="round"
                  transform="rotate(-90 100 100)"
                />

                <circle
                  cx="100"
                  cy="100"
                  r="80"
                  fill="none"
                  stroke="#4caf50"
                  strokeWidth="18"
                  strokeDasharray="380 502"
                  strokeDashoffset="-60"
                  strokeLinecap="round"
                  transform="rotate(-90 100 100)"
                />
              </svg>

              <div className="donut-center">
                <span className="donut-score">4.6</span>
                <span className="donut-total">de 5</span>
              </div>

            </div>


            <div className="legend">

              <div className="legend-item">
                <span className="legend-dot green"></span>
                <span>Excelente</span>
              </div>

              <div className="legend-item">
                <span className="legend-dot light-green"></span>
                <span>Bueno</span>
              </div>

              <div className="legend-item">
                <span className="legend-dot yellow"></span>
                <span>Regular</span>
              </div>

              <div className="legend-item">
                <span className="legend-dot red"></span>
                <span>Deficiente</span>
              </div>

            </div>

          </div>

        </div>

      </section>

    </div>
  );
}

export default Home;