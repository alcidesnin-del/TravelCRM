import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { Plane, Users, Calendar, MessageSquare, FileText, Check, ArrowRight, Phone } from "lucide-react";
import { toast } from "sonner";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const LandingPage = () => {
  const navigate = useNavigate();
  const [showContactForm, setShowContactForm] = useState(false);
  const [contactData, setContactData] = useState({
    name: "",
    email: "",
    phone: "",
    company: "",
    message: ""
  });
  const [loadingDemo, setLoadingDemo] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const features = [
    {
      icon: Users,
      title: "Gestión de Pasajeros",
      description: "Fichas completas con toda la información: pasaportes, contacto, preferencias y más."
    },
    {
      icon: MessageSquare,
      title: "Chat WhatsApp Integrado",
      description: "Comunica con tus clientes directamente desde el CRM. Historial completo de conversaciones."
    },
    {
      icon: Calendar,
      title: "Calendario de Viajes",
      description: "Visualiza todos los viajes en un calendario interactivo con detalles completos."
    },
    {
      icon: FileText,
      title: "Documentos en la Nube",
      description: "Almacena pasaportes, visas y documentos en Google Drive integrado."
    },
    {
      icon: Phone,
      title: "Registro de Llamadas",
      description: "Mantén historial de todas tus llamadas con notas y seguimiento."
    },
    {
      icon: Plane,
      title: "Detalles de Viaje",
      description: "Vuelos, hoteles, rent a car, seguros. Todo organizado en un solo lugar."
    }
  ];

  const benefits = [
    "✅ Ahorra tiempo con automatización",
    "✅ Mejora la comunicación con clientes",
    "✅ Organiza todos tus viajes",
    "✅ Acceso desde cualquier dispositivo",
    "✅ Sin instalación, 100% web",
    "✅ Soporte incluido"
  ];

  const handleTryDemo = async () => {
    setLoadingDemo(true);
    try {
      const response = await axios.post(`${API}/demo/reset`);
      const { credentials, token } = response.data;
      
      localStorage.setItem("token", token);
      axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
      
      toast.success("¡Bienvenido a la demo!");
      navigate("/dashboard");
    } catch (error) {
      toast.error("Error al cargar la demo. Inténtalo de nuevo.");
      console.error(error);
    } finally {
      setLoadingDemo(false);
    }
  };

  const handleContactSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await axios.post(`${API}/contact`, contactData);
      toast.success("¡Gracias! Te contactaremos pronto.");
      setShowContactForm(false);
      setContactData({ name: "", email: "", phone: "", company: "", message: "" });
    } catch (error) {
      toast.error("Error al enviar. Inténtalo de nuevo.");
      console.error(error);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Hero Section */}
      <section className="bg-slate-900 text-white py-20 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-amber-600 rounded-full mb-6">
              <Plane className="w-10 h-10 text-white" />
            </div>
            <h1
              className="text-5xl md:text-6xl lg:text-7xl font-bold mb-6"
              style={{ fontFamily: 'Playfair Display, serif' }}
            >
              TravelCRM
            </h1>
            <p className="text-xl md:text-2xl text-slate-300 mb-8 max-w-3xl mx-auto">
              El CRM completo para agentes de viajes modernos. Gestiona pasajeros, viajes y comunicaciones en un solo lugar.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button
                onClick={handleTryDemo}
                disabled={loadingDemo}
                data-testid="try-demo-button"
                className="bg-amber-600 hover:bg-amber-700 text-white rounded-full px-8 py-6 text-lg font-semibold shadow-lg hover:shadow-xl transition-all"
              >
                {loadingDemo ? "Cargando..." : "Probar Demo Gratis"}
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
              <Button
                onClick={() => setShowContactForm(true)}
                data-testid="contact-button"
                className="bg-white text-slate-900 hover:bg-slate-100 rounded-full px-8 py-6 text-lg font-semibold transition-all"
              >
                Solicitar Información
              </Button>
            </div>
            <p className="text-sm text-slate-400 mt-4">Sin tarjeta de crédito • Acceso instantáneo</p>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2
              className="text-4xl md:text-5xl font-bold text-slate-900 mb-4"
              style={{ fontFamily: 'Playfair Display, serif' }}
            >
              Todo lo que necesitas
            </h2>
            <p className="text-xl text-slate-600">Diseñado específicamente para agentes de viajes profesionales</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <Card
                key={index}
                className="p-8 bg-white rounded-xl border border-slate-100 shadow-sm hover:shadow-lg transition-all duration-300"
              >
                <div className="bg-amber-100 rounded-full w-14 h-14 flex items-center justify-center mb-4">
                  <feature.icon className="w-7 h-7 text-amber-600" />
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-2">{feature.title}</h3>
                <p className="text-slate-600">{feature.description}</p>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20 px-4 bg-white">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2
                className="text-4xl md:text-5xl font-bold text-slate-900 mb-6"
                style={{ fontFamily: 'Playfair Display, serif' }}
              >
                ¿Por qué TravelCRM?
              </h2>
              <p className="text-lg text-slate-600 mb-8">
                Diseñado pensando en tu flujo de trabajo. Simple, potente y profesional.
              </p>
              <div className="space-y-4">
                {benefits.map((benefit, index) => (
                  <div key={index} className="flex items-center gap-3">
                    <div className="bg-emerald-100 rounded-full w-8 h-8 flex items-center justify-center flex-shrink-0">
                      <Check className="w-5 h-5 text-emerald-600" />
                    </div>
                    <p className="text-lg text-slate-700">{benefit}</p>
                  </div>
                ))}
              </div>
            </div>
            <div className="bg-slate-900 rounded-2xl p-8 text-white">
              <h3
                className="text-3xl font-bold mb-4"
                style={{ fontFamily: 'Playfair Display, serif' }}
              >
                Comienza hoy mismo
              </h3>
              <p className="text-slate-300 mb-6">
                Prueba todas las funcionalidades con nuestra demo interactiva. Sin compromisos.
              </p>
              <ul className="space-y-3 mb-8">
                <li className="flex items-center gap-2">
                  <Check className="w-5 h-5 text-amber-500" />
                  <span>5 pasajeros de ejemplo</span>
                </li>
                <li className="flex items-center gap-2">
                  <Check className="w-5 h-5 text-amber-500" />
                  <span>Viajes pre-cargados</span>
                </li>
                <li className="flex items-center gap-2">
                  <Check className="w-5 h-5 text-amber-500" />
                  <span>Conversaciones WhatsApp de muestra</span>
                </li>
                <li className="flex items-center gap-2">
                  <Check className="w-5 h-5 text-amber-500" />
                  <span>Acceso completo a todas las funciones</span>
                </li>
              </ul>
              <Button
                onClick={handleTryDemo}
                disabled={loadingDemo}
                className="w-full bg-amber-600 hover:bg-amber-700 text-white rounded-full py-6 text-lg font-semibold"
              >
                {loadingDemo ? "Cargando Demo..." : "Acceder a la Demo"}
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-amber-50">
        <div className="max-w-4xl mx-auto text-center">
          <h2
            className="text-4xl md:text-5xl font-bold text-slate-900 mb-6"
            style={{ fontFamily: 'Playfair Display, serif' }}
          >
            ¿Listo para modernizar tu agencia?
          </h2>
          <p className="text-xl text-slate-600 mb-8">
            Únete a los agentes de viajes que están optimizando su trabajo con TravelCRM
          </p>
          <Button
            onClick={() => setShowContactForm(true)}
            className="bg-slate-900 hover:bg-slate-800 text-white rounded-full px-12 py-6 text-lg font-semibold shadow-lg hover:shadow-xl transition-all"
          >
            Solicitar Información
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 text-white py-12 px-4">
        <div className="max-w-6xl mx-auto text-center">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="bg-amber-600 rounded-full p-2">
              <Plane className="w-6 h-6 text-white" />
            </div>
            <h3
              className="text-2xl font-bold"
              style={{ fontFamily: 'Playfair Display, serif' }}
            >
              TravelCRM
            </h3>
          </div>
          <p className="text-slate-400">
            Sistema de Gestión para Agentes de Viajes
          </p>
          <p className="text-slate-500 text-sm mt-4">
            © 2025 TravelCRM. Todos los derechos reservados.
          </p>
        </div>
      </footer>

      {/* Contact Form Modal */}
      {showContactForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <Card className="max-w-2xl w-full p-8 bg-white rounded-xl relative max-h-[90vh] overflow-y-auto">
            <button
              onClick={() => setShowContactForm(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-slate-600"
            >
              ✕
            </button>
            <h2
              className="text-3xl font-bold text-slate-900 mb-6"
              style={{ fontFamily: 'Playfair Display, serif' }}
            >
              Solicitar Información
            </h2>
            <form onSubmit={handleContactSubmit} className="space-y-4">
              <div>
                <Label htmlFor="name">Nombre Completo *</Label>
                <Input
                  id="name"
                  value={contactData.name}
                  onChange={(e) => setContactData({ ...contactData, name: e.target.value })}
                  required
                  className="mt-2"
                  placeholder="Juan Pérez"
                />
              </div>
              <div>
                <Label htmlFor="email">Email *</Label>
                <Input
                  id="email"
                  type="email"
                  value={contactData.email}
                  onChange={(e) => setContactData({ ...contactData, email: e.target.value })}
                  required
                  className="mt-2"
                  placeholder="juan@agencia.com"
                />
              </div>
              <div>
                <Label htmlFor="phone">Teléfono</Label>
                <Input
                  id="phone"
                  value={contactData.phone}
                  onChange={(e) => setContactData({ ...contactData, phone: e.target.value })}
                  className="mt-2"
                  placeholder="+34 600 123 456"
                />
              </div>
              <div>
                <Label htmlFor="company">Nombre de la Agencia</Label>
                <Input
                  id="company"
                  value={contactData.company}
                  onChange={(e) => setContactData({ ...contactData, company: e.target.value })}
                  className="mt-2"
                  placeholder="Viajes Globales S.L."
                />
              </div>
              <div>
                <Label htmlFor="message">Mensaje</Label>
                <textarea
                  id="message"
                  value={contactData.message}
                  onChange={(e) => setContactData({ ...contactData, message: e.target.value })}
                  className="mt-2 w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:border-slate-900 focus:ring-1 focus:ring-slate-900"
                  rows="4"
                  placeholder="Cuéntanos sobre tu agencia y tus necesidades..."
                />
              </div>
              <Button
                type="submit"
                disabled={submitting}
                className="w-full bg-slate-900 hover:bg-slate-800 text-white rounded-full py-6 text-lg font-semibold"
              >
                {submitting ? "Enviando..." : "Enviar Solicitud"}
              </Button>
            </form>
          </Card>
        </div>
      )}
    </div>
  );
};

export default LandingPage;
