'use client';

import { useAuth } from '@/contexts/AuthContext';
import { Card } from '@senda/ui';

export default function DashboardPage() {
  const { user } = useAuth();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">
          Welcome back, {user?.email?.split('@')[0]}!
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card title="Voice Assistants">
          <p className="text-gray-600">0 active assistants</p>
          <p className="text-sm text-gray-500 mt-2">
            Set up your first voice assistant to get started
          </p>
        </Card>

        <Card title="Conversations">
          <p className="text-gray-600">0 conversations</p>
          <p className="text-sm text-gray-500 mt-2">No conversations yet</p>
        </Card>

        <Card title="Integrations">
          <p className="text-gray-600">0 integrations</p>
          <p className="text-sm text-gray-500 mt-2">
            Connect Phorest, Telnyx, and more
          </p>
        </Card>
      </div>

      <Card title="Quick Start">
        <div className="space-y-4">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-semibold">
              1
            </div>
            <div>
              <h3 className="font-medium text-gray-900">
                Set up your voice assistant
              </h3>
              <p className="text-sm text-gray-600">
                Configure your AI-powered voice assistant with custom settings
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-semibold">
              2
            </div>
            <div>
              <h3 className="font-medium text-gray-900">
                Connect your integrations
              </h3>
              <p className="text-sm text-gray-600">
                Link Phorest for booking management and Telnyx for telephony
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-semibold">
              3
            </div>
            <div>
              <h3 className="font-medium text-gray-900">Start automating</h3>
              <p className="text-sm text-gray-600">
                Let your AI assistant handle calls and bookings automatically
              </p>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
