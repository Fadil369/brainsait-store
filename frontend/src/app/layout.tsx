import React from 'react';
import type { Metadata } from 'next';
import './globals.css';
import { Providers } from '@/lib/providers';

// Use system fonts instead of Google Fonts for static export compatibility

export const metadata: Metadata = {
  title: 'BrainSAIT Store - Digital Innovation Hub',
  description: 'Transform Your Business with Premium Digital Solutions - Supporting Saudi Vision 2030',
  keywords: [
    'digital solutions',
    'Saudi Arabia', 
    'Vision 2030',
    'AI tools',
    'business automation',
    'digital transformation',
    'BrainSAIT'
  ],
  authors: [{ name: 'Dr. Fadil', url: 'https://linkedin.com/in/fadil369' }],
  creator: 'Dr. Fadil',
  publisher: 'BrainSAIT',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL('https://store.brainsait.com'),
  alternates: {
    canonical: '/',
    languages: {
      'en-US': '/en',
      'ar-SA': '/ar',
    },
  },
  openGraph: {
    title: 'BrainSAIT Store - Digital Innovation Hub',
    description: 'Transform Your Business with Premium Digital Solutions',
    url: 'https://store.brainsait.com',
    siteName: 'BrainSAIT Store',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'BrainSAIT Store - Digital Innovation Hub',
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'BrainSAIT Store - Digital Innovation Hub',
    description: 'Transform Your Business with Premium Digital Solutions',
    creator: '@brainsait369',
    images: ['/og-image.png'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    google: 'your-google-verification-code',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" dir="ltr">
      <head>
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
        <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
        <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
        <link rel="manifest" href="/site.webmanifest" />
        <meta name="theme-color" content="#00d4aa" />
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5" />
        
        {/* Preload critical resources - moved to _document.js for proper Next.js font optimization */}
        
        {/* JSON-LD structured data */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "Organization",
              "name": "BrainSAIT",
              "url": "https://store.brainsait.com",
              "logo": "https://store.brainsait.com/logo.png",
              "description": "Digital Innovation Hub supporting Saudi Vision 2030",
              "address": {
                "@type": "PostalAddress",
                "addressCountry": "SA",
                "addressLocality": "Riyadh"
              },
              "sameAs": [
                "https://x.com/brainsait369",
                "https://linkedin.com/in/fadil369",
                "https://github.com/fadil369"
              ]
            }),
          }}
        />
      </head>
      <body className="font-sans antialiased">
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}