/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  i18n: {
    locales: ['en', 'ar'],
    defaultLocale: 'en',
  },
  experimental: {
    serverActions: true,
  },
}

module.exports = nextConfig
