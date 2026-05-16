import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "QUANTARA OS — AI Trading Command Center",
  description: "Personal AI-powered trading and financial operating system for Indian retail options trading.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="grid-bg">
        <div className="layout-root">
          {children}
        </div>
      </body>
    </html>
  );
}
