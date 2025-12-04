import React, { useState, useEffect, useRef } from 'react';
import { Camera, Upload, Zap, Sun, Shield, User, Activity } from 'lucide-react';

const API_URL = "http://localhost:8000";
const WS_URL = "ws://localhost:8000/ws";

const App = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [fps, setFps] = useState(0);
  const [liveImage, setLiveImage] = useState<string | null>(null);
  const [sourceImage, setSourceImage] = useState<string | null>(null);
  
  const [settings, setSettings] = useState({
    structureAdapt: true,
    relighting: true,
    enhance: false
  });

  const wsRef = useRef<WebSocket | null>(null);

  // WebSocket Verbindung
  useEffect(() => {
    connectWebSocket();
    return () => {
      wsRef.current?.close();
    };
  }, []);

  // Settings Update an Backend senden
  useEffect(() => {
    fetch(`${API_URL}/update_settings`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(settings)
    }).catch(err => console.error("Settings sync error", err));
  }, [settings]);

  const connectWebSocket = () => {
    const ws = new WebSocket(WS_URL);
    
    ws.onopen = () => setIsConnected(true);
    ws.onclose = () => setIsConnected(false);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.image) setLiveImage(data.image);
      if (data.fps) setFps(data.fps);
    };

    wsRef.current = ws;
  };

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setSourceImage(URL.createObjectURL(file));

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${API_URL}/upload_source`, {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if(data.status === 'success') {
        alert("Gesicht erfolgreich analysiert und geladen!");
      } else {
        alert("Fehler: " + data.message);
      }
    } catch (err) {
      console.error(err);
      alert("Upload fehlgeschlagen - Backend läuft nicht?");
    }
  };

  return (
    <div className="flex h-screen w-screen bg-neutral-900 text-white font-sans overflow-hidden">
      
      {/* SIDEBAR */}
      <div className="w-80 flex-shrink-0 bg-neutral-800 border-r border-neutral-700 flex flex-col p-4 shadow-xl z-10">
        <div className="mb-8 flex items-center gap-2">
          <div className="w-8 h-8 bg-blue-600 rounded flex items-center justify-center shadow-lg shadow-blue-500/20">
            <Camera size={18} className="text-white" />
          </div>
          <h1 className="text-xl font-bold tracking-tight">DeepLive<span className="text-blue-400">Cam</span></h1>
        </div>

        {/* Source Image */}
        <div className="mb-6">
          <h2 className="text-xs font-bold text-neutral-500 uppercase tracking-wider mb-3">Source Face</h2>
          <div className="relative group">
            <div className="w-full aspect-square bg-neutral-700/50 rounded-xl border-2 border-dashed border-neutral-600 hover:border-blue-500 hover:bg-neutral-700 transition-all flex flex-col items-center justify-center overflow-hidden">
              {sourceImage ? (
                <img src={sourceImage} alt="Source" className="w-full h-full object-cover" />
              ) : (
                <div className="flex flex-col items-center text-neutral-500">
                  <Upload size={32} className="mb-2" />
                  <span className="text-xs">Drop Image here</span>
                </div>
              )}
            </div>
            <input 
              type="file" 
              className="absolute inset-0 opacity-0 cursor-pointer" 
              accept="image/*"
              onChange={handleImageUpload}
            />
          </div>
        </div>

        {/* Settings */}
        <div className="flex-1 space-y-4">
           <h2 className="text-xs font-bold text-neutral-500 uppercase tracking-wider">Parameters</h2>
           
           <Toggle 
             label="3D Structure Adapt" 
             desc="MediaPipe Mesh Warping"
             icon={<User size={16} />}
             active={settings.structureAdapt}
             onClick={() => setSettings(s => ({...s, structureAdapt: !s.structureAdapt}))}
           />
           
           <Toggle 
             label="Dynamic Relighting" 
             desc="Match Ambient Light"
             icon={<Sun size={16} />}
             active={settings.relighting}
             onClick={() => setSettings(s => ({...s, relighting: !s.relighting}))}
           />

            <Toggle 
             label="Face Enhancer" 
             desc="GFPGAN (Slows FPS)"
             icon={<Zap size={16} />}
             active={settings.enhance}
             onClick={() => setSettings(s => ({...s, enhance: !s.enhance}))}
           />
        </div>

        <div className="mt-4 p-3 bg-neutral-900 rounded-lg border border-neutral-700">
            <div className="flex items-center gap-2 text-neutral-400 text-xs">
                <Activity size={14} />
                <span>Backend Status:</span>
                <span className={isConnected ? "text-green-400" : "text-red-400"}>
                    {isConnected ? "Connected" : "Disconnected"}
                </span>
            </div>
        </div>
      </div>

      {/* MAIN VIEWPORT */}
      <div className="flex-1 bg-black relative flex items-center justify-center">
        {liveImage ? (
            <img 
                src={liveImage} 
                className="w-full h-full object-contain" 
                alt="Live Stream" 
            />
        ) : (
            <div className="text-neutral-500 flex flex-col items-center">
                <div className="loader mb-4 border-t-blue-500 rounded-full w-8 h-8 border-4 border-neutral-700 animate-spin"></div>
                <p>Waiting for Camera Stream...</p>
            </div>
        )}

        {/* HUD Overlay */}
        <div className="absolute top-4 right-4 flex gap-2">
            <div className="bg-black/70 backdrop-blur border border-white/10 px-3 py-1 rounded text-sm font-mono font-bold text-green-400">
                {fps} FPS
            </div>
        </div>
        
        {/* Protection Badge */}
        <div className="absolute bottom-4 left-4 flex items-center gap-2 text-xs text-white/20 select-none">
            <Shield size={12} />
            <span>AI Generated Content • Watermarked</span>
        </div>
      </div>
    </div>
  );
};

// Helper Component
const Toggle = ({ label, desc, icon, active, onClick }: any) => (
  <div 
    onClick={onClick}
    className={`flex items-center justify-between p-3 rounded-xl border transition-all cursor-pointer ${
      active 
        ? 'bg-blue-900/20 border-blue-500/50' 
        : 'bg-neutral-800 border-transparent hover:bg-neutral-700'
    }`}
  >
    <div className="flex items-center gap-3">
      <div className={`p-2 rounded-lg ${active ? 'text-blue-400 bg-blue-900/30' : 'text-neutral-400 bg-neutral-700'}`}>
        {icon}
      </div>
      <div>
        <div className={`text-sm font-medium ${active ? 'text-blue-100' : 'text-neutral-300'}`}>{label}</div>
        <div className="text-[10px] text-neutral-500">{desc}</div>
      </div>
    </div>
    <div className={`w-3 h-3 rounded-full ${active ? 'bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.6)]' : 'bg-neutral-600'}`}></div>
  </div>
);

export default App;
