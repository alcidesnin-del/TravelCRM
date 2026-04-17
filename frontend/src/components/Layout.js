import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { LogOut, Home, Users, Calendar, Plane } from "lucide-react";
import { Button } from "@/components/ui/button";
import NotificationBell from "@/components/NotificationBell";

const Layout = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const navItems = [
    { path: "/app/dashboard", icon: Home, label: "Dashboard" },
    { path: "/app/passengers", icon: Users, label: "Pasajeros" },
    { path: "/app/calendar", icon: Calendar, label: "Calendario" },
  ];

  return (
    <div className="flex h-screen bg-slate-50">
      <aside className="w-64 bg-slate-900 text-white fixed left-0 top-0 h-full flex flex-col z-50">
        <div className="p-6 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="bg-amber-600 rounded-full p-2">
              <Plane className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold" style={{ fontFamily: 'Playfair Display, serif' }}>
                TravelCRM
              </h1>
              <p className="text-xs text-slate-400">Gestión de Viajes</p>
            </div>
          </div>
        </div>

        <div className="px-4 pt-3 flex justify-end">
          <NotificationBell />
        </div>

        <nav className="flex-1 p-4 space-y-2">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              data-testid={`nav-${item.label.toLowerCase()}`}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                  isActive
                    ? "bg-slate-800 text-white border-l-4 border-amber-600"
                    : "text-slate-300 hover:bg-slate-800 hover:text-white"
                }`
              }
            >
              <item.icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-slate-800">
          <div className="bg-slate-800 rounded-lg p-4 mb-4">
            <p className="text-sm font-medium">{user?.name}</p>
            <p className="text-xs text-slate-400 truncate">{user?.email}</p>
          </div>
          <Button
            onClick={handleLogout}
            data-testid="logout-button"
            className="w-full bg-slate-800 hover:bg-slate-700 text-white"
          >
            <LogOut className="w-4 h-4 mr-2" />
            Cerrar Sesión
          </Button>
        </div>
      </aside>

      <main className="ml-64 flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;
