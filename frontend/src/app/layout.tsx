import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { LanguageProvider } from "../../contexts/LanguageContext";
import { AuthProvider } from "../../contexts/AuthContext";
import { OfflineProvider } from "../../contexts/OfflineContext";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "BazaarBrain - AI-Powered Business Assistant",
  description: "AI-powered business assistant for shopkeepers using GPT + Gemini",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <AuthProvider>
          <OfflineProvider>
            <LanguageProvider>
              {children}
            </LanguageProvider>
          </OfflineProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
