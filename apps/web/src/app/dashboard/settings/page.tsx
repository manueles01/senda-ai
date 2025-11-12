'use client';

import { useAuth } from '@/contexts/AuthContext';
import { Card } from '@senda/ui';

export default function SettingsPage() {
  const { user } = useAuth();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-2">
          Manage your account and preferences
        </p>
      </div>

      <Card title="Account Information">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Email
            </label>
            <p className="mt-1 text-gray-900">{user?.email}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">
              User ID
            </label>
            <p className="mt-1 text-gray-900 font-mono text-sm">{user?.uid}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Account Created
            </label>
            <p className="mt-1 text-gray-900">
              {user?.metadata.creationTime
                ? new Date(user.metadata.creationTime).toLocaleDateString()
                : 'N/A'}
            </p>
          </div>
        </div>
      </Card>

      <Card title="Integrations">
        <p className="text-gray-600">
          Connect your business tools and services
        </p>
        <div className="mt-4 space-y-3">
          <div className="flex items-center justify-between p-3 border border-gray-200 rounded-md">
            <div>
              <p className="font-medium">Phorest</p>
              <p className="text-sm text-gray-500">Salon management system</p>
            </div>
            <span className="text-sm text-gray-500">Not connected</span>
          </div>
          <div className="flex items-center justify-between p-3 border border-gray-200 rounded-md">
            <div>
              <p className="font-medium">Telnyx</p>
              <p className="text-sm text-gray-500">Telephony services</p>
            </div>
            <span className="text-sm text-gray-500">Not connected</span>
          </div>
          <div className="flex items-center justify-between p-3 border border-gray-200 rounded-md">
            <div>
              <p className="font-medium">Google Gemini</p>
              <p className="text-sm text-gray-500">AI/ML capabilities</p>
            </div>
            <span className="text-sm text-gray-500">Not connected</span>
          </div>
        </div>
      </Card>
    </div>
  );
}
