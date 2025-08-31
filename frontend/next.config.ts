import type { NextConfig } from "next";

// Expose only the required public env vars at build time.
// Runtime is handled by NEXT_PUBLIC_* vars provided in .env.production
const nextConfig: NextConfig = {
  env: {
    NEXT_PUBLIC_SUPABASE_URL: process.env.NEXT_PUBLIC_SUPABASE_URL,
    NEXT_PUBLIC_SUPABASE_KEY: process.env.NEXT_PUBLIC_SUPABASE_KEY,
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL,
  },
  reactStrictMode: true,
};

export default nextConfig;
