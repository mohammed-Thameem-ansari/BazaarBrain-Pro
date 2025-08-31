"use client";
import { useEffect, useState } from 'react';
import Nav from '../../../../components/Nav';
import { collectiveAPI } from '../../../../lib/collective';
import { useOffline } from '../../../../contexts/OfflineContext';

export default function CollectivePage() {
  const [productId, setProductId] = useState('rice');
  const [qty, setQty] = useState(50);
  const [orders, setOrders] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { addUnsynced } = useOffline();

  const refresh = async () => {
    try {
      const res = await collectiveAPI.getMyOrders();
      setOrders(res.orders || []);
    } catch (e) {
      setOrders([]);
    }
  };

  const place = async () => {
    setLoading(true);
    setError(null);
    try {
      await collectiveAPI.placeOrder({ user_id: 'me', product_id: productId, quantity: Number(qty) });
      await refresh();
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to place order');
      // mark unsynced locally (offline)
      addUnsynced();
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  return (
    <>
      <Nav />
      <main className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <h1 className="text-2xl font-bold mb-4">Collective Orders</h1>
          <div className="bg-white border rounded-lg p-4 mb-6">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <input className="border rounded px-3 py-2" value={productId} onChange={(e) => setProductId(e.target.value)} placeholder="product id" />
              <input className="border rounded px-3 py-2" type="number" value={qty} onChange={(e) => setQty(Number(e.target.value))} placeholder="quantity" />
              <button onClick={place} disabled={loading} className="bg-blue-600 text-white rounded px-4 py-2">
                {loading ? 'Placing…' : 'Place / Join Order'}
              </button>
            </div>
            {error && <p className="text-red-600 mt-2">{error}</p>}
          </div>

          <div className="bg-white border rounded-lg p-4">
            <h2 className="font-semibold mb-3">Aggregated Orders</h2>
            {orders.length === 0 ? (
              <p className="text-gray-500">No orders yet.</p>
            ) : (
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-gray-600">
                    <th className="py-2">Product</th>
                    <th className="py-2">Total Qty</th>
                    <th className="py-2">Participants</th>
                    <th className="py-2">Price/Unit</th>
                    <th className="py-2">Savings</th>
                  </tr>
                </thead>
                <tbody>
                  {orders.map((o, i) => (
                    <tr key={i} className="border-t">
                      <td className="py-2">{o.product_id}</td>
                      <td className="py-2">{o.total_quantity}</td>
                      <td className="py-2">{o.participants}</td>
                      <td className="py-2">${o.price_per_unit}</td>
                      <td className="py-2">{o.estimated_savings}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </main>
    </>
  );
}
