/** Public runtime config, read from NEXT_PUBLIC_* env vars. */

export const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export const APP_NAME = process.env.NEXT_PUBLIC_APP_NAME ?? "FastForge";
