import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { toast } from "sonner";
import { Plane } from "lucide-react";

const Login = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);
  const { login, register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (isLogin) {
        await login(email, password);
        toast.success("¡Bienvenido de vuelta!");
      } else {
        await register(email, password, name);
        toast.success("¡Cuenta creada exitosamente!");
      }
      navigate("/app/dashboard");
    } catch (error) {
      toast.error(
        error.response?.data?.detail || "Error en la autenticación"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-amber-600 rounded-full mb-4">
            <Plane className="w-8 h-8 text-white" />
          </div>
          <h1
            className="text-4xl font-bold text-white mb-2"
            style={{ fontFamily: 'Playfair Display, serif' }}
          >
            TravelCRM
          </h1>
          <p className="text-slate-400">Sistema de Gestión para Agentes de Viajes</p>
        </div>

        <Card className="p-8 bg-white rounded-xl shadow-2xl">
          <form onSubmit={handleSubmit} className="space-y-6">
            {!isLogin && (
              <div>
                <Label htmlFor="name" className="text-slate-700">
                  Nombre Completo
                </Label>
                <Input
                  id="name"
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required={!isLogin}
                  data-testid="name-input"
                  className="mt-2 bg-slate-50 border-slate-200 focus:border-slate-900 focus:ring-slate-900"
                  placeholder="Juan Pérez"
                />
              </div>
            )}

            <div>
              <Label htmlFor="email" className="text-slate-700">
                Email
              </Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                data-testid="email-input"
                className="mt-2 bg-slate-50 border-slate-200 focus:border-slate-900 focus:ring-slate-900"
                placeholder="tu@email.com"
              />
            </div>

            <div>
              <Label htmlFor="password" className="text-slate-700">
                Contraseña
              </Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                data-testid="password-input"
                className="mt-2 bg-slate-50 border-slate-200 focus:border-slate-900 focus:ring-slate-900"
                placeholder="••••••••"
              />
            </div>

            <Button
              type="submit"
              disabled={loading}
              data-testid="submit-button"
              className="w-full bg-slate-900 hover:bg-slate-800 text-white rounded-full py-6 font-medium text-lg transition-all shadow-lg hover:shadow-xl"
            >
              {loading ? "Procesando..." : isLogin ? "Iniciar Sesión" : "Registrarse"}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <button
              type="button"
              onClick={() => setIsLogin(!isLogin)}
              data-testid="toggle-auth-mode"
              className="text-slate-600 hover:text-slate-900 font-medium transition-colors"
            >
              {isLogin
                ? "¿No tienes cuenta? Regístrate"
                : "¿Ya tienes cuenta? Inicia sesión"}
            </button>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Login;
