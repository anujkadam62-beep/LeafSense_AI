import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "CoffeeLeaf AI — Disease Detection & Severity Estimation",
  description: "Upload a coffee leaf photo and get a disease prediction with confidence and severity.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} h-full`}>
      <body className="flex min-h-full bg-[var(--color-bg)] text-[var(--color-foreground)] antialiased">
        {children}
      </body>
    </html>
  );
}
