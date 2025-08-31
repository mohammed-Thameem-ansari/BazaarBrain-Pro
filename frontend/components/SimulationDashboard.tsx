'use client';

import { useState } from 'react';
import { simulationsAPI, SimulationResult } from '../lib/simulations';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';
import { useTextToSpeech } from '../lib/tts';

interface SimulationDashboardProps {
  initialQuery?: string;
  onSimulationComplete?: (result: SimulationResult) => void;
}

export default function SimulationDashboard({ initialQuery = '', onSimulationComplete }: SimulationDashboardProps) {
  const [query, setQuery] = useState(initialQuery);
  const [isRunning, setIsRunning] = useState(false);
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showAdvancedForm, setShowAdvancedForm] = useState(false);
  const { speak, muted, toggleMute } = useTextToSpeech();

  // Advanced form fields
  const [scenario, setScenario] = useState('price_change');
  const [item, setItem] = useState('');
  const [change, setChange] = useState('');
  const [quantity, setQuantity] = useState('');
  const [currentPrice, setCurrentPrice] = useState('');

  const handleNaturalLanguageSimulation = async () => {
    if (!query.trim()) return;

    setIsRunning(true);
    setError(null);
    setResult(null);

    try {
      const response = await simulationsAPI.runSimulation(query);
      
      if (response.success) {
        setResult(response.result);
        onSimulationComplete?.(response.result);
        try {
          const r = response.result;
          const summary = `Simulation complete. Scenario: ${r.scenario}. Revenue change ${r.impact.revenue_change.toFixed(2)} dollars, profit change ${r.impact.profit_change.toFixed(2)} dollars. Confidence ${r.confidence} percent.`;
          speak(summary);
        } catch {}
      } else {
        setError(response.error || 'Simulation failed');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Simulation failed';
      setError(errorMessage);
    } finally {
      setIsRunning(false);
    }
  };

  const handleAdvancedSimulation = async () => {
    if (!item || !change) return;

    const advancedQuery = `What if I ${scenario === 'price_change' ? 'change the price of' : 'change the quantity of'} ${item} by ${change}${quantity ? ` with quantity ${quantity}` : ''}${currentPrice ? ` from current price $${currentPrice}` : ''}?`;

    setQuery(advancedQuery);
    await handleNaturalLanguageSimulation();
  };

  const resetForm = () => {
    setQuery('');
    setResult(null);
    setError(null);
    setScenario('price_change');
    setItem('');
    setChange('');
    setQuantity('');
    setCurrentPrice('');
  };

  return (
    <motion.div 
      className="max-w-6xl mx-auto p-6 space-y-8"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      <motion.div 
        className="text-center"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.2 }}
      >
        <h2 className="text-3xl font-bold text-gray-900 mb-4">Business Simulation</h2>
        <p className="text-lg text-gray-600">
          Ask "what if" questions to analyze business scenarios and get AI-powered insights
        </p>
        <button onClick={toggleMute} className="mt-2 text-sm text-blue-600 hover:text-blue-700">
          {muted ? 'Unmute voice' : 'Mute voice'}
        </button>
      </motion.div>

      {/* Natural Language Input */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Natural Language Query</h3>
        <div className="space-y-4">
          <div>
            <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
              Describe your business scenario
            </label>
            <textarea
              id="query"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., What if I increase rice price by 5%? What if I order 100 more units of coffee? What happens to my profit if I reduce prices by 10%?"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              rows={3}
            />
          </div>
          
          <div className="flex items-center justify-between">
            <button
              onClick={handleNaturalLanguageSimulation}
              disabled={!query.trim() || isRunning}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isRunning ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Running Simulation...
                </div>
              ) : (
                'Run Simulation'
              )}
            </button>
            
            <button
              onClick={() => setShowAdvancedForm(!showAdvancedForm)}
              className="text-blue-600 hover:text-blue-700 font-medium text-sm"
            >
              {showAdvancedForm ? 'Hide' : 'Show'} Advanced Form
            </button>
          </div>
        </div>
      </div>

      {/* Advanced Form */}
      {showAdvancedForm && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Advanced Simulation</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="scenario" className="block text-sm font-medium text-gray-700 mb-1">
                Scenario Type
              </label>
              <select
                id="scenario"
                value={scenario}
                onChange={(e) => setScenario(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="price_change">Price Change</option>
                <option value="quantity_change">Quantity Change</option>
                <option value="cost_change">Cost Change</option>
                <option value="demand_change">Demand Change</option>
              </select>
            </div>
            
            <div>
              <label htmlFor="item" className="block text-sm font-medium text-gray-700 mb-1">
                Item/Product
              </label>
              <input
                id="item"
                type="text"
                value={item}
                onChange={(e) => setItem(e.target.value)}
                placeholder="e.g., Rice, Coffee, Bread"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <div>
              <label htmlFor="change" className="block text-sm font-medium text-gray-700 mb-1">
                Change Amount
              </label>
              <input
                id="change"
                type="text"
                value={change}
                onChange={(e) => setChange(e.target.value)}
                placeholder="e.g., +5%, -10%, +100 units"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <div>
              <label htmlFor="quantity" className="block text-sm font-medium text-gray-700 mb-1">
                Quantity (optional)
              </label>
              <input
                id="quantity"
                type="number"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                placeholder="e.g., 100"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <div>
              <label htmlFor="currentPrice" className="block text-sm font-medium text-gray-700 mb-1">
                Current Price (optional)
              </label>
              <input
                id="currentPrice"
                type="number"
                step="0.01"
                value={currentPrice}
                onChange={(e) => setCurrentPrice(e.target.value)}
                placeholder="e.g., 2.50"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          
          <div className="mt-6 flex space-x-3">
            <button
              onClick={handleAdvancedSimulation}
              disabled={!item || !change || isRunning}
              className="bg-green-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Run Advanced Simulation
            </button>
            <button
              onClick={resetForm}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
            >
              Reset Form
            </button>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Simulation Result */}
      {result && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          <div className="flex items-center mb-6">
            <div className="flex-shrink-0">
              <svg className="h-8 w-8 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-xl font-medium text-green-800">Simulation Results</h3>
              <p className="text-sm text-green-600">Analysis complete for: {result.scenario}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Before vs After Comparison */}
            <div className="bg-white rounded-lg border border-green-200 p-4">
              <h4 className="text-lg font-semibold text-gray-900 mb-4">Before vs After</h4>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Revenue:</span>
                  <div className="text-right">
                    <span className="text-gray-900 font-medium">${result.before.revenue.toFixed(2)}</span>
                    <span className="text-gray-500 mx-2">→</span>
                    <span className="text-gray-900 font-medium">${result.after.revenue.toFixed(2)}</span>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Profit:</span>
                  <div className="text-right">
                    <span className="text-gray-900 font-medium">${result.before.profit.toFixed(2)}</span>
                    <span className="text-gray-500 mx-2">→</span>
                    <span className="text-gray-900 font-medium">${result.after.profit.toFixed(2)}</span>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Price:</span>
                  <div className="text-right">
                    <span className="text-gray-900 font-medium">${result.before.price.toFixed(2)}</span>
                    <span className="text-gray-500 mx-2">→</span>
                    <span className="text-gray-900 font-medium">${result.after.price.toFixed(2)}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Impact Analysis */}
            <div className="bg-white rounded-lg border border-green-200 p-4">
              <h4 className="text-lg font-semibold text-gray-900 mb-4">Impact Analysis</h4>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Revenue Change:</span>
                  <span className={`font-semibold ${result.impact.revenue_change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {result.impact.revenue_change >= 0 ? '+' : ''}${result.impact.revenue_change.toFixed(2)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Profit Change:</span>
                  <span className={`font-semibold ${result.impact.profit_change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {result.impact.profit_change >= 0 ? '+' : ''}${result.impact.profit_change.toFixed(2)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Percentage Change:</span>
                  <span className={`font-semibold ${result.impact.percentage_change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {result.impact.percentage_change >= 0 ? '+' : ''}{result.impact.percentage_change.toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Confidence:</span>
                  <span className="font-semibold text-gray-900">{result.confidence}%</span>
                </div>
              </div>
            </div>
          </div>

          {/* Recommendations */}
          {result.recommendations.length > 0 && (
            <div className="mt-6 bg-white rounded-lg border border-green-200 p-4">
              <h4 className="text-lg font-semibold text-gray-900 mb-3">Recommendations</h4>
              <ul className="space-y-2">
                {result.recommendations.map((rec, index) => (
                  <li key={index} className="flex items-start">
                    <span className="text-green-500 mr-2">•</span>
                    <span className="text-gray-700">{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

                         {/* Assumptions */}
               {result.assumptions.length > 0 && (
                 <div className="mt-6 bg-white rounded-lg border border-green-200 p-4">
                   <h4 className="text-lg font-semibold text-gray-900 mb-3">Key Assumptions</h4>
                   <ul className="space-y-2">
                     {result.assumptions.map((assumption, index) => (
                       <li key={index} className="flex items-start">
                         <span className="text-blue-500 mr-2">•</span>
                         <span className="text-gray-700">{assumption}</span>
                       </li>
                     ))}
                   </ul>
                 </div>
               )}

               {/* Charts and Analytics */}
               <div className="mt-6 space-y-6">
                 <h4 className="text-lg font-semibold text-gray-900">Analytics & Charts</h4>
                 
                 {/* Revenue & Profit Trend */}
                 <div className="bg-white rounded-lg border border-green-200 p-4">
                   <h5 className="text-md font-semibold text-gray-900 mb-4">Revenue & Profit Trend</h5>
                   <ResponsiveContainer width="100%" height={300}>
                     <LineChart data={[
                       { period: 'Before', revenue: result.before.revenue, profit: result.before.profit },
                       { period: 'After', revenue: result.after.revenue, profit: result.after.profit }
                     ]}>
                       <CartesianGrid strokeDasharray="3 3" />
                       <XAxis dataKey="period" />
                       <YAxis />
                       <Tooltip formatter={(value) => [`$${(value as number).toFixed(2)}`, '']} />
                       <Legend />
                       <Line type="monotone" dataKey="revenue" stroke="#3b82f6" strokeWidth={2} name="Revenue" />
                       <Line type="monotone" dataKey="profit" stroke="#10b981" strokeWidth={2} name="Profit" />
                     </LineChart>
                   </ResponsiveContainer>
                 </div>

                 {/* Impact Comparison */}
                 <div className="bg-white rounded-lg border border-green-200 p-4">
                   <h5 className="text-md font-semibold text-gray-900 mb-4">Impact Comparison</h5>
                   <ResponsiveContainer width="100%" height={300}>
                     <BarChart data={[
                       { metric: 'Revenue Change', value: result.impact.revenue_change, color: result.impact.revenue_change >= 0 ? '#10b981' : '#ef4444' },
                       { metric: 'Profit Change', value: result.impact.profit_change, color: result.impact.profit_change >= 0 ? '#10b981' : '#ef4444' },
                       { metric: 'Percentage', value: result.impact.percentage_change, color: result.impact.percentage_change >= 0 ? '#10b981' : '#ef4444' }
                     ]}>
                       <CartesianGrid strokeDasharray="3 3" />
                       <XAxis dataKey="metric" />
                       <YAxis />
                       <Tooltip formatter={(value) => [typeof value === 'number' ? (value >= 0 ? '+' : '') + (value as number).toFixed(2) : value, '']} />
                       <Bar dataKey="value" fill="#3b82f6" />
                     </BarChart>
                   </ResponsiveContainer>
                 </div>

                 {/* Confidence Distribution */}
                 <div className="bg-white rounded-lg border border-green-200 p-4">
                   <h5 className="text-md font-semibold text-gray-900 mb-4">Confidence Level</h5>
                   <ResponsiveContainer width="100%" height={300}>
                     <PieChart>
                       <Pie
                         data={[
                           { name: 'Confidence', value: result.confidence, color: result.confidence >= 80 ? '#10b981' : result.confidence >= 60 ? '#f59e0b' : '#ef4444' },
                           { name: 'Uncertainty', value: 100 - result.confidence, color: '#e5e7eb' }
                         ]}
                         cx="50%"
                         cy="50%"
                         innerRadius={60}
                         outerRadius={100}
                         paddingAngle={5}
                         dataKey="value"
                       >
                         {[
                           { name: 'Confidence', value: result.confidence, color: result.confidence >= 80 ? '#10b981' : result.confidence >= 60 ? '#f59e0b' : '#ef4444' },
                           { name: 'Uncertainty', value: 100 - result.confidence, color: '#e5e7eb' }
                         ].map((entry, index) => (
                           <Cell key={`cell-${index}`} fill={entry.color} />
                         ))}
                       </Pie>
                       <Tooltip formatter={(value) => [`${value}%`, '']} />
                       <Legend />
                     </PieChart>
                   </ResponsiveContainer>
                 </div>
               </div>
             </div>
           )}
         </motion.div>
       );
     }
