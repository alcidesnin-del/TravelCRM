import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { Bell, AlertTriangle, Plane, X, Shield, Clock, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const severityConfig = {
  critical: { color: "bg-red-500", text: "text-red-700", bg: "bg-red-50", border: "border-red-200", icon: AlertTriangle },
  high: { color: "bg-orange-500", text: "text-orange-700", bg: "bg-orange-50", border: "border-orange-200", icon: AlertTriangle },
  medium: { color: "bg-amber-500", text: "text-amber-700", bg: "bg-amber-50", border: "border-amber-200", icon: Clock },
  low: { color: "bg-yellow-500", text: "text-yellow-700", bg: "bg-yellow-50", border: "border-yellow-200", icon: Clock },
  info: { color: "bg-blue-500", text: "text-blue-700", bg: "bg-blue-50", border: "border-blue-200", icon: Plane },
};

const NotificationBell = () => {
  const [notifications, setNotifications] = useState([]);
  const [count, setCount] = useState(0);
  const [open, setOpen] = useState(false);
  const panelRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 60000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (panelRef.current && !panelRef.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const fetchNotifications = async () => {
    try {
      const res = await axios.get(`${API}/notifications`);
      setNotifications(res.data.notifications);
      setCount(res.data.count);
    } catch (err) {
      console.error("Error fetching notifications:", err);
    }
  };

  const dismissNotification = async (notifId, e) => {
    e.stopPropagation();
    try {
      await axios.post(`${API}/notifications/dismiss/${notifId}`);
      setNotifications((prev) => prev.filter((n) => n.id !== notifId));
      setCount((prev) => Math.max(0, prev - 1));
    } catch (err) {
      console.error("Error dismissing notification:", err);
    }
  };

  const handleNotifClick = (notif) => {
    if (notif.passenger_id) {
      navigate(`/app/passengers/${notif.passenger_id}`);
      setOpen(false);
    }
  };

  return (
    <div className="relative" ref={panelRef}>
      <button
        onClick={() => setOpen(!open)}
        data-testid="notification-bell"
        className="relative p-2 rounded-lg hover:bg-slate-800 transition-colors"
      >
        <Bell className="w-5 h-5 text-slate-300" />
        {count > 0 && (
          <span
            data-testid="notification-badge"
            className="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full min-w-[18px] h-[18px] flex items-center justify-center px-1"
          >
            {count > 99 ? "99+" : count}
          </span>
        )}
      </button>

      {open && (
        <div
          data-testid="notification-panel"
          className="fixed left-64 top-12 w-96 bg-white rounded-xl shadow-2xl border border-slate-200 z-[100] overflow-hidden"
          style={{ maxHeight: "calc(100vh - 80px)" }}
        >
          <div className="px-4 py-3 bg-slate-900 text-white flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4" />
              <span className="font-semibold text-sm">Notificaciones</span>
            </div>
            <span className="text-xs text-slate-400">
              {count} {count === 1 ? "alerta" : "alertas"}
            </span>
          </div>

          <div className="max-h-96 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="py-10 text-center">
                <Bell className="w-10 h-10 text-slate-300 mx-auto mb-2" />
                <p className="text-sm text-slate-500">Sin notificaciones</p>
              </div>
            ) : (
              notifications.map((notif) => {
                const config = severityConfig[notif.severity] || severityConfig.info;
                const Icon = config.icon;
                return (
                  <div
                    key={notif.id}
                    data-testid={`notification-item-${notif.id}`}
                    onClick={() => handleNotifClick(notif)}
                    className={`px-4 py-3 border-b border-slate-100 hover:bg-slate-50 cursor-pointer transition-colors flex items-start gap-3`}
                  >
                    <div className={`mt-0.5 p-1.5 rounded-lg ${config.bg}`}>
                      <Icon className={`w-4 h-4 ${config.text}`} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-slate-900">{notif.title}</p>
                      <p className="text-xs text-slate-600 mt-0.5 line-clamp-2">{notif.message}</p>
                    </div>
                    <div className="flex items-center gap-1 flex-shrink-0">
                      <button
                        onClick={(e) => dismissNotification(notif.id, e)}
                        data-testid={`dismiss-notif-${notif.id}`}
                        className="p-1 rounded hover:bg-slate-200 transition-colors"
                        title="Descartar"
                      >
                        <X className="w-3.5 h-3.5 text-slate-400" />
                      </button>
                      <ChevronRight className="w-4 h-4 text-slate-300" />
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default NotificationBell;
