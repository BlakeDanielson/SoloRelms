import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  // Load environment variables from the project root
  env: {
    // These will be available on both server and client side (if prefixed with NEXT_PUBLIC_)
  },
  // Configure Next.js to look for .env files in the project root
  experimental: {
    // This ensures .env files are loaded from the project root
  },
};

// Load environment variables from project root
if (typeof process !== 'undefined') {
  require('dotenv').config({ path: path.resolve(__dirname, '../.env') });
}

export default nextConfig;
