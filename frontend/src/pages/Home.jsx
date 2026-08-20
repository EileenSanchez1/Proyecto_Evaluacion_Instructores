import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/Home.css';

const Home = ({ usuario, rol }) => {

  const renderHeroButton = () => {
    if (usuario) {
      if (rol === 'aprendiz') {
        return (
          <Link to="/evaluaciones" className="btn-primary">
            <i className="fas fa-play"></i>
            Realizar evaluación
          </Link>
        );
      }
      return null;
    }

    return (
      <Link to="/login" className="btn-primary">
        <i className="fas fa-play"></i>
        Iniciar sesión para evaluar
      </Link>
    );
  };

  const barData = [
    { month: 'Ene', value: 45 },
    { month: 'Feb', value: 60 },
    { month: 'Mar', value: 55 },
    { month: 'Abr', value: 75 },
    { month: 'May', value: 65 },
    { month: 'Jun', value: 85 },
    { month: 'Jul', value: 70 },
    { month: 'Ago', value: 90 },
    { month: 'Sep', value: 80 },
    { month: 'Oct', value: 95 },
    { month: 'Nov', value: 85 },
    { month: 'Dic', value: 70 },
  ];

  return (
    <div className="dashboard-content">

      {/* Welcome */}
      <div className="welcome-section">
        <h1>¡Bienvenido!</h1>
        <p>Este es el resumen general del sistema.</p>
      </div>

      {/* Hero Banner */}
      <section className="hero-banner">
        <div className="hero-text">
          <h2>
            Evalúa. Aprende.<br />
            Mejora juntos.
          </h2>
          <p>Tu opinión ayuda a fortalecer la calidad de nuestros instructores.</p>
          {renderHeroButton()}
        </div>
        <div className="hero-image">
          <img
            src="https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=500&h=300&fit=crop"
            alt="Estudiantes colaborando"
          />
        </div>
      </section>

      {/* Stats Cards */}
      <section className="stats-section">
        <div className="stat-card">
          <div className="stat-header">
            <div className="stat-icon green">
              <i className="fas fa-clipboard-check"></i>
            </div>
            <span className="stat-label">Evaluaciones realizadas</span>
          </div>
          <div className="stat-number">150</div>
          <div className="stat-trend up">
            <i className="fas fa-arrow-trend-up"></i>
            <span>+12% desde el mes pasado</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <div className="stat-icon blue">
              <i className="fas fa-chalkboard-user"></i>
            </div>
            <span className="stat-label">Instructores registrados</span>
          </div>
          <div className="stat-number">25</div>
          <div className="stat-trend up">
            <i className="fas fa-arrow-trend-up"></i>
            <span>+8% desde el mes pasado</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <div className="stat-icon teal">
              <i className="fas fa-address-card"></i>
            </div>
            <span className="stat-label">Fichas activas</span>
          </div>
          <div className="stat-number">12</div>
          <div className="stat-trend up">
            <i className="fas fa-arrow-trend-up"></i>
            <span>+5% desde el mes pasado</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <div className="stat-icon orange">
              <i className="fas fa-file-lines"></i>
            </div>
            <span className="stat-label">Reportes generados</span>
          </div>
          <div className="stat-number">18</div>
          <div className="stat-trend up">
            <i className="fas fa-arrow-trend-up"></i>
            <span>+15% desde el mes pasado</span>
          </div>
        </div>
      </section>

      {/* Charts */}
      <section className="charts-section">
        <div className="chart-card bar-chart">
          <div className="chart-header">
            <h3>Resumen de evaluaciones</h3>
            <div className="chart-filter">
              <span>Este año</span>
              <i className="fas fa-chevron-down"></i>
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
                {barData.map((item) => (
                  <div className="bar-group" key={item.month}>
                    <div className="bar" style={{ height: `${item.value}%` }}>
                      <span className="bar-tooltip">{item.value}</span>
                    </div>
                    <span className="bar-label">{item.month}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="chart-card donut-chart">
          <div className="chart-header">
            <h3>Promedio general</h3>
          </div>
          <div className="chart-body">
            <div className="donut-container">
              <svg viewBox="0 0 200 200" className="donut-svg">
                <circle cx="100" cy="100" r="80" fill="none" stroke="#e8e8e8" strokeWidth="18" />
                <circle
                  cx="100" cy="100" r="80" fill="none" stroke="#ffc107" strokeWidth="18"
                  strokeDasharray="60 502" strokeDashoffset="0" strokeLinecap="round"
                  transform="rotate(-90 100 100)"
                />
                <circle
                  cx="100" cy="100" r="80" fill="none" stroke="#4caf50" strokeWidth="18"
                  strokeDasharray="380 502" strokeDashoffset="-60" strokeLinecap="round"
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
};

export default Home;