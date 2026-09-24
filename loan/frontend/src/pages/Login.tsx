import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { motion } from 'framer-motion';
import { Anchor, Eye, EyeOff, Ship, Waves, TrendingUp, Shield, AlertTriangle } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { useToast } from '@/context/ToastContext';
import { Button, Input } from '@/components/ui';

const schema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
  rememberMe: z.boolean().optional(),
});
type FormValues = z.infer<typeof schema>;

const Login: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const { success, error } = useToast();
  const [showPassword, setShowPassword] = useState(false);

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { email: 'admin@maritimerisks.com', password: 'maritime2026' },
  });

  const onSubmit = async (data: FormValues) => {
    try {
      await login(data.email, data.password);
      success('Welcome back', 'Maritime Risk Intelligence loaded.');
      navigate('/dashboard');
    } catch {
      error('Authentication failed', 'Please check your credentials and try again.');
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* LEFT — Maritime Visual */}
      <div className="hidden lg:flex w-1/2 relative bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 overflow-hidden">
        {/* Orange accent overlay */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary/20 via-transparent to-transparent" />

        {/* Animated wave layers */}
        <div className="absolute bottom-0 left-0 right-0 h-32 opacity-20">
          <svg viewBox="0 0 1200 120" preserveAspectRatio="none" className="w-full h-full">
            <path d="M0,60 C150,100 350,0 600,60 C850,120 1050,20 1200,60 L1200,120 L0,120 Z" fill="#F59E0B" />
          </svg>
        </div>
        <div className="absolute bottom-0 left-0 right-0 h-20 opacity-10">
          <svg viewBox="0 0 1200 120" preserveAspectRatio="none" className="w-full h-full">
            <path d="M0,80 C200,20 400,100 600,40 C800,-20 1000,80 1200,40 L1200,120 L0,120 Z" fill="#F59E0B" />
          </svg>
        </div>

        {/* Grid dots */}
        <div
          className="absolute inset-0 opacity-5"
          style={{
            backgroundImage: 'radial-gradient(circle, #F59E0B 1px, transparent 1px)',
            backgroundSize: '32px 32px',
          }}
        />

        {/* Content */}
        <div className="relative z-10 flex flex-col justify-between p-12 w-full">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center">
              <Anchor className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="text-white font-bold text-lg leading-none">Maritime Risk</p>
              <p className="text-slate-400 text-xs">Intelligence Platform</p>
            </div>
          </div>

          {/* Main hero */}
          <div className="py-12">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.6 }}
            >
              <div className="flex items-center gap-2 mb-4">
                <Ship className="w-8 h-8 text-primary" />
              </div>
              <h2 className="text-3xl font-bold text-white leading-tight mb-4">
                AI-Powered Maritime<br />
                <span className="text-primary">Financial Risk</span><br />
                Intelligence
              </h2>
              <p className="text-slate-300 text-sm leading-relaxed max-w-xs">
                Advanced loan default prediction for shipping companies using
                Topological Data Analysis, Graph Neural Networks, and XGBoost.
              </p>
            </motion.div>

            {/* Feature chips */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5, duration: 0.6 }}
              className="mt-8 space-y-3"
            >
              {[
                { icon: <TrendingUp className="w-4 h-4" />, label: 'XGBoost + GNN Prediction', desc: '92.6% accuracy' },
                { icon: <Waves className="w-4 h-4" />, label: 'Topological Data Analysis', desc: 'Persistent homology features' },
                { icon: <Shield className="w-4 h-4" />, label: 'Network Risk Assessment', desc: 'Financial network analysis' },
                { icon: <AlertTriangle className="w-4 h-4" />, label: 'Explainable AI', desc: 'SHAP-based feature importance' },
              ].map((f, i) => (
                <div key={i} className="flex items-center gap-3 bg-white/5 rounded-lg px-4 py-2.5">
                  <div className="text-primary">{f.icon}</div>
                  <div>
                    <p className="text-white text-xs font-medium">{f.label}</p>
                    <p className="text-slate-400 text-2xs">{f.desc}</p>
                  </div>
                </div>
              ))}
            </motion.div>
          </div>

          {/* Footer */}
          <p className="text-slate-500 text-xs">
            Final Year Project — Enhanced TDA-Based ML for Maritime Loan Default Prediction
          </p>
        </div>
      </div>

      {/* RIGHT — Login Form */}
      <div className="flex-1 flex items-center justify-center p-8 bg-white">
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4 }}
          className="w-full max-w-sm"
        >
          {/* Mobile logo */}
          <div className="flex lg:hidden items-center gap-2 mb-8">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <Anchor className="w-4 h-4 text-white" />
            </div>
            <p className="font-bold text-content-primary">Maritime Risk Intelligence</p>
          </div>

          <h1 className="text-2xl font-bold text-content-primary">Welcome back</h1>
          <p className="text-sm text-content-secondary mt-1 mb-8">
            Sign in to the Maritime Risk Intelligence platform
          </p>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <Input
              id="email"
              type="email"
              label="Email address"
              placeholder="admin@maritimerisks.com"
              error={errors.email?.message}
              {...register('email')}
            />

            <div className="form-group">
              <label className="label" htmlFor="password">Password</label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Enter your password"
                  className={`input pr-10 ${errors.password ? 'input-error' : ''}`}
                  {...register('password')}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(s => !s)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-content-tertiary hover:text-content-secondary"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {errors.password && <p className="text-xs text-danger mt-1">{errors.password.message}</p>}
            </div>

            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" className="rounded border-surface-200" {...register('rememberMe')} />
                <span className="text-sm text-content-secondary">Remember me</span>
              </label>
              <button type="button" className="text-sm text-primary hover:text-primary-hover font-medium">
                Forgot password?
              </button>
            </div>

            <Button type="submit" className="w-full" loading={isSubmitting} size="lg">
              {isSubmitting ? 'Signing in...' : 'Sign In'}
            </Button>
          </form>

          {/* Demo hint */}
          <div className="mt-6 p-3 bg-surface-50 rounded-lg border border-surface-200">
            <p className="text-xs text-content-secondary font-medium mb-1">Demo credentials pre-filled:</p>
            <p className="text-xs text-content-tertiary">admin@maritimerisks.com / maritime2026</p>
          </div>

          <p className="text-xs text-content-tertiary text-center mt-6">
            Maritime Risk Intelligence Platform · Final Year Project 2026
          </p>
        </motion.div>
      </div>
    </div>
  );
};

export default Login;
