import type { Metadata } from "next";
import { Newsreader } from "next/font/google";
import "./globals.css";

const geistSans = Newsreader({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Babelfish",
  description: "Speak tech jargon and watch our AI goldfish translate it into plain English",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
