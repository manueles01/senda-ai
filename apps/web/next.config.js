/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  transpilePackages: ['@senda/ui', '@senda/shared-types', '@senda/clients'],
};

module.exports = nextConfig;
