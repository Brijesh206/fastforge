import type { Metadata } from "next";
import { Open_Sans, Poppins } from "next/font/google";

import { SessionProvider } from "@/providers/session-provider";
import { APP_NAME } from "@/lib/config";
import "../styles/globals.css";

const openSans = Open_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-open-sans",
  display: "swap",
});

const poppins = Poppins({
  subsets: ["latin"],
  weight: ["500", "600", "700"],
  variable: "--font-poppins",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: `${APP_NAME} — Ship your SaaS faster`,
    template: `%s · ${APP_NAME}`,
  },
  description:
    "A production-ready SaaS foundation with authentication, subscription billing, and a polished dashboard out of the box.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${openSans.variable} ${poppins.variable}`}>
      <body>
        <SessionProvider>{children}</SessionProvider>
      </body>
    </html>
  );
}
