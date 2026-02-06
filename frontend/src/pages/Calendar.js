import { useEffect, useState } from "react";
import { Calendar as BigCalendar, momentLocalizer } from 'react-big-calendar';
import moment from 'moment';
import 'moment/locale/es';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import axios from "axios";
import { Card } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { MapPin, Calendar as CalendarIcon, User, Plane } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

moment.locale('es');
const localizer = momentLocalizer(moment);

const Calendar = () => {
  const [trips, setTrips] = useState([]);
  const [passengers, setPassengers] = useState({});
  const [events, setEvents] = useState([]);
  const [selectedTrip, setSelectedTrip] = useState(null);
  const [showDetailDialog, setShowDetailDialog] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [tripsRes, passengersRes] = await Promise.all([
        axios.get(`${API}/trips`),
        axios.get(`${API}/passengers`),
      ]);

      setTrips(tripsRes.data);

      const passengersMap = {};
      passengersRes.data.forEach((p) => {
        passengersMap[p.id] = p;
      });
      setPassengers(passengersMap);

      const calendarEvents = tripsRes.data.map((trip) => ({
        id: trip.id,
        title: trip.title,
        start: new Date(trip.start_date),
        end: new Date(trip.end_date),
        resource: trip,
      }));
      setEvents(calendarEvents);
    } catch (error) {
      toast.error("Error al cargar datos del calendario");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectEvent = (event) => {
    setSelectedTrip(event.resource);
    setShowDetailDialog(true);
  };

  const eventStyleGetter = (event) => {
    const trip = event.resource;
    let backgroundColor = '#D97706';

    if (trip.status === 'completed') {
      backgroundColor = '#6B7280';
    } else if (trip.status === 'ongoing') {
      backgroundColor = '#2563EB';
    }

    return {
      style: {
        backgroundColor,
        borderRadius: '6px',
        opacity: 0.9,
        color: 'white',
        border: 'none',
        display: 'block',
        fontWeight: '500',
        fontSize: '0.875rem',
      },
    };
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-slate-600">Cargando calendario...</div>
      </div>
    );
  }

  return (
    <div className="p-8 md:p-12" data-testid="calendar-page">
      <div className="mb-8">
        <h1
          className="text-4xl md:text-5xl font-bold text-slate-900 mb-2"
          style={{ fontFamily: 'Playfair Display, serif' }}
        >
          Calendario de Viajes
        </h1>
        <p className="text-slate-600">Visualiza todos los viajes programados</p>
      </div>

      <Card className="p-6 bg-white rounded-xl border border-slate-100 shadow-sm">
        <div style={{ height: '600px' }}>
          <BigCalendar
            localizer={localizer}
            events={events}
            startAccessor="start"
            endAccessor="end"
            onSelectEvent={handleSelectEvent}
            eventPropGetter={eventStyleGetter}
            views={['month', 'week', 'day', 'agenda']}
            defaultView="month"
            messages={{
              next: 'Siguiente',
              previous: 'Anterior',
              today: 'Hoy',
              month: 'Mes',
              week: 'Semana',
              day: 'Día',
              agenda: 'Agenda',
              date: 'Fecha',
              time: 'Hora',
              event: 'Viaje',
              noEventsInRange: 'No hay viajes en este rango',
              showMore: (total) => `+ Ver más (${total})`,
            }}
          />
        </div>
      </Card>

      <Dialog open={showDetailDialog} onOpenChange={setShowDetailDialog}>
        <DialogContent className="max-w-2xl">
          {selectedTrip && (
            <>
              <DialogHeader>
                <DialogTitle className="text-2xl" style={{ fontFamily: 'Playfair Display, serif' }}>
                  {selectedTrip.title}
                </DialogTitle>
              </DialogHeader>
              <div className="space-y-4 mt-4">
                <div className="flex items-center gap-3 p-4 bg-slate-50 rounded-lg">
                  <MapPin className="w-5 h-5 text-amber-600" />
                  <div>
                    <p className="text-sm text-slate-600">Destino</p>
                    <p className="font-semibold text-slate-900">{selectedTrip.destination}</p>
                  </div>
                </div>

                <div className="flex items-center gap-3 p-4 bg-slate-50 rounded-lg">
                  <CalendarIcon className="w-5 h-5 text-amber-600" />
                  <div>
                    <p className="text-sm text-slate-600">Fechas</p>
                    <p className="font-semibold text-slate-900">
                      {new Date(selectedTrip.start_date).toLocaleDateString('es-ES')} - {new Date(selectedTrip.end_date).toLocaleDateString('es-ES')}
                    </p>
                  </div>
                </div>

                {passengers[selectedTrip.passenger_id] && (
                  <div className="flex items-center gap-3 p-4 bg-slate-50 rounded-lg">
                    <User className="w-5 h-5 text-amber-600" />
                    <div>
                      <p className="text-sm text-slate-600">Pasajero</p>
                      <p className="font-semibold text-slate-900">{passengers[selectedTrip.passenger_id].full_name}</p>
                    </div>
                  </div>
                )}

                <div className="flex items-center gap-3 p-4 bg-slate-50 rounded-lg">
                  <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                    selectedTrip.status === 'upcoming' ? 'bg-amber-100 text-amber-800' :
                    selectedTrip.status === 'ongoing' ? 'bg-blue-100 text-blue-800' :
                    'bg-slate-200 text-slate-700'
                  }`}>
                    {selectedTrip.status === 'upcoming' ? 'Próximo' :
                     selectedTrip.status === 'ongoing' ? 'En curso' : 'Completado'}
                  </div>
                </div>

                {selectedTrip.notes && (
                  <div className="p-4 bg-slate-50 rounded-lg">
                    <p className="text-sm text-slate-600 mb-2">Notas</p>
                    <p className="text-slate-900">{selectedTrip.notes}</p>
                  </div>
                )}

                {selectedTrip.details && selectedTrip.details.length > 0 && (
                  <div className="p-4 bg-slate-50 rounded-lg">
                    <h3 className="text-sm font-semibold text-slate-900 mb-3">Detalles del Viaje</h3>
                    <div className="space-y-3">
                      {selectedTrip.details.map((detail, index) => (
                        <div key={index} className="flex items-start gap-3 p-3 bg-white rounded-lg border border-slate-200">
                          <Plane className="w-4 h-4 text-amber-600 mt-1" />
                          <div className="flex-1">
                            <div className="flex items-center justify-between mb-1">
                              <span className="font-medium text-slate-900">{detail.type}</span>
                              {detail.cost && (
                                <span className="text-sm font-semibold text-slate-900">${detail.cost}</span>
                              )}
                            </div>
                            <p className="text-sm text-slate-600">{detail.description}</p>
                            {detail.provider && (
                              <p className="text-xs text-slate-500 mt-1">Proveedor: {detail.provider}</p>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {selectedTrip.total_cost && (
                  <div className="p-4 bg-amber-50 rounded-lg border border-amber-200">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-slate-900">Costo Total</span>
                      <span className="text-2xl font-bold text-amber-800">${selectedTrip.total_cost}</span>
                    </div>
                  </div>
                )}

                <Button
                  onClick={() => setShowDetailDialog(false)}
                  className="w-full bg-slate-900 hover:bg-slate-800 text-white rounded-full mt-4"
                >
                  Cerrar
                </Button>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Calendar;
