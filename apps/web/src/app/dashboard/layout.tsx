import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { Navbar } from '@/components/dashboard/Navbar';
import { Sidebar } from '@/components/dashboard/Sidebar';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="flex">
          <Sidebar />
          <main className="flex-1 p-8">{children}</main>
        </div>
      </div>
    </ProtectedRoute>
  );
}
