import React, { useState } from 'react';
import axios from 'axios';
import { ShieldCheck, AlertTriangle, Upload, Lock, Activity, FileWarning } from 'lucide-react';

function App() {
  const [file, setFile] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [preview, setPreview] = useState(null);
  const [demoMode, setDemoMode] = useState(true);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setPreview(URL.createObjectURL(selectedFile));
      setResult(null);
    }
  };

  const handleAnalyze = async () => {
    if (!file) return;

    setAnalyzing(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      // Assuming backend is running on localhost:8000
      // Pass demo_mode param
      const response = await axios.post(`http://localhost:8000/analyze?demo_mode=${demoMode}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Simulate a delay for "Matrix" effect
      setTimeout(() => {
        setResult(response.data);
        setAnalyzing(false);
      }, 2000);

    } catch (error) {
      console.error("Error analyzing file:", error);
      setAnalyzing(false);
      alert("Error connecting to the analysis engine.");
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-between p-4 relative">
      <div className="scan-line"></div>

      {/* Header */}
      <header className="w-full max-w-4xl flex justify-between items-center py-6 border-b border-green-900">
        <div className="flex items-center gap-2">
          <Lock className="w-8 h-8 text-[#00ff41]" />
          <h1 className="text-2xl font-bold tracking-widest text-[#00ff41] uppercase">
            DeepFake Detection System
          </h1>
        </div>
        <div className="flex flex-col items-end gap-1">
          <div className="text-xs text-green-700 font-mono">
            V.1.0.0 // POLYGON AMOY
          </div>
          <button
            onClick={() => setDemoMode(!demoMode)}
            className={`text-[10px] font-mono border px-2 py-0.5 rounded transition-all uppercase tracking-wider
              ${demoMode
                ? 'text-yellow-500 border-yellow-500/30 bg-yellow-500/10 animate-pulse hover:bg-yellow-500/20'
                : 'text-green-500 border-green-500/30 bg-green-500/10 hover:bg-green-500/20'
              }`}
          >
            {demoMode ? '⚠ DEMO MODE ACTIVE' : '● LIVENET MODE'}
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 w-full max-w-4xl flex flex-col items-center justify-center gap-8 py-10">

        {/* Upload Zone */}
        {!result && (
          <div className="w-full max-w-xl">
            <label
              className={`flex flex-col items-center justify-center w-full h-64 border-2 border-dashed rounded-lg cursor-pointer 
              ${analyzing ? 'border-green-500 bg-green-900/20 animate-pulse' : 'border-green-800 hover:border-[#00ff41] hover:bg-green-900/10'} 
              transition-all duration-300`}
            >
              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                {preview ? (
                  <img src={preview} alt="Preview" className="h-40 object-contain mb-4 opacity-80" />
                ) : (
                  <Upload className="w-12 h-12 mb-4 text-green-600" />
                )}
                <p className="mb-2 text-sm text-green-500">
                  <span className="font-semibold">Click to upload</span> or drag and drop
                </p>
                <p className="text-xs text-green-700">PNG, JPG, JPEG (MAX. 10MB)</p>
              </div>
              <input type="file" className="hidden" onChange={handleFileChange} accept="image/*" disabled={analyzing} />
            </label>

            {file && !analyzing && (
              <button
                onClick={handleAnalyze}
                className="w-full mt-6 py-3 px-6 matrix-button font-bold text-lg flex items-center justify-center gap-2"
              >
                <Activity className="w-5 h-5" />
                INITIATE SCAN
              </button>
            )}

            {analyzing && (
              <div className="w-full mt-6 text-center">
                <div className="text-[#00ff41] text-lg animate-pulse">
                  &gt; SCANNING BLOCKCHAIN...
                  <br />
                  &gt; CALCULATING PHASH...
                  <br />
                  &gt; VERIFYING INTEGRITY...
                </div>
              </div>
            )}
          </div>
        )}

        {/* Results Overlay */}
        {result && (
          <div className="w-full max-w-2xl animate-in fade-in zoom-in duration-500">
            <div className={`relative p-8 rounded-lg border-2 ${result.status === 'verified' ? 'border-green-500 bg-green-900/20' : 'border-red-500 bg-red-900/20'} backdrop-blur-sm`}>

              <div className="flex flex-col items-center text-center gap-4">
                {result.status === 'verified' ? (
                  <ShieldCheck className="w-24 h-24 text-green-500" />
                ) : (
                  <AlertTriangle className="w-24 h-24 text-red-500" />
                )}

                <h2 className={`text-3xl font-bold uppercase tracking-widest ${result.status === 'verified' ? 'text-green-400' : 'text-red-500'}`}>
                  {result.status === 'verified' ? 'VERIFIED AUTHENTIC' : 'MANIPULATION DETECTED'}
                </h2>

                <div className="w-full h-px bg-current opacity-30 my-2"></div>

                <div className="grid grid-cols-2 gap-8 w-full text-left">
                  <div>
                    <p className="text-xs uppercase opacity-50">Source</p>
                    <p className="text-lg font-mono">{result.source || "Unknown"}</p>
                  </div>
                  <div>
                    <p className="text-xs uppercase opacity-50">Integrity Score</p>
                    <p className="text-lg font-mono">
                      {result.score ? `${(result.score * 100).toFixed(1)}%` : "100%"}
                    </p>
                  </div>
                </div>

                <div className="mt-4 p-4 w-full bg-black/50 rounded border border-white/10">
                  <p className="font-mono text-sm">
                    &gt; SYSTEM MESSAGE: {result.message}
                  </p>
                </div>

                <button
                  onClick={() => { setResult(null); setFile(null); setPreview(null); }}
                  className="mt-6 py-2 px-8 border border-white/20 hover:bg-white/10 transition-colors uppercase text-sm"
                >
                  Analyze Another File
                </button>
              </div>
            </div>
          </div>
        )}

      </main>

      {/* Footer */}
      <footer className="w-full py-4 text-center border-t border-green-900 mt-auto">
        <p className="text-green-800 text-xs uppercase tracking-widest">
          Built by Team-Tech4Bharat
        </p>
      </footer>
    </div>
  );
}

export default App;
