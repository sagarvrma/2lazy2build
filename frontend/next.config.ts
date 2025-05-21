const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'c1.neweggimages.com',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'i.ebayimg.com',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: '1000logos.net',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'upload.wikimedia.org',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'cdn.freebiesupply.com',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'edgeup.asus.com',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'static.vecteezy.com',
        pathname: '/**',
      },
    ],
  },
}

export default nextConfig
