'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import VoiceOrderForm from '@/components/field-sales/VoiceOrderForm';

export default function VoiceOrderPage() {
  const router = useRouter();
  // TODO: Get actual rep ID from authentication context
  const repId = 'demo-rep-id';

  const handleSuccess = () => {
    router.push('/field-sales/dashboard');
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <VoiceOrderForm repId={repId} onSuccess={handleSuccess} />
    </div>
  );
}
