import { useEffect, useState } from "react";
import axios from "axios";
import { Card } from "@/components/ui/card";
import { Users, Plane, Phone, Calendar as CalendarIcon } from "lucide-react";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = () => {
  const [stats, setStats] = useState({
    total_passengers: 0,
    total_trips: 0,
    upcoming_trips: 0,
    total_calls: 0,
  });
  const [recentTrips, setRecentTrips] = useState([]);
  const [recentCalls, setRecentCalls] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsRes, tripsRes, callsRes] = await Promise.all([
        axios.get(`${API}/stats`),
        axios.get(`${API}/trips?status=upcoming`),
        axios.get(`${API}/calls`),
      ]);

      setStats(statsRes.data);
      setRecentTrips(tripsRes.data.slice(0, 5));
      setRecentCalls(callsRes.data.slice(-5).reverse());
    } catch (error) {
      toast.error("Error al cargar datos del dashboard");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const statCards = [
    {
      title: "Total Pasajeros",
      value: stats.total_passengers,
      icon: Users,
      color: "bg-emerald-600",
    },
    {
      title: "Viajes Próximos",
      value: stats.upcoming_trips,
      icon: Plane,
      color: "bg-amber-600",
    },
    {
      title: "Total Viajes",
      value: stats.total_trips,
      icon: CalendarIcon,
      color: "bg-blue-600",
    },
    {
      title: "Llamadas Registradas",
      value: stats.total_calls,
      icon: Phone,
      color: "bg-purple-600",
    },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-slate-600">Cargando...</div>
      </div>
    );
  }

  return (
    <div className="p-8 md:p-12" data-testid="dashboard">
      <div className="mb-8">
        <h1
          className="text-4xl md:text-5xl font-bold text-slate-900 mb-2"
          style={{ fontFamily: 'Playfair Display, serif' }}
        >
          Dashboard
        </h1>
        <p className="text-slate-600">Resumen de tu gestión de viajes</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {statCards.map((stat) => (
          <Card
            key={stat.title}
            data-testid={`stat-${stat.title.toLowerCase().replace(/ /g, '-')}`}
            className="p-6 bg-white rounded-xl border border-slate-100 shadow-sm hover:shadow-lg transition-all duration-300"
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-slate-600 mb-2">{stat.title}</p>
                <p className="text-3xl font-bold text-slate-900">{stat.value}</p>
              </div>
              <div className={`${stat.color} p-3 rounded-lg`}>
                <stat.icon className="w-6 h-6 text-white" />
              </div>
            </div>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-6 bg-white rounded-xl border border-slate-100 shadow-sm">
          <h2
            className="text-2xl font-bold text-slate-900 mb-4"
            style={{ fontFamily: 'Playfair Display, serif' }}
          >
            Próximos Viajes
          </h2>
          {recentTrips.length === 0 ? (
            <p className="text-slate-500 text-center py-8">No hay viajes próximos</p>
          ) : (
            <div className="space-y-3">
              {recentTrips.map((trip) => (
                <div
                  key={trip.id}
                  className="p-4 bg-slate-50 rounded-lg border border-slate-200 hover:border-amber-600 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-semibold text-slate-900">{trip.title}</h3>
                      <p className="text-sm text-slate-600">{trip.destination}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-amber-600">
                        {new Date(trip.start_date).toLocaleDateString('es-ES')}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>

        <Card className="p-6 bg-white rounded-xl border border-slate-100 shadow-sm">
          <h2
            className="text-2xl font-bold text-slate-900 mb-4"
            style={{ fontFamily: 'Playfair Display, serif' }}
          >
            Llamadas Recientes
          </h2>
          {recentCalls.length === 0 ? (
            <p className="text-slate-500 text-center py-8">No hay llamadas registradas</p>
          ) : (
            <div className="space-y-3">
              {recentCalls.map((call) => (
                <div
                  key={call.id}
                  className="p-4 bg-slate-50 rounded-lg border border-slate-200"
                >
                  <div className="flex items-start justify-between mb-2">
                    <p className="text-sm font-medium text-slate-900">
                      {new Date(call.call_date).toLocaleDateString('es-ES')}
                    </p>
                    {call.duration && (
                      <p className="text-sm text-slate-600">{call.duration} min</p>
                    )}
                  </div>
                  {call.notes && (
                    <p className="text-sm text-slate-600 line-clamp-2">{call.notes}</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
