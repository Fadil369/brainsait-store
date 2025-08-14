'use client';

import React from 'react';
import Link from 'next/link';
import { useTranslation } from '@/hooks/useTranslation';
import { cn } from '@/lib/utils';

interface FooterProps {
  className?: string;
}

export const Footer: React.FC<FooterProps> = ({ className }) => {
  const { t } = useTranslation('common');

  const footerSections = [
    {
      title: t('footer.products'),
      links: [
        { key: 'apps', href: '#apps', label: 'Mobile Applications' },
        { key: 'templates', href: '#templates', label: 'Business Templates' },
        { key: 'courses', href: '#courses', label: 'Online Courses' },
        { key: 'ai', href: '#ai', label: 'AI Solutions' },
      ]
    },
    {
      title: t('footer.support'),
      links: [
        { key: 'consultation', href: 'https://calendly.com/fadil369', label: t('footer.bookConsultation') },
        { key: 'patreon', href: 'https://patreon.com/Fadil369', label: t('footer.supportPatreon') },
        { key: 'contact', href: '#contact', label: t('footer.contactSupport') },
        { key: 'docs', href: '#docs', label: t('footer.documentation') },
      ]
    },
    {
      title: t('footer.company'),
      links: [
        { key: 'about', href: '#about', label: t('footer.aboutUs') },
        { key: 'vision', href: '#vision', label: t('footer.vision2030') },
        { key: 'partners', href: '#partners', label: t('footer.partners') },
        { key: 'careers', href: '#careers', label: t('footer.careers') },
      ]
    }
  ];

  const socialLinks = [
    { 
      name: 'X (Twitter)', 
      href: 'https://x.com/brainsait369', 
      icon: '𝕏',
      color: 'hover:text-blue-400'
    },
    { 
      name: 'LinkedIn', 
      href: 'https://linkedin.com/in/fadil369', 
      icon: 'in',
      color: 'hover:text-blue-500'
    },
    { 
      name: 'GitHub', 
      href: 'https://github.com/fadil369', 
      icon: '⚡',
      color: 'hover:text-purple-400'
    },
    { 
      name: 'Calendly', 
      href: 'https://calendly.com/fadil369', 
      icon: '📅',
      color: 'hover:text-green-400'
    },
  ];

  return (
    <footer className={cn(
      'mt-24 glass border-t border-glass-border',
      className
    )}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        {/* Main Footer Content */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-12">
          {/* Brand Section */}
          <div className="lg:col-span-1">
            <div className="flex items-center gap-2 mb-4">
              <div className="text-2xl gradient-text-primary">◈</div>
              <span className="text-xl font-black gradient-text">
                BrainSAIT
              </span>
            </div>
            
            <p className="text-text-secondary mb-6 leading-relaxed">
              {t('footer.description')}
            </p>
            
            {/* Social Links */}
            <div className="flex gap-4">
              {socialLinks.map((social) => (
                <Link
                  key={social.name}
                  href={social.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={cn(
                    'w-12 h-12 glass rounded-xl flex items-center justify-center text-text-primary transition-all duration-300 hover:scale-105 hover:glass-hover',
                    social.color
                  )}
                  aria-label={social.name}
                >
                  <span className="text-lg font-bold">{social.icon}</span>
                </Link>
              ))}
            </div>
          </div>

          {/* Footer Sections */}
          {footerSections.map((section, index) => (
            <div key={index} className="lg:col-span-1">
              <h3 className="font-bold text-text-primary mb-4 text-lg">
                {section.title}
              </h3>
              
              <ul className="space-y-3">
                {section.links.map((link) => (
                  <li key={link.key}>
                    <Link
                      href={link.href}
                      className="text-text-secondary hover:text-vision-green transition-colors duration-300 block py-1"
                      target={link.href.startsWith('http') ? '_blank' : undefined}
                      rel={link.href.startsWith('http') ? 'noopener noreferrer' : undefined}
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Vision 2030 Badge */}
        <div className="flex justify-center mb-8">
          <div className="glass rounded-full px-6 py-3 border border-vision-green/30">
            <div className="flex items-center gap-3">
              <span className="text-2xl">🇸🇦</span>
              <span className="font-semibold text-vision-green">
                Supporting Saudi Vision 2030
              </span>
            </div>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="pt-8 border-t border-glass-border">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-text-secondary">
            <p>
              {t('footer.copyright')} | 
              <span className="text-vision-green font-semibold ml-2">
                Saudi Vision 2030
              </span>
            </p>
            
            <p>
              {t('footer.location')}
            </p>
          </div>
        </div>
      </div>

      {/* Animated background elements */}
      <div className="absolute bottom-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-vision-green to-transparent opacity-50" />
    </footer>
  );
};