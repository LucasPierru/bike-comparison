import type { Metadata } from "next";
import { Lexend } from "next/font/google";
import Script from "next/script";
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
      <Script
        type="text/javascript"
        src="http://classic.avantlink.com/affiliate_app_confirm.php?mode=js&authResponse=6ee4cd8e19971ad0d6c26337b68b5d01d8a5851b"
      />
      <body className={`${lexend.className}`}>{children}</body>
    </html>
  );
}
