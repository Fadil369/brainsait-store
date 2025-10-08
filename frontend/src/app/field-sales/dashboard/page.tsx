'use client';

import React from 'react';
import SalesRepDashboard from '@/components/field-sales/SalesRepDashboard';

export default function FieldSalesDashboardPage() {
  // TODO: Get actual rep ID from authentication context
  const repId = 'demo-rep-id';

  return <SalesRepDashboard repId={repId} />;
}
