import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Plus, Search, User, Phone, Mail } from "lucide-react";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Passengers = () => {
  const [passengers, setPassengers] = useState([]);
  const [filteredPassengers, setFilteredPassengers] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(true);
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [formData, setFormData] = useState({
    full_name: "",
    email: "",
    phone: "",
    passport_number: "",
    passport_expiry: "",
    date_of_birth: "",
    nationality: "",
    address: "",
    notes: "",
  });
  const navigate = useNavigate();

  useEffect(() => {
    fetchPassengers();
  }, []);

  useEffect(() => {
    const filtered = passengers.filter((p) =>
      p.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.passport_number?.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredPassengers(filtered);
  }, [searchTerm, passengers]);

  const fetchPassengers = async () => {
    try {
      const response = await axios.get(`${API}/passengers`);
      setPassengers(response.data);
      setFilteredPassengers(response.data);
    } catch (error) {
      toast.error("Error al cargar pasajeros");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/passengers`, formData);
      toast.success("Pasajero creado exitosamente");
      setShowAddDialog(false);
      setFormData({
        full_name: "",
        email: "",
        phone: "",
        passport_number: "",
        passport_expiry: "",
        date_of_birth: "",
        nationality: "",
        address: "",
        notes: "",
      });
      fetchPassengers();
    } catch (error) {
      toast.error("Error al crear pasajero");
      console.error(error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-slate-600">Cargando...</div>
      </div>
    );
  }

  return (
    <div className="p-8 md:p-12">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1
            className="text-4xl md:text-5xl font-bold text-slate-900 mb-2"
            style={{ fontFamily: 'Playfair Display, serif' }}
          >
            Pasajeros
          </h1>
          <p className="text-slate-600">Gestión completa de tus clientes</p>
        </div>
        <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
          <DialogTrigger asChild>
            <Button
              data-testid="add-passenger-button"
              className="bg-slate-900 hover:bg-slate-800 text-white rounded-full px-6 py-6 font-medium shadow-lg hover:shadow-xl transition-all"
            >
              <Plus className="w-5 h-5 mr-2" />
              Nuevo Pasajero
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="text-2xl" style={{ fontFamily: 'Playfair Display, serif' }}>
                Agregar Nuevo Pasajero
              </DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4 mt-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                  <Label htmlFor="full_name">Nombre Completo *</Label>
                  <Input
                    id="full_name"
                    value={formData.full_name}
                    onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                    required
                    data-testid="passenger-name-input"
                    className="mt-2 bg-slate-50 border-slate-200"
                  />
                </div>
                <div>
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    data-testid="passenger-email-input"
                    className="mt-2 bg-slate-50 border-slate-200"
                  />
                </div>
                <div>
                  <Label htmlFor="phone">Teléfono</Label>
                  <Input
                    id="phone"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    data-testid="passenger-phone-input"
                    className="mt-2 bg-slate-50 border-slate-200"
                  />
                </div>
                <div>
                  <Label htmlFor="passport_number">Número de Pasaporte</Label>
                  <Input
                    id="passport_number"
                    value={formData.passport_number}
                    onChange={(e) => setFormData({ ...formData, passport_number: e.target.value })}
                    data-testid="passenger-passport-input"
                    className="mt-2 bg-slate-50 border-slate-200"
                  />
                </div>
                <div>
                  <Label htmlFor="passport_expiry">Vencimiento Pasaporte</Label>
                  <Input
                    id="passport_expiry"
                    type="date"
                    value={formData.passport_expiry}
                    onChange={(e) => setFormData({ ...formData, passport_expiry: e.target.value })}
                    className="mt-2 bg-slate-50 border-slate-200"
                  />
                </div>
                <div>
                  <Label htmlFor="date_of_birth">Fecha de Nacimiento</Label>
                  <Input
                    id="date_of_birth"
                    type="date"
                    value={formData.date_of_birth}
                    onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
                    className="mt-2 bg-slate-50 border-slate-200"
                  />
                </div>
                <div>
                  <Label htmlFor="nationality">Nacionalidad</Label>
                  <Input
                    id="nationality"
                    value={formData.nationality}
                    onChange={(e) => setFormData({ ...formData, nationality: e.target.value })}
                    className="mt-2 bg-slate-50 border-slate-200"
                  />
                </div>
                <div className="col-span-2">
                  <Label htmlFor="address">Dirección</Label>
                  <Input
                    id="address"
                    value={formData.address}
                    onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                    className="mt-2 bg-slate-50 border-slate-200"
                  />
                </div>
                <div className="col-span-2">
                  <Label htmlFor="notes">Notas</Label>
                  <textarea
                    id="notes"
                    value={formData.notes}
                    onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                    className="mt-2 w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:border-slate-900 focus:ring-1 focus:ring-slate-900"
                    rows="3"
                  />
                </div>
              </div>
              <div className="flex gap-3 justify-end">
                <Button
                  type="button"
                  onClick={() => setShowAddDialog(false)}
                  className="bg-white border border-slate-200 text-slate-900 hover:bg-slate-50 rounded-full"
                >
                  Cancelar
                </Button>
                <Button
                  type="submit"
                  data-testid="save-passenger-button"
                  className="bg-slate-900 hover:bg-slate-800 text-white rounded-full"
                >
                  Guardar Pasajero
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Card className="p-6 bg-white rounded-xl border border-slate-100 shadow-sm mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          <Input
            placeholder="Buscar pasajeros por nombre, email o pasaporte..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            data-testid="search-passengers-input"
            className="pl-10 bg-slate-50 border-slate-200"
          />
        </div>
      </Card>

      {filteredPassengers.length === 0 ? (
        <Card className="p-12 bg-white rounded-xl border border-slate-100 shadow-sm text-center">
          <User className="w-16 h-16 text-slate-300 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-slate-900 mb-2">No hay pasajeros</h3>
          <p className="text-slate-600">Comienza agregando tu primer pasajero</p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredPassengers.map((passenger) => (
            <Card
              key={passenger.id}
              data-testid={`passenger-card-${passenger.id}`}
              className="p-6 bg-white rounded-xl border border-slate-100 shadow-sm hover:shadow-lg transition-all duration-300 cursor-pointer"
              onClick={() => navigate(`/passengers/${passenger.id}`)}
            >
              <div className="flex items-start gap-4">
                <div className="bg-slate-900 rounded-full p-3">
                  <User className="w-6 h-6 text-white" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-lg text-slate-900 mb-2">
                    {passenger.full_name}
                  </h3>
                  {passenger.email && (
                    <div className="flex items-center gap-2 text-sm text-slate-600 mb-1">
                      <Mail className="w-4 h-4" />
                      <span className="truncate">{passenger.email}</span>
                    </div>
                  )}
                  {passenger.phone && (
                    <div className="flex items-center gap-2 text-sm text-slate-600 mb-1">
                      <Phone className="w-4 h-4" />
                      <span>{passenger.phone}</span>
                    </div>
                  )}
                  {passenger.passport_number && (
                    <div className="mt-2 text-xs font-mono bg-amber-50 text-amber-800 px-2 py-1 rounded inline-block">
                      {passenger.passport_number}
                    </div>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default Passengers;
