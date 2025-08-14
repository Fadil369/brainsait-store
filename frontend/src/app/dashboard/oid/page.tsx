import { Metadata } from 'next';
import OIDTreeViewer from '@/components/oid/OIDTreeViewer';

export const metadata: Metadata = {
  title: 'OID System | BrainSAIT Store',
  description: 'Explore the BrainSAIT OID (Object Identification) system and unified platform components',
};

export default function OIDPage() {
  return (
    <div className="container mx-auto py-6">
      <OIDTreeViewer />
    </div>
  );
}