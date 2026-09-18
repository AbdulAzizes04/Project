import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import { Shield, Users, HardDrive, Database, Cpu, Lock, AlertCircle, Loader } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const Admin = () => {
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchAdminData();
  }, []);

  const fetchAdminData = async () => {
    setLoading(true);
    setError('');
    try {
      const [statsRes, usersRes] = await Promise.all([
        axios.get(`${API_URL}/admin/stats`),
        axios.get(`${API_URL}/admin/users`)
      ]);
      setStats(statsRes.data);
      setUsers(usersRes.data);
    } catch (err) {
      console.error('Failed to fetch admin data:', err);
      setError(err.response?.data?.message || 'Access denied: Admin role required');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="py-24 flex flex-col items-center justify-center space-y-3">
        <Loader className="w-8 h-8 text-indigo-500 animate-spin" />
        <p className="text-xs dark:text-slate-400 text-slate-500">Checking system diagnostics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-card p-12 text-center flex flex-col items-center justify-center min-h-[400px]">
        <Lock className="w-14 h-14 text-rose-500 mb-4 animate-bounce" />
        <h3 className="text-lg font-bold dark:text-slate-200 text-slate-700">Administrator Credentials Required</h3>
        <p className="text-sm dark:text-slate-400 text-slate-500 max-w-sm mt-1">
          {error}. Only accounts configured with the admin role can view system logs and manage user permissions.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight dark:text-white text-slate-800 flex items-center gap-2">
          Administrator Console
          <Shield className="w-5 h-5 text-indigo-500" />
        </h1>
        <p className="text-sm dark:text-slate-400 text-slate-500 font-medium">
          System telemetry logs, user registers, and physical disk metrics.
        </p>
      </div>

      {stats && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="glass-card p-5 flex items-center gap-4">
            <div className="p-3.5 bg-indigo-500/10 text-indigo-500 rounded-xl shrink-0">
              <Users className="w-6 h-6" />
            </div>
            <div>
              <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Total Users</p>
              <h3 className="text-xl font-bold dark:text-white text-slate-800 mt-1">{stats.userCount}</h3>
            </div>
          </div>

          <div className="glass-card p-5 flex items-center gap-4">
            <div className="p-3.5 bg-emerald-500/10 text-emerald-400 rounded-xl shrink-0">
              <Database className="w-6 h-6" />
            </div>
            <div>
              <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Datasets Loaded</p>
              <h3 className="text-xl font-bold dark:text-white text-slate-800 mt-1">{stats.datasetCount}</h3>
            </div>
          </div>

          <div className="glass-card p-5 flex items-center gap-4">
            <div className="p-3.5 bg-rose-500/10 text-rose-400 rounded-xl shrink-0">
              <Cpu className="w-6 h-6" />
            </div>
            <div>
              <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">ML Pipelines Trained</p>
              <h3 className="text-xl font-bold dark:text-white text-slate-800 mt-1">{stats.modelCount}</h3>
            </div>
          </div>

          <div className="glass-card p-5 flex items-center gap-4">
            <div className="p-3.5 bg-amber-500/10 text-amber-400 rounded-xl shrink-0">
              <HardDrive className="w-6 h-6" />
            </div>
            <div>
              <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Disk Storage Used</p>
              <h3 className="text-xl font-bold dark:text-white text-slate-800 mt-1">{stats.storageUsedMB} MB</h3>
            </div>
          </div>
        </div>
      )}

      {/* User Management table */}
      <div className="glass-card p-6">
        <h3 className="text-sm font-bold dark:text-white text-slate-800 uppercase tracking-wider mb-6">User Database Registry</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b dark:border-slate-800 border-slate-200">
                <th className="pb-3 text-xs font-bold uppercase tracking-wider dark:text-slate-400 text-slate-500">Username</th>
                <th className="pb-3 text-xs font-bold uppercase tracking-wider dark:text-slate-400 text-slate-500 pl-4">Email</th>
                <th className="pb-3 text-xs font-bold uppercase tracking-wider dark:text-slate-400 text-slate-500 pl-4">Role</th>
                <th className="pb-3 text-xs font-bold uppercase tracking-wider dark:text-slate-400 text-slate-500 pl-4">Created At</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u._id} className="border-b dark:border-slate-800/40 border-slate-100">
                  <td className="py-3 text-xs font-semibold dark:text-slate-200 text-slate-700">{u.username}</td>
                  <td className="py-3 pl-4 text-xs dark:text-slate-400 text-slate-500">{u.email}</td>
                  <td className="py-3 pl-4">
                    <span className={`px-2 py-0.5 rounded text-[9px] font-bold uppercase ${
                      u.role === 'admin' ? 'bg-indigo-500/10 text-indigo-400' : 'bg-slate-700/10 text-slate-400'
                    }`}>
                      {u.role}
                    </span>
                  </td>
                  <td className="py-3 pl-4 text-xs dark:text-slate-400 text-slate-500">
                    {new Date(u.createdAt).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Admin;
