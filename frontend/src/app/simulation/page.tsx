'use client';

import { Suspense, useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Nav from '../../../components/Nav';
import SimulationDashboard from '../../../components/SimulationDashboard';
import { SimulationResult } from '../../../lib/simulations';

function SimulationInner() {
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem('BB_TOKEN');
    if (!token) {
      router.push('/login');
      return;
    }
    setIsLoading(false);
  }, [router]);

  const handleSimulationComplete = (result: SimulationResult) => {
    console.log('Simulation completed:', result);
    // You can add additional logic here, like saving to history
    // or showing a success message
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

  // Get initial query from URL params if available
  const initialQuery = searchParams.get('query') || '';

  return (
    <>
      <Nav />
      <main className="min-h-screen bg-gray-50 py-8">
        <SimulationDashboard
          initialQuery={initialQuery}
          onSimulationComplete={handleSimulationComplete}
        />
      </main>
    </>
  );
}

export default function SimulationPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center"><p className="text-gray-600">Loading...</p></div>}>
      <SimulationInner />
    </Suspense>
  );
}
