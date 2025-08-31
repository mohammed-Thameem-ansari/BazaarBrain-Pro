'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Nav from '../../../components/Nav';
import UploadReceipt from '../../../components/UploadReceipt';
import { ReceiptData } from '../../../lib/receipts';

export default function UploadPage() {
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem('BB_TOKEN');
    if (!token) {
      router.push('/login');
      return;
    }
    setIsLoading(false);
  }, [router]);

  const handleUploadSuccess = (data: ReceiptData) => {
    console.log('Receipt uploaded successfully:', data);
    // You can add additional logic here, like redirecting to dashboard
    // or showing a success message
  };

  const handleUploadError = (error: string) => {
    console.error('Upload failed:', error);
    // You can add additional error handling here
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <Nav />
      <main className="min-h-screen bg-gray-50 py-8">
        <UploadReceipt
          onUploadSuccess={handleUploadSuccess}
          onUploadError={handleUploadError}
        />
      </main>
    </>
  );
}
