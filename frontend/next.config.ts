const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'c1.neweggimages.com',
        pathname: '/**',
      },
      // eBay image domains
      {
        protocol: 'https',
        hostname: 'i.ebayimg.com',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'p.ebayimg.com',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'ir.ebaystatic.com',
        pathname: '/**',
      },
      // Brand logos
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
      // Your fallback domain
      {
        protocol: 'https',
        hostname: '2lazy2build.vercel.app',
        pathname: '/**',
      },
    ],
  },
}

export default nextConfig