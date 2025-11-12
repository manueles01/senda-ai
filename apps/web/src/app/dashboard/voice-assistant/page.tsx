'use client';

import { Card } from '@senda/ui';

export default function VoiceAssistantPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">
          Voice Assistant Setup
        </h1>
        <p className="text-gray-600 mt-2">
          Configure your AI-powered voice assistant
        </p>
      </div>

      <Card title="Coming Soon">
        <div className="text-center py-8">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg
              className="w-8 h-8 text-blue-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
              />
            </svg>
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            Voice Assistant Configuration
          </h3>
          <p className="text-gray-600 max-w-md mx-auto mb-6">
            Set up your virtual voice assistant to handle calls, take bookings,
            and provide customer support. This feature will be available soon.
          </p>
          <div className="space-y-4 text-left max-w-md mx-auto">
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-6 h-6 bg-green-100 text-green-600 rounded-full flex items-center justify-center text-xs font-bold">
                ✓
              </div>
              <p className="text-sm text-gray-600">
                Configure voice and personality settings
              </p>
            </div>
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-6 h-6 bg-green-100 text-green-600 rounded-full flex items-center justify-center text-xs font-bold">
                ✓
              </div>
              <p className="text-sm text-gray-600">
                Set up call handling and routing
              </p>
            </div>
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-6 h-6 bg-green-100 text-green-600 rounded-full flex items-center justify-center text-xs font-bold">
                ✓
              </div>
              <p className="text-sm text-gray-600">
                Integrate with Dialogflow CX and Gemini
              </p>
            </div>
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-6 h-6 bg-green-100 text-green-600 rounded-full flex items-center justify-center text-xs font-bold">
                ✓
              </div>
              <p className="text-sm text-gray-600">
                Connect telephony via Telnyx
              </p>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
