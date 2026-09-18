import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { BarChart3, Lock, Mail, User, AlertCircle, Sparkles } from 'lucide-react';

const Login = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [formLoading, setFormLoading] = useState(false);

  const { login, register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setFormLoading(true);

    if (isLogin) {
      const res = await login(email, password);
      if (res.success) {
        navigate('/');
      } else {
        setError(res.message);
      }
    } else {
      if (!username.trim()) {
        setError('Username is required');
        setFormLoading(false);
        return;
      }
      const res = await register(username, email, password);
      if (res.success) {
        navigate('/');
      } else {
        setError(res.message);
      }
    }
    setFormLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900 text-slate-100 px-4 relative overflow-hidden">
      {/* Decorative Blur Background Spheres */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-600/20 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-emerald-600/10 rounded-full blur-[120px] pointer-events-none" />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        {/* App Title Header */}
        <div className="flex flex-col items-center mb-8">
          <div className="w-14 h-14 bg-indigo-600 rounded-2xl flex items-center justify-center shadow-lg shadow-indigo-600/30 mb-3">
            <BarChart3 className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-1.5">
            AI Business Advisor <Sparkles className="w-4 h-4 text-emerald-400" />
          </h1>
          <p className="text-sm text-slate-400 mt-1">Intelligent Enterprise Analytics Platform</p>
        </div>

        {/* Card */}
        <div className="bg-slate-800/60 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-8 shadow-2xl">
          {/* Tab Selection */}
          <div className="flex border-b border-slate-700 mb-6">
            <button
              onClick={() => { setIsLogin(true); setError(''); }}
              className={`flex-1 pb-3 text-sm font-semibold transition-all relative ${
                isLogin ? 'text-indigo-400' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Sign In
              {isLogin && (
                <motion.div
                  layoutId="activeTab"
                  className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-500"
                />
              )}
            </button>
            <button
              onClick={() => { setIsLogin(false); setError(''); }}
              className={`flex-1 pb-3 text-sm font-semibold transition-all relative ${
                !isLogin ? 'text-indigo-400' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Register
              {!isLogin && (
                <motion.div
                  layoutId="activeTab"
                  className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-500"
                />
              )}
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center gap-2 bg-rose-500/10 border border-rose-500/30 text-rose-400 px-4 py-3 rounded-lg text-sm"
              >
                <AlertCircle className="w-5 h-5 shrink-0" />
                <span>{error}</span>
              </motion.div>
            )}

            {!isLogin && (
              <div className="space-y-1">
                <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Username</label>
                <div className="relative">
                  <span className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                    <User className="h-5 w-5 text-slate-500" />
                  </span>
                  <input
                    type="text"
                    required
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="e.g. johndoe"
                    className="w-full bg-slate-900 border border-slate-700/60 rounded-xl py-2.5 pl-10 pr-4 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
                  />
                </div>
              </div>
            )}

            <div className="space-y-1">
              <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                {isLogin ? 'Email Address or Username' : 'Email Address'}
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                  <Mail className="h-5 w-5 text-slate-500" />
                </span>
                <input
                  type={isLogin ? "text" : "email"}
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder={isLogin ? "e.g. john@company.com or johndoe" : "e.g. john@company.com"}
                  className="w-full bg-slate-900 border border-slate-700/60 rounded-xl py-2.5 pl-10 pr-4 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
                />
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Password</label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                  <Lock className="h-5 w-5 text-slate-500" />
                </span>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full bg-slate-900 border border-slate-700/60 rounded-xl py-2.5 pl-10 pr-4 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={formLoading}
              className="w-full bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl py-3 font-semibold text-sm shadow-lg shadow-indigo-600/20 active:scale-[0.98] transition-all disabled:opacity-50 disabled:pointer-events-none mt-2 flex items-center justify-center"
            >
              {formLoading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : isLogin ? (
                'Sign In'
              ) : (
                'Create Account'
              )}
            </button>
          </form>
        </div>
      </motion.div>
    </div>
  );
};

export default Login;
