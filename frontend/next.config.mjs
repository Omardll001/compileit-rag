/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone", // Krävs för Docker-deployment
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000",
  },
  devIndicators: false, // Döljer Next.js dev-indikatorn (blå "N")
};
export default nextConfig;
