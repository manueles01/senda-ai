'use client';

import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { Button } from '@senda/ui';

export default function Home() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && user) {
      router.push('/dashboard');
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <div className="text-center max-w-3xl">
        <h1 className="text-5xl font-bold mb-6 text-gray-900">Senda</h1>
        <p className="text-2xl text-gray-600 mb-4">
          Conversational AI Platform
        </p>
        <p className="text-lg text-gray-500 mb-8">
          Guiding businesses along the path to automation and intelligent
          service
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link href="/signup">
            <Button variant="primary" className="px-8 py-3">
              Get Started
            </Button>
          </Link>
          <Link href="/login">
            <Button variant="outline" className="px-8 py-3">
              Sign In
            </Button>
          </Link>
        </div>

        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 text-left">
          <div>
            <h3 className="font-semibold text-lg mb-2">Voice Assistants</h3>
            <p className="text-gray-600">
              AI-powered voice assistants that handle calls and bookings
              automatically
            </p>
          </div>
          <div>
            <h3 className="font-semibold text-lg mb-2">Smart Integration</h3>
            <p className="text-gray-600">
              Seamlessly connects with Phorest, Telnyx, and other business tools
            </p>
          </div>
          <div>
            <h3 className="font-semibold text-lg mb-2">24/7 Automation</h3>
            <p className="text-gray-600">
              Never miss a customer interaction with round-the-clock service
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
