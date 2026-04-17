import { useState, useRef } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Camera, Loader2, CheckCircle, AlertCircle, Upload } from "lucide-react";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DocumentScanner = ({ onDataExtracted, className = "" }) => {
  const [scanning, setScanning] = useState(false);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileSelect = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const validTypes = ["image/jpeg", "image/png", "image/webp"];
    if (!validTypes.includes(file.type)) {
      toast.error("Formato no soportado. Usa JPG, PNG o WEBP.");
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      toast.error("La imagen es demasiado grande (máx 10MB).");
      return;
    }

    const reader = new FileReader();
    reader.onload = (ev) => setPreview(ev.target.result);
    reader.readAsDataURL(file);

    setScanning(true);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await axios.post(`${API}/ocr/scan`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 30000,
      });

      if (response.data.success) {
        setResult({ success: true, data: response.data.data });
        toast.success("Datos extraídos del documento");
      } else {
        setResult({ success: false, message: response.data.message });
        toast.error(response.data.message);
      }
    } catch (error) {
      const msg = error.response?.data?.detail || "Error al escanear documento";
      setResult({ success: false, message: msg });
      toast.error(msg);
    } finally {
      setScanning(false);
    }
  };

  const applyData = () => {
    if (result?.data) {
      onDataExtracted(result.data);
      toast.success("Datos aplicados al formulario");
      resetScanner();
    }
  };

  const resetScanner = () => {
    setPreview(null);
    setResult(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  return (
    <div className={`${className}`}>
      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        onChange={handleFileSelect}
        className="hidden"
        data-testid="ocr-file-input"
      />

      {!preview ? (
        <div
          onClick={() => fileInputRef.current?.click()}
          data-testid="ocr-upload-zone"
          className="border-2 border-dashed border-slate-300 rounded-xl p-6 text-center cursor-pointer hover:border-amber-500 hover:bg-amber-50/30 transition-all group"
        >
          <div className="bg-amber-100 rounded-full p-3 w-fit mx-auto mb-3 group-hover:bg-amber-200 transition-colors">
            <Camera className="w-6 h-6 text-amber-700" />
          </div>
          <p className="text-sm font-medium text-slate-700">
            Escanear Pasaporte o Carnet
          </p>
          <p className="text-xs text-slate-500 mt-1">
            Sube una foto y extraeremos los datos automáticamente
          </p>
          <p className="text-xs text-slate-400 mt-1">JPG, PNG o WEBP (máx 10MB)</p>
        </div>
      ) : (
        <div className="space-y-3">
          <div className="relative rounded-xl overflow-hidden border border-slate-200">
            <img
              src={preview}
              alt="Documento"
              className="w-full h-40 object-cover"
              data-testid="ocr-preview-image"
            />
            {scanning && (
              <div className="absolute inset-0 bg-slate-900/60 flex items-center justify-center">
                <div className="text-center">
                  <Loader2 className="w-8 h-8 text-white animate-spin mx-auto mb-2" />
                  <p className="text-white text-sm font-medium">Escaneando documento...</p>
                </div>
              </div>
            )}
          </div>

          {result && (
            <div
              data-testid="ocr-result"
              className={`p-4 rounded-lg border ${
                result.success
                  ? "bg-emerald-50 border-emerald-200"
                  : "bg-red-50 border-red-200"
              }`}
            >
              {result.success ? (
                <>
                  <div className="flex items-center gap-2 mb-3">
                    <CheckCircle className="w-4 h-4 text-emerald-600" />
                    <span className="text-sm font-medium text-emerald-700">
                      Datos extraídos correctamente
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    {result.data.full_name && (
                      <div>
                        <span className="text-slate-500">Nombre:</span>{" "}
                        <span className="font-medium text-slate-800">{result.data.full_name}</span>
                      </div>
                    )}
                    {result.data.passport_number && (
                      <div>
                        <span className="text-slate-500">N° Doc:</span>{" "}
                        <span className="font-medium font-mono text-slate-800">{result.data.passport_number}</span>
                      </div>
                    )}
                    {result.data.nationality && (
                      <div>
                        <span className="text-slate-500">Nacionalidad:</span>{" "}
                        <span className="font-medium text-slate-800">{result.data.nationality}</span>
                      </div>
                    )}
                    {result.data.date_of_birth && (
                      <div>
                        <span className="text-slate-500">Nacimiento:</span>{" "}
                        <span className="font-medium text-slate-800">{result.data.date_of_birth}</span>
                      </div>
                    )}
                    {result.data.passport_expiry && (
                      <div>
                        <span className="text-slate-500">Vencimiento:</span>{" "}
                        <span className="font-medium text-slate-800">{result.data.passport_expiry}</span>
                      </div>
                    )}
                    {result.data.document_type && (
                      <div>
                        <span className="text-slate-500">Tipo:</span>{" "}
                        <span className="font-medium text-slate-800">
                          {result.data.document_type === "passport" ? "Pasaporte" : "Carnet de Identidad"}
                        </span>
                      </div>
                    )}
                  </div>
                  <div className="flex gap-2 mt-3">
                    <Button
                      type="button"
                      onClick={applyData}
                      data-testid="ocr-apply-data"
                      className="bg-emerald-600 hover:bg-emerald-700 text-white rounded-full text-xs h-8 px-4"
                    >
                      <CheckCircle className="w-3.5 h-3.5 mr-1" />
                      Aplicar Datos
                    </Button>
                    <Button
                      type="button"
                      onClick={resetScanner}
                      data-testid="ocr-reset"
                      className="bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 rounded-full text-xs h-8 px-4"
                    >
                      Escanear otro
                    </Button>
                  </div>
                </>
              ) : (
                <>
                  <div className="flex items-center gap-2 mb-2">
                    <AlertCircle className="w-4 h-4 text-red-600" />
                    <span className="text-sm font-medium text-red-700">
                      No se pudieron extraer datos
                    </span>
                  </div>
                  <p className="text-xs text-red-600">{result.message}</p>
                  <Button
                    type="button"
                    onClick={resetScanner}
                    data-testid="ocr-retry"
                    className="mt-2 bg-white border border-red-200 text-red-700 hover:bg-red-50 rounded-full text-xs h-8 px-4"
                  >
                    Intentar de nuevo
                  </Button>
                </>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DocumentScanner;
