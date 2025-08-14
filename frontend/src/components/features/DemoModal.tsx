'use client';

import React from 'react';
import Image from 'next/image';
import { useTranslation } from '@/hooks/useTranslation';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import { Product } from '@/types';
import { useAppStore, useCartStore } from '@/stores';

interface DemoModalProps {
  isOpen: boolean;
  onClose: () => void;
  product?: Product;
}

export const DemoModal: React.FC<DemoModalProps> = ({
  isOpen,
  onClose,
  product,
}) => {
  const { t } = useTranslation('common');
  const { language } = useAppStore();
  const { addItem } = useCartStore();

  if (!product || !product.demo) {
    return null;
  }

  const handleAddToCart = () => {
    addItem(product);
    onClose();
  };

  const getLocalizedDemoTitle = () => {
    return language === 'ar' && product.demo?.arabicTitle 
      ? product.demo.arabicTitle 
      : product.demo?.title || '';
  };

  const getLocalizedDemoPreview = () => {
    return language === 'ar' && product.demo?.arabicPreview 
      ? product.demo.arabicPreview 
      : product.demo?.preview || '';
  };

  const getLocalizedFeatureTitle = (feature: any) => {
    return language === 'ar' && feature.arabicTitle 
      ? feature.arabicTitle 
      : feature.title;
  };

  const getLocalizedFeatureDesc = (feature: any) => {
    return language === 'ar' && feature.arabicDesc 
      ? feature.arabicDesc 
      : feature.desc;
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={getLocalizedDemoTitle()}
      size="xl"
      className="demo-modal"
    >
      <div className="space-y-8">
        {/* Demo Preview */}
        <div className="glass rounded-2xl p-8 text-center">
          <div className="text-6xl mb-6">
            {product.icon}
          </div>
          
          <div className="max-w-3xl mx-auto">
            <p className="text-text-secondary text-lg leading-relaxed">
              {getLocalizedDemoPreview()}
            </p>
          </div>
        </div>

        {/* Demo Features */}
        {product.demo.features && product.demo.features.length > 0 && (
          <div>
            <h3 className="text-2xl font-bold text-text-primary mb-6 text-center">
              {t('demo.features')}
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {product.demo.features.map((feature, index) => (
                <div 
                  key={index}
                  className="glass rounded-xl p-6 flex gap-4 hover:glass-hover transition-all duration-300"
                >
                  <div className="text-3xl flex-shrink-0">
                    {feature.icon}
                  </div>
                  
                  <div>
                    <h4 className="font-semibold text-text-primary mb-2 text-lg">
                      {getLocalizedFeatureTitle(feature)}
                    </h4>
                    <p className="text-text-secondary leading-relaxed">
                      {getLocalizedFeatureDesc(feature)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Demo Video/Images */}
        {product.demo.videoUrl && (
          <div className="glass rounded-xl overflow-hidden">
            <video 
              controls 
              className="w-full aspect-video"
              poster={product.demo.images?.[0]}
            >
              <source src={product.demo.videoUrl} type="video/mp4" />
              Your browser does not support the video tag.
            </video>
          </div>
        )}

        {/* Demo Images Gallery */}
        {product.demo.images && product.demo.images.length > 0 && !product.demo.videoUrl && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {product.demo.images.map((image, index) => (
              <div key={index} className="glass rounded-xl overflow-hidden">
                <Image 
                  src={image} 
                  alt={`${product.title} demo ${index + 1}`}
                  width={400}
                  height={192}
                  className="w-full h-48 object-cover"
                />
              </div>
            ))}
          </div>
        )}

        {/* Call-to-Action */}
        <div className="text-center py-8 border-t border-glass-border">
          <h3 className="text-xl font-bold text-text-primary mb-4">
            Ready to get started?
          </h3>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center max-w-md mx-auto">
            <Button
              variant="gradient"
              size="lg"
              onClick={handleAddToCart}
              className="w-full sm:w-auto"
            >
              {t('product.addToCart')}
            </Button>
            
            <Button
              variant="outline"
              size="lg"
              onClick={onClose}
              className="w-full sm:w-auto"
            >
              {t('demo.close')}
            </Button>
          </div>
          
          <p className="text-text-secondary text-sm mt-4">
            Try risk-free with our 30-day money-back guarantee
          </p>
        </div>
      </div>
    </Modal>
  );
};