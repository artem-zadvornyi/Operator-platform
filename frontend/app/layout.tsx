import type { Metadata } from "next";
import { Inter } from "next/font/google";

import { DesignSystemProvider } from "@/components/providers";
import "@/styles/globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Operator",
  description: "Build a business. Not just content.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="bg-background-primary text-text-primary min-h-screen font-sans antialiased">
        <DesignSystemProvider>{children}</DesignSystemProvider>
      </body>
    </html>
  );
}
