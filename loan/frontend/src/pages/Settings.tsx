import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Settings as SettingsIcon, User, Bell, Shield, Database, Cpu, Save } from 'lucide-react';
import { Card, PageHeader, Button, Input, Select, SectionHeader, Tabs } from '@/components/ui';
import { useAuth } from '@/context/AuthContext';
import { useToast } from '@/context/ToastContext';

const Settings: React.FC = () => {
  const { user } = useAuth();
  const { success } = useToast();
  const [tab, setTab] = useState('profile');

  const tabs = [
    { id: 'profile', label: 'Profile', icon: <User className="w-3.5 h-3.5" /> },
    { id: 'models', label: 'Model Config', icon: <Cpu className="w-3.5 h-3.5" /> },
    { id: 'notifications', label: 'Notifications', icon: <Bell className="w-3.5 h-3.5" /> },
    { id: 'api', label: 'API Settings', icon: <Database className="w-3.5 h-3.5" /> },
    { id: 'security', label: 'Security', icon: <Shield className="w-3.5 h-3.5" /> },
  ];

  return (
    <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      <PageHeader title="Settings" subtitle="Configure platform preferences and system settings" breadcrumb={['Settings']} />
      <Tabs tabs={tabs} active={tab} onChange={setTab} />

      {tab === 'profile' && (
        <Card>
          <SectionHeader title="Profile Information" subtitle="Update your personal details" />
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 max-w-xl">
            <Input label="Full Name" defaultValue={user?.name} />
            <Input label="Email Address" defaultValue={user?.email} type="email" />
            <Input label="Role" defaultValue={user?.role} disabled />
            <Input label="Organization" defaultValue="Maritime Risk Analytics" />
          </div>
          <Button className="mt-6" leftIcon={<Save className="w-4 h-4" />} onClick={() => success('Profile updated', 'Your changes have been saved.')}>
            Save Changes
          </Button>
        </Card>
      )}

      {tab === 'models' && (
        <div className="space-y-4">
          <Card>
            <SectionHeader title="Default Prediction Model" subtitle="Choose which model to use for new predictions" />
            <div className="max-w-xs">
              <Select label="Primary Model" options={[
                { value: 'gnn', label: 'Graph Neural Network (Best)' },
                { value: 'xgboost', label: 'XGBoost' },
                { value: 'svm', label: 'Support Vector Machine' },
                { value: 'logistic_regression', label: 'Logistic Regression' },
              ]} defaultValue="gnn" />
            </div>
            <Button className="mt-4" onClick={() => success('Model settings saved')}>Save</Button>
          </Card>
          <Card>
            <SectionHeader title="Risk Thresholds" subtitle="Customize risk category boundaries" />
            <div className="grid grid-cols-2 gap-4 max-w-md">
              <Input label="Low → Medium Threshold (%)" type="number" defaultValue={35} />
              <Input label="Medium → High Threshold (%)" type="number" defaultValue={65} />
            </div>
            <Button className="mt-4" onClick={() => success('Thresholds updated')}>Save</Button>
          </Card>
        </div>
      )}

      {tab === 'notifications' && (
        <Card>
          <SectionHeader title="Notification Preferences" />
          <div className="space-y-4 max-w-md">
            {[
              'Email alerts for HIGH risk predictions',
              'Daily portfolio risk summary',
              'Model retraining notifications',
              'Network risk alerts',
              'Data upload confirmations',
            ].map(label => (
              <label key={label} className="flex items-center gap-3 cursor-pointer">
                <input type="checkbox" defaultChecked className="rounded border-surface-200 text-primary" />
                <span className="text-sm text-content-primary">{label}</span>
              </label>
            ))}
          </div>
          <Button className="mt-6" onClick={() => success('Notification settings saved')}>Save Preferences</Button>
        </Card>
      )}

      {tab === 'api' && (
        <Card>
          <SectionHeader title="API Configuration" subtitle="Backend connection settings" />
          <div className="space-y-4 max-w-md">
            <Input label="API Base URL" defaultValue="http://localhost:8000/api" />
            <Input label="Request Timeout (ms)" type="number" defaultValue={30000} />
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-success" />
              <span className="text-xs text-content-secondary">Mock mode enabled — using local data</span>
            </div>
          </div>
          <Button className="mt-4" onClick={() => success('API settings saved')}>Save</Button>
        </Card>
      )}

      {tab === 'security' && (
        <Card>
          <SectionHeader title="Security Settings" />
          <div className="space-y-4 max-w-md">
            <Input label="Current Password" type="password" placeholder="••••••••" />
            <Input label="New Password" type="password" placeholder="••••••••" />
            <Input label="Confirm Password" type="password" placeholder="••••••••" />
          </div>
          <Button className="mt-4" onClick={() => success('Password updated')}>Change Password</Button>
        </Card>
      )}
    </motion.div>
  );
};

export default Settings;
