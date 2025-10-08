'use client';

import React from 'react';
import { CustomerPortalDashboard } from '@/components/customer-portal/CustomerPortalDashboard';

export default function CustomerPortalPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-black">
      <CustomerPortalDashboard />
    </div>
  );
}
