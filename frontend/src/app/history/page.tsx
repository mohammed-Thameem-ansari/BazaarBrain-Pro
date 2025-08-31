'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Nav from '../../../components/Nav';
import TransactionHistory from '../../../components/TransactionHistory';
import SimulationHistory from '../../../components/SimulationHistory';

export default function HistoryPage() {
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'transactions' | 'simulations'>('transactions');
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
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">History</h1>
            <p className="text-gray-600 mt-2">
              View your transaction and simulation history
            </p>
          </div>

          {/* Tab Navigation */}
          <div className="border-b border-gray-200 mb-8">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('transactions')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'transactions'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Transactions
              </button>
              <button
                onClick={() => setActiveTab('simulations')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'simulations'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Simulations
              </button>
            </nav>
          </div>

          {/* Tab Content */}
          {activeTab === 'transactions' && <TransactionHistory />}
          {activeTab === 'simulations' && <SimulationHistory />}
        </div>
      </main>
    </>
  );
}
