import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { ArrowLeft, Edit, Trash2, Phone, Upload, FileText, Plus, Image, Calendar, MapPin } from "lucide-react";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PassengerDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [passenger, setPassenger] = useState(null);
  const [calls, setCalls] = useState([]);
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [showCallDialog, setShowCallDialog] = useState(false);
  const [showTripDialog, setShowTripDialog] = useState(false);
  const [driveConnected, setDriveConnected] = useState(false);
  const [uploadingFile, setUploadingFile] = useState(false);
  const [formData, setFormData] = useState({});
  const [callData, setCallData] = useState({
    call_date: new Date().toISOString().split('T')[0],
    duration: "",
    notes: "",
  });
  const [tripData, setTripData] = useState({
    title: "",
    destination: "",
    start_date: "",
    end_date: "",
    status: "upcoming",
    notes: "",
    details: [],
  });

  useEffect(() => {
    fetchPassengerData();
    checkDriveStatus();
  }, [id]);

  const fetchPassengerData = async () => {
    try {
      const [passengerRes, callsRes, tripsRes] = await Promise.all([
        axios.get(`${API}/passengers/${id}`),
        axios.get(`${API}/calls?passenger_id=${id}`),
        axios.get(`${API}/trips?passenger_id=${id}`),
      ]);
      setPassenger(passengerRes.data);
      setFormData(passengerRes.data);
      setCalls(callsRes.data);
      setTrips(tripsRes.data);
    } catch (error) {
      toast.error("Error al cargar datos del pasajero");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const checkDriveStatus = async () => {
    try {
      const response = await axios.get(`${API}/drive/status`);
      setDriveConnected(response.data.connected);
    } catch (error) {
      console.error(error);
    }
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    try {
      await axios.put(`${API}/passengers/${id}`, formData);
      toast.success("Pasajero actualizado exitosamente");
      setShowEditDialog(false);
      fetchPassengerData();
    } catch (error) {
      toast.error("Error al actualizar pasajero");
      console.error(error);
    }
  };

  const handleDelete = async () => {
    if (window.confirm("¿Estás seguro de eliminar este pasajero?")) {
      try {
        await axios.delete(`${API}/passengers/${id}`);
        toast.success("Pasajero eliminado exitosamente");
        navigate("/passengers");
      } catch (error) {
        toast.error("Error al eliminar pasajero");
        console.error(error);
      }
    }
  };

  const handleAddCall = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/calls`, { ...callData, passenger_id: id });
      toast.success("Llamada registrada exitosamente");
      setShowCallDialog(false);
      setCallData({ call_date: new Date().toISOString().split('T')[0], duration: "", notes: "" });
      fetchPassengerData();
    } catch (error) {
      toast.error("Error al registrar llamada");
      console.error(error);
    }
  };

  const handleAddTrip = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/trips`, { ...tripData, passenger_id: id });
      toast.success("Viaje creado exitosamente");
      setShowTripDialog(false);
      setTripData({ title: "", destination: "", start_date: "", end_date: "", status: "upcoming", notes: "", details: [] });
      fetchPassengerData();
    } catch (error) {
      toast.error("Error al crear viaje");
      console.error(error);
    }
  };

  const connectDrive = async () => {
    try {
      const response = await axios.get(`${API}/drive/connect`);
      window.location.href = response.data.authorization_url;
    } catch (error) {
      toast.error("Error al conectar con Google Drive");
      console.error(error);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploadingFile(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      await axios.post(`${API}/drive/upload/${id}`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      toast.success("Archivo subido exitosamente");
      fetchPassengerData();
    } catch (error) {
      if (error.response?.status === 400 && error.response?.data?.detail?.includes("not connected")) {
        toast.error("Por favor conecta tu cuenta de Google Drive primero");
      } else {
        toast.error("Error al subir archivo");
      }
      console.error(error);
    } finally {
      setUploadingFile(false);
    }
  };

  const handleDeleteDocument = async (fileId) => {
    if (window.confirm("¿Estás seguro de eliminar este documento?")) {
      try {
        await axios.delete(`${API}/drive/files/${fileId}?passenger_id=${id}`);
        toast.success("Documento eliminado exitosamente");
        fetchPassengerData();
      } catch (error) {
        toast.error("Error al eliminar documento");
        console.error(error);
      }
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-slate-600">Cargando...</div>
      </div>
    );
  }

  if (!passenger) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-slate-600">Pasajero no encontrado</div>
      </div>
    );
  }

  return (
    <div className="p-8 md:p-12">
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-4">
          <Button
            onClick={() => navigate("/passengers")}
            className="bg-white border border-slate-200 text-slate-900 hover:bg-slate-50 rounded-full"
            data-testid="back-button"
          >
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div>
            <h1
              className="text-4xl md:text-5xl font-bold text-slate-900"
              style={{ fontFamily: 'Playfair Display, serif' }}
            >
              {passenger.full_name}
            </h1>
            <p className="text-slate-600 mt-1">Información completa del pasajero</p>
          </div>
        </div>
        <div className="flex gap-3">
          <Dialog open={showEditDialog} onOpenChange={setShowEditDialog}>
            <DialogTrigger asChild>
              <Button
                data-testid="edit-passenger-button"
                className="bg-amber-600 hover:bg-amber-700 text-white rounded-full"
              >
                <Edit className="w-5 h-5 mr-2" />
                Editar
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle className="text-2xl" style={{ fontFamily: 'Playfair Display, serif' }}>
                  Editar Pasajero
                </DialogTitle>
              </DialogHeader>
              <form onSubmit={handleUpdate} className="space-y-4 mt-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="col-span-2">
                    <Label htmlFor="full_name">Nombre Completo</Label>
                    <Input
                      id="full_name"
                      value={formData.full_name || ""}
                      onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                      className="mt-2 bg-slate-50"
                    />
                  </div>
                  <div>
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      value={formData.email || ""}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      className="mt-2 bg-slate-50"
                    />
                  </div>
                  <div>
                    <Label htmlFor="phone">Teléfono</Label>
                    <Input
                      id="phone"
                      value={formData.phone || ""}
                      onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                      className="mt-2 bg-slate-50"
                    />
                  </div>
                  <div>
                    <Label htmlFor="passport_number">Número de Pasaporte</Label>
                    <Input
                      id="passport_number"
                      value={formData.passport_number || ""}
                      onChange={(e) => setFormData({ ...formData, passport_number: e.target.value })}
                      className="mt-2 bg-slate-50"
                    />
                  </div>
                  <div>
                    <Label htmlFor="passport_expiry">Vencimiento</Label>
                    <Input
                      id="passport_expiry"
                      type="date"
                      value={formData.passport_expiry || ""}
                      onChange={(e) => setFormData({ ...formData, passport_expiry: e.target.value })}
                      className="mt-2 bg-slate-50"
                    />
                  </div>
                  <div>
                    <Label htmlFor="date_of_birth">Fecha de Nacimiento</Label>
                    <Input
                      id="date_of_birth"
                      type="date"
                      value={formData.date_of_birth || ""}
                      onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
                      className="mt-2 bg-slate-50"
                    />
                  </div>
                  <div>
                    <Label htmlFor="nationality">Nacionalidad</Label>
                    <Input
                      id="nationality"
                      value={formData.nationality || ""}
                      onChange={(e) => setFormData({ ...formData, nationality: e.target.value })}
                      className="mt-2 bg-slate-50"
                    />
                  </div>
                  <div className="col-span-2">
                    <Label htmlFor="address">Dirección</Label>
                    <Input
                      id="address"
                      value={formData.address || ""}
                      onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                      className="mt-2 bg-slate-50"
                    />
                  </div>
                </div>
                <div className="flex gap-3 justify-end">
                  <Button
                    type="button"
                    onClick={() => setShowEditDialog(false)}
                    className="bg-white border border-slate-200 text-slate-900 hover:bg-slate-50 rounded-full"
                  >
                    Cancelar
                  </Button>
                  <Button
                    type="submit"
                    className="bg-slate-900 hover:bg-slate-800 text-white rounded-full"
                  >
                    Guardar Cambios
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
          <Button
            onClick={handleDelete}
            data-testid="delete-passenger-button"
            className="bg-red-600 hover:bg-red-700 text-white rounded-full"
          >
            <Trash2 className="w-5 h-5 mr-2" />
            Eliminar
          </Button>
        </div>
      </div>

      <Tabs defaultValue="info" className="space-y-6">
        <TabsList className="bg-white border border-slate-200 p-1 rounded-lg">
          <TabsTrigger value="info" data-testid="tab-info" className="rounded-md data-[state=active]:bg-slate-900 data-[state=active]:text-white">
            Información
          </TabsTrigger>
          <TabsTrigger value="documents" data-testid="tab-documents" className="rounded-md data-[state=active]:bg-slate-900 data-[state=active]:text-white">
            Documentos
          </TabsTrigger>
          <TabsTrigger value="calls" data-testid="tab-calls" className="rounded-md data-[state=active]:bg-slate-900 data-[state=active]:text-white">
            Llamadas
          </TabsTrigger>
          <TabsTrigger value="trips" data-testid="tab-trips" className="rounded-md data-[state=active]:bg-slate-900 data-[state=active]:text-white">
            Viajes
          </TabsTrigger>
        </TabsList>

        <TabsContent value="info">
          <Card className="p-8 bg-white rounded-xl border border-slate-100 shadow-sm">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <Label className="text-slate-600">Email</Label>
                <p className="mt-1 text-lg font-medium text-slate-900">{passenger.email || "No especificado"}</p>
              </div>
              <div>
                <Label className="text-slate-600">Teléfono</Label>
                <p className="mt-1 text-lg font-medium text-slate-900">{passenger.phone || "No especificado"}</p>
              </div>
              <div>
                <Label className="text-slate-600">Número de Pasaporte</Label>
                <p className="mt-1 text-lg font-medium font-mono text-slate-900">{passenger.passport_number || "No especificado"}</p>
              </div>
              <div>
                <Label className="text-slate-600">Vencimiento Pasaporte</Label>
                <p className="mt-1 text-lg font-medium text-slate-900">
                  {passenger.passport_expiry ? new Date(passenger.passport_expiry).toLocaleDateString('es-ES') : "No especificado"}
                </p>
              </div>
              <div>
                <Label className="text-slate-600">Fecha de Nacimiento</Label>
                <p className="mt-1 text-lg font-medium text-slate-900">
                  {passenger.date_of_birth ? new Date(passenger.date_of_birth).toLocaleDateString('es-ES') : "No especificado"}
                </p>
              </div>
              <div>
                <Label className="text-slate-600">Nacionalidad</Label>
                <p className="mt-1 text-lg font-medium text-slate-900">{passenger.nationality || "No especificado"}</p>
              </div>
              <div className="col-span-2">
                <Label className="text-slate-600">Dirección</Label>
                <p className="mt-1 text-lg font-medium text-slate-900">{passenger.address || "No especificado"}</p>
              </div>
              {passenger.notes && (
                <div className="col-span-2">
                  <Label className="text-slate-600">Notas</Label>
                  <p className="mt-1 text-slate-900">{passenger.notes}</p>
                </div>
              )}
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="documents">
          <Card className="p-8 bg-white rounded-xl border border-slate-100 shadow-sm">
            <div className="flex items-center justify-between mb-6">
              <h2
                className="text-2xl font-bold text-slate-900"
                style={{ fontFamily: 'Playfair Display, serif' }}
              >
                Documentos
              </h2>
              <div className="flex gap-3">
                {!driveConnected && (
                  <Button
                    onClick={connectDrive}
                    data-testid="connect-drive-button"
                    className="bg-blue-600 hover:bg-blue-700 text-white rounded-full"
                  >
                    Conectar Google Drive
                  </Button>
                )}
                {driveConnected && (
                  <>
                    <input
                      type="file"
                      id="file-upload"
                      className="hidden"
                      onChange={handleFileUpload}
                      disabled={uploadingFile}
                    />
                    <Button
                      onClick={() => document.getElementById('file-upload').click()}
                      disabled={uploadingFile}
                      data-testid="upload-document-button"
                      className="bg-slate-900 hover:bg-slate-800 text-white rounded-full"
                    >
                      <Upload className="w-5 h-5 mr-2" />
                      {uploadingFile ? "Subiendo..." : "Subir Documento"}
                    </Button>
                  </>
                )}
              </div>
            </div>

            {passenger.documents && passenger.documents.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {passenger.documents.map((doc) => (
                  <div
                    key={doc.id}
                    className="p-4 bg-slate-50 rounded-lg border border-slate-200 hover:border-amber-600 transition-colors"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        {doc.mimeType?.includes('image') ? (
                          <Image className="w-5 h-5 text-amber-600" />
                        ) : (
                          <FileText className="w-5 h-5 text-slate-600" />
                        )}
                        <span className="font-medium text-slate-900 text-sm truncate">{doc.name}</span>
                      </div>
                      <Button
                        size="sm"
                        onClick={() => handleDeleteDocument(doc.id)}
                        className="bg-red-600 hover:bg-red-700 text-white h-7 w-7 p-0 rounded-full"
                      >
                        <Trash2 className="w-3 h-3" />
                      </Button>
                    </div>
                    <p className="text-xs text-slate-500 mb-2">
                      {new Date(doc.uploaded_at).toLocaleDateString('es-ES')}
                    </p>
                    {doc.webViewLink && (
                      <a
                        href={doc.webViewLink}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-blue-600 hover:text-blue-700 hover:underline"
                      >
                        Ver en Drive
                      </a>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <FileText className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                <p className="text-slate-600">No hay documentos subidos</p>
                {!driveConnected && (
                  <p className="text-sm text-slate-500 mt-2">Conecta Google Drive para subir documentos</p>
                )}
              </div>
            )}
          </Card>
        </TabsContent>

        <TabsContent value="calls">
          <Card className="p-8 bg-white rounded-xl border border-slate-100 shadow-sm">
            <div className="flex items-center justify-between mb-6">
              <h2
                className="text-2xl font-bold text-slate-900"
                style={{ fontFamily: 'Playfair Display, serif' }}
              >
                Historial de Llamadas
              </h2>
              <Dialog open={showCallDialog} onOpenChange={setShowCallDialog}>
                <DialogTrigger asChild>
                  <Button
                    data-testid="add-call-button"
                    className="bg-slate-900 hover:bg-slate-800 text-white rounded-full"
                  >
                    <Plus className="w-5 h-5 mr-2" />
                    Registrar Llamada
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle className="text-2xl" style={{ fontFamily: 'Playfair Display, serif' }}>
                      Registrar Nueva Llamada
                    </DialogTitle>
                  </DialogHeader>
                  <form onSubmit={handleAddCall} className="space-y-4 mt-4">
                    <div>
                      <Label htmlFor="call_date">Fecha</Label>
                      <Input
                        id="call_date"
                        type="date"
                        value={callData.call_date}
                        onChange={(e) => setCallData({ ...callData, call_date: e.target.value })}
                        required
                        className="mt-2 bg-slate-50"
                      />
                    </div>
                    <div>
                      <Label htmlFor="duration">Duración (minutos)</Label>
                      <Input
                        id="duration"
                        type="number"
                        value={callData.duration}
                        onChange={(e) => setCallData({ ...callData, duration: e.target.value })}
                        className="mt-2 bg-slate-50"
                      />
                    </div>
                    <div>
                      <Label htmlFor="notes">Notas</Label>
                      <textarea
                        id="notes"
                        value={callData.notes}
                        onChange={(e) => setCallData({ ...callData, notes: e.target.value })}
                        className="mt-2 w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg"
                        rows="4"
                      />
                    </div>
                    <div className="flex gap-3 justify-end">
                      <Button
                        type="button"
                        onClick={() => setShowCallDialog(false)}
                        className="bg-white border border-slate-200 text-slate-900 hover:bg-slate-50 rounded-full"
                      >
                        Cancelar
                      </Button>
                      <Button
                        type="submit"
                        data-testid="save-call-button"
                        className="bg-slate-900 hover:bg-slate-800 text-white rounded-full"
                      >
                        Guardar Llamada
                      </Button>
                    </div>
                  </form>
                </DialogContent>
              </Dialog>
            </div>

            {calls.length > 0 ? (
              <div className="space-y-3">
                {calls.map((call) => (
                  <div
                    key={call.id}
                    className="p-4 bg-slate-50 rounded-lg border border-slate-200"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Phone className="w-5 h-5 text-amber-600" />
                        <span className="font-medium text-slate-900">
                          {new Date(call.call_date).toLocaleDateString('es-ES')}
                        </span>
                      </div>
                      {call.duration && (
                        <span className="text-sm text-slate-600">{call.duration} minutos</span>
                      )}
                    </div>
                    {call.notes && (
                      <p className="text-slate-600 text-sm">{call.notes}</p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <Phone className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                <p className="text-slate-600">No hay llamadas registradas</p>
              </div>
            )}
          </Card>
        </TabsContent>

        <TabsContent value="trips">
          <Card className="p-8 bg-white rounded-xl border border-slate-100 shadow-sm">
            <div className="flex items-center justify-between mb-6">
              <h2
                className="text-2xl font-bold text-slate-900"
                style={{ fontFamily: 'Playfair Display, serif' }}
              >
                Historial de Viajes
              </h2>
              <Dialog open={showTripDialog} onOpenChange={setShowTripDialog}>
                <DialogTrigger asChild>
                  <Button
                    data-testid="add-trip-button"
                    className="bg-slate-900 hover:bg-slate-800 text-white rounded-full"
                  >
                    <Plus className="w-5 h-5 mr-2" />
                    Nuevo Viaje
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-2xl">
                  <DialogHeader>
                    <DialogTitle className="text-2xl" style={{ fontFamily: 'Playfair Display, serif' }}>
                      Crear Nuevo Viaje
                    </DialogTitle>
                  </DialogHeader>
                  <form onSubmit={handleAddTrip} className="space-y-4 mt-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="col-span-2">
                        <Label htmlFor="title">Título del Viaje</Label>
                        <Input
                          id="title"
                          value={tripData.title}
                          onChange={(e) => setTripData({ ...tripData, title: e.target.value })}
                          required
                          className="mt-2 bg-slate-50"
                          placeholder="Ej: Vacaciones en Europa"
                        />
                      </div>
                      <div className="col-span-2">
                        <Label htmlFor="destination">Destino</Label>
                        <Input
                          id="destination"
                          value={tripData.destination}
                          onChange={(e) => setTripData({ ...tripData, destination: e.target.value })}
                          required
                          className="mt-2 bg-slate-50"
                          placeholder="Ej: París, Francia"
                        />
                      </div>
                      <div>
                        <Label htmlFor="start_date">Fecha de Inicio</Label>
                        <Input
                          id="start_date"
                          type="date"
                          value={tripData.start_date}
                          onChange={(e) => setTripData({ ...tripData, start_date: e.target.value })}
                          required
                          className="mt-2 bg-slate-50"
                        />
                      </div>
                      <div>
                        <Label htmlFor="end_date">Fecha de Finalización</Label>
                        <Input
                          id="end_date"
                          type="date"
                          value={tripData.end_date}
                          onChange={(e) => setTripData({ ...tripData, end_date: e.target.value })}
                          required
                          className="mt-2 bg-slate-50"
                        />
                      </div>
                      <div className="col-span-2">
                        <Label htmlFor="notes">Notas</Label>
                        <textarea
                          id="notes"
                          value={tripData.notes}
                          onChange={(e) => setTripData({ ...tripData, notes: e.target.value })}
                          className="mt-2 w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg"
                          rows="3"
                        />
                      </div>
                    </div>
                    <div className="flex gap-3 justify-end">
                      <Button
                        type="button"
                        onClick={() => setShowTripDialog(false)}
                        className="bg-white border border-slate-200 text-slate-900 hover:bg-slate-50 rounded-full"
                      >
                        Cancelar
                      </Button>
                      <Button
                        type="submit"
                        data-testid="save-trip-button"
                        className="bg-slate-900 hover:bg-slate-800 text-white rounded-full"
                      >
                        Crear Viaje
                      </Button>
                    </div>
                  </form>
                </DialogContent>
              </Dialog>
            </div>

            {trips.length > 0 ? (
              <div className="space-y-4">
                {trips.map((trip) => (
                  <div
                    key={trip.id}
                    className="p-6 bg-slate-50 rounded-lg border border-slate-200 hover:border-amber-600 transition-colors cursor-pointer"
                    onClick={() => navigate(`/calendar?trip=${trip.id}`)}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="text-lg font-semibold text-slate-900">{trip.title}</h3>
                        <div className="flex items-center gap-2 text-slate-600 mt-1">
                          <MapPin className="w-4 h-4" />
                          <span>{trip.destination}</span>
                        </div>
                      </div>
                      <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                        trip.status === 'upcoming' ? 'bg-amber-100 text-amber-800' :
                        trip.status === 'ongoing' ? 'bg-blue-100 text-blue-800' :
                        'bg-slate-200 text-slate-700'
                      }`}>
                        {trip.status === 'upcoming' ? 'Próximo' :
                         trip.status === 'ongoing' ? 'En curso' : 'Completado'}
                      </div>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-slate-600">
                      <div className="flex items-center gap-2">
                        <Calendar className="w-4 h-4" />
                        <span>
                          {new Date(trip.start_date).toLocaleDateString('es-ES')} - {new Date(trip.end_date).toLocaleDateString('es-ES')}
                        </span>
                      </div>
                    </div>
                    {trip.notes && (
                      <p className="text-sm text-slate-600 mt-3 line-clamp-2">{trip.notes}</p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <MapPin className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                <p className="text-slate-600">No hay viajes registrados</p>
              </div>
            )}
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default PassengerDetail;
