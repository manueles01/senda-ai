import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Senda - Conversational AI Platform',
  description:
    'Guiding businesses along the path to automation and intelligent service',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
