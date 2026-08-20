import { Outlet } from "react-router-dom";
import Navbar from "./Navbar";
import Sidebar from "./Sidebar";
import "./Layout.css";

function Layout() {
  return (
    <div className="layout">
      <Sidebar />
      <div className="layout-main">
        <Navbar />
        <main className="main-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default Layout;
{/* Meses */}