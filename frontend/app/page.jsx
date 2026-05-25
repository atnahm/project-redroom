"use client";

import { useState, useEffect, useRef } from "react";
import ReCAPTCHA from "react-google-recaptcha";
import axios from "axios";
import { initializeApp } from "firebase/app";
import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword, onAuthStateChanged, signOut } from "firebase/auth";

// Firebase Configuration (Placeholder - will need real values in prod)
const firebaseConfig = {
  apiKey: "AIzaSyDummyKeyForDevelopmentPurposes123",
  authDomain: "redroom-demo.firebaseapp.com",
  projectId: "redroom-demo",
  storageBucket: "redroom-demo.appspot.com",
  messagingSenderId: "123456789012",
  appId: "1:123456789012:web:abcdef1234567890"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

export default function Home() {
  const [user, setUser] = useState(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
    const [error, setError] = useState("");
  const [isLogin, setIsLogin] = useState(true);
  const [captchaToken, setCaptchaToken] = useState(null);
  const recaptchaRef = useRef(null);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
    });
    return () => unsubscribe();
  }, []);

    const handleAuth = async (e) => {
    e.preventDefault();
    setError("");

    if (!captchaToken) {
      setError("Please complete the bot verification.");
      return;
    }
    try {
      if (isLogin) {
        await signInWithEmailAndPassword(auth, email, password);
      } else {
        await createUserWithEmailAndPassword(auth, email, password);
      }
    } catch (err) {
      console.error("Firebase Auth Error:", err);
      setError(err.message);

    }
  };

  const handleLogout = async () => {
    try {
      await signOut(auth);
    } catch (err) {
      setUser(null);
    }
  };

  if (user) {
    return <Dashboard user={user} onLogout={handleLogout} />;
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-900 p-4">
      <div className="w-full max-w-md bg-slate-800 rounded-xl shadow-2xl p-8 border border-slate-700">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-black text-red-500 tracking-tighter mb-2">REDROOM</h1>
          <p className="text-slate-400">Deepfake Forensics System</p>
        </div>

        {error && <div className="bg-red-500/10 border border-red-500 text-red-500 p-3 rounded mb-4 text-sm">{error}</div>}

        <form onSubmit={handleAuth} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Email</label>
            <input
              type="email"
              className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded focus:outline-none focus:border-red-500 text-white"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
                    <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Password</label>
            <input
              type="password"
              className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded focus:outline-none focus:border-red-500 text-white"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <div className="flex justify-center my-4">
            <ReCAPTCHA
              ref={recaptchaRef}
              sitekey="6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI" // Google Test Key
              onChange={(token) => setCaptchaToken(token)}
              theme="dark"
            />
          </div>
          <button
            type="submit"
            className="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded transition-colors"
          >
            {isLogin ? "Sign In" : "Create Account"}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-slate-400">
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <button
            onClick={() => setIsLogin(!isLogin)}
            className="text-red-400 hover:text-red-300 font-semibold"
          >
            {isLogin ? "Sign Up" : "Sign In"}
          </button>
        </div>
      </div>
    </div>
  );
}

function Dashboard({ user, onLogout }) {
  const [file, setFile] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setAnalyzing(true);
    setResult(null);

    // Real analysis calling the FastAPI backend
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await axios.post('http://localhost:8002/analyze', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setResult(res.data);
    } catch (err) {
      console.error(err);
      alert('Analysis failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900">
      <nav className="border-b border-slate-800 bg-slate-900/50 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center">
              <h1 className="text-2xl font-black text-red-500 tracking-tighter">REDROOM</h1>
              <span className="ml-3 px-2 py-1 bg-red-500/10 text-red-400 text-xs font-bold rounded border border-red-500/20">PRO</span>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-slate-400">{user.email}</span>
              <button
                onClick={onLogout}
                className="text-sm text-slate-400 hover:text-white transition-colors"
              >
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">

          <div className="md:col-span-1 space-y-6">
            <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
              <h2 className="text-lg font-bold mb-4">New Analysis</h2>
              <div className="border-2 border-dashed border-slate-600 rounded-lg p-8 text-center hover:border-red-500 transition-colors cursor-pointer">
                <input
                  type="file"
                  accept="video/*,image/*"
                  className="hidden"
                  id="file-upload"
                  onChange={handleFileChange}
                />
                <label htmlFor="file-upload" className="cursor-pointer">
                  <div className="text-slate-400 mb-2">
                    <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                  </div>
                  <span className="text-sm font-medium text-slate-300">
                    {file ? file.name : "Click to upload evidence (MP4, JPG)"}
                  </span>
                </label>
              </div>

              <button
                onClick={handleAnalyze}
                disabled={!file || analyzing}
                className={`w-full mt-4 py-3 rounded font-bold transition-all ${
                  !file || analyzing
                    ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
                    : 'bg-red-600 hover:bg-red-700 text-white shadow-lg shadow-red-900/50'
                }`}
              >
                {analyzing ? 'Processing Deepfake Forensics...' : 'Run Analysis'}
              </button>
            </div>
          </div>

          <div className="md:col-span-2">
            <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 min-h-[500px]">
              <h2 className="text-lg font-bold mb-6">Forensic Results</h2>

              {!result && !analyzing && (
                <div className="flex h-[400px] items-center justify-center text-slate-500">
                  Upload evidence to begin orchestration pipeline.
                </div>
              )}

              {analyzing && (
                <div className="flex flex-col h-[400px] items-center justify-center space-y-4">
                  <div className="w-16 h-16 border-4 border-slate-700 border-t-red-500 rounded-full animate-spin"></div>
                  <div className="text-slate-400 font-mono text-sm animate-pulse">
                    &gt; INGESTING ASSET...<br/>
                    &gt; EXTRACTING PRNU FINGERPRINT...<br/>
                    &gt; COMPUTING BISPECTRAL BICOHERENCE...<br/>
                    &gt; DETECTING RPPG SIGNAL...
                  </div>
                </div>
              )}

              {result && (
                <div className="space-y-6 animate-in fade-in duration-500">
                  <div className="flex items-center justify-between p-6 rounded-lg bg-slate-900 border border-slate-700">
                    <div>
                      <h3 className="text-sm text-slate-400 uppercase tracking-wider font-semibold mb-1">Final Verdict</h3>
                      <div className={`text-3xl font-black ${result.ai_probability > 0.7 ? 'text-red-500' : 'text-green-500'}`}>
                        {result.decision}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-slate-400 uppercase tracking-wider font-semibold mb-1">AI Probability</div>
                      <div className="text-3xl font-mono">{(result.ai_probability * 100).toFixed(1)}%</div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-sm text-slate-400 uppercase tracking-wider font-semibold mb-3">Forensic Modules</h3>
                    <div className="space-y-3">
                      {result.factors.map((factor, i) => (
                        <div key={i} className="p-4 rounded bg-slate-900 border border-slate-700 flex justify-between items-center">
                          <div>
                            <div className="font-semibold text-slate-200">{factor.name}</div>
                            <div className="text-sm text-slate-400 mt-1">{factor.value}</div>
                          </div>
                          <div className="text-red-400 font-mono font-bold">
                            {(factor.score * 100).toFixed(0)}%
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="p-4 bg-black/30 rounded border border-slate-800 font-mono text-xs text-slate-500 break-all">
                    Ledger Hash: {result.hash}
                  </div>
                </div>
              )}
            </div>
          </div>

        </div>
      </main>
    </div>
  );
}
