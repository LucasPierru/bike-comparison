import type { Metadata } from "next";
import { Lexend } from "next/font/google";
import "./globals.css";

export const metadata: Metadata = {
  title:
    "Compare Bikes & Prices | Find the Best Deals on Road & Mountain Bikes",
  description:
    "Easily compare bike prices from top brands. Find the best road, mountain, and electric bikes with our updated listings. Get the best deals today!",
};

const lexend = Lexend({
  subsets: ["latin"],
  weight: ["100", "200", "300", "400", "500", "600", "700", "800", "900"],
});

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${lexend.className}`}>{children}</body>
    </html>
  );
}
