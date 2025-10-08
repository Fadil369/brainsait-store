'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import CheckInForm from '@/components/field-sales/CheckInForm';

export default function CheckInPage() {
  const router = useRouter();
  // TODO: Get actual rep ID from authentication context
  const repId = 'demo-rep-id';

  const handleSuccess = () => {
    router.push('/field-sales/dashboard');
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <CheckInForm repId={repId} onSuccess={handleSuccess} />
    </div>
  );
}
