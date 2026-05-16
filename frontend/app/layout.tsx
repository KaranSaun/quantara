import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "QUANTARA OS — AI Trading Command Center",
  description: "Personal AI-powered trading and financial operating system for Indian retail options trading.",
};

import { useState } from 'react';

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <html lang="en">
      <body className="grid-bg">
        <div className={`layout-root ${isSidebarOpen ? 'sidebar-open' : ''}`}>
          {/* Mobile Menu Button */}
          <button 
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            style={{
              position: 'fixed',
              bottom: 24,
              right: 24,
              width: 56,
              height: 56,
              borderRadius: 28,
              background: 'var(--green)',
              color: '#000',
              zIndex: 1000,
              border: 'none',
              boxShadow: '0 8px 24px rgba(0, 255, 136, 0.4)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 24,
            }}
            className="mobile-only"
          >
            {isSidebarOpen ? '×' : '☰'}
          </button>
          {children}
        </div>
      </body>
    </html>
  );
}
