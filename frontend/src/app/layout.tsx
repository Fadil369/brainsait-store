'use client';

import React, { useEffect } from 'react';
import type { Metadata } from 'next';
import './globals.css';
import { Providers } from '@/lib/providers';
import { useAppStore } from '@/stores';

// Use system fonts instead of Google Fonts for static export compatibility

// Note: Since we need client-side features (language switching), 
// metadata is moved to a separate metadata file or handled via head management

function RootLayoutContent({
  children,
}: {
  children: React.ReactNode;
}) {
  const { language } = useAppStore();
  const dir = language === 'ar' ? 'rtl' : 'ltr';
  const lang = language === 'ar' ? 'ar-SA' : 'en-US';

  useEffect(() => {
    // Update document direction and language
    document.documentElement.dir = dir;
    document.documentElement.lang = lang;
  }, [dir, lang]);

  return (
    <html lang={lang} dir={dir}>
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5" />
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
        <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
        <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
        <link rel="manifest" href="/site.webmanifest" />
        <meta name="theme-color" content="#00d4aa" />
        
        <title>BrainSAIT Store - Digital Innovation Hub</title>
        <meta name="description" content="Transform Your Business with Premium Digital Solutions - Supporting Saudi Vision 2030" />
        <meta name="keywords" content="digital solutions, Saudi Arabia, Vision 2030, AI tools, business automation, digital transformation, BrainSAIT" />
        
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

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <RootLayoutContent>{children}</RootLayoutContent>;
}