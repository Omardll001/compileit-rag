/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000",
  },
  // Döljer Next.js dev-indikatorn (det blå "N") i nedre vänstra hörnet
  devIndicators: false,
};
export default nextConfig;
