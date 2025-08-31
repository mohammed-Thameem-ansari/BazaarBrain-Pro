'use client';

import { useState } from 'react';

interface LLMResponse {
  content: string;
  confidence: number;
  reasoning: string;
  timestamp: string;
}

interface ArbitrationResult {
  gpt_response: LLMResponse;
  gemini_response: LLMResponse;
  final_decision: string;
  arbitration_reasoning: string;
  confidence: number;
  merged_insights: string[];
}

interface ArbitrationPanelProps {
  result: ArbitrationResult;
  onApproveAction?: () => void;
}

export default function ArbitrationPanel({ result, onApproveAction }: ArbitrationPanelProps) {
  const [activeTab, setActiveTab] = useState<'comparison' | 'decision' | 'insights'>('comparison');

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return 'text-green-600';
    if (confidence >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getConfidenceLabel = (confidence: number) => {
    if (confidence >= 80) return 'High';
    if (confidence >= 60) return 'Medium';
    return 'Low';
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="mb-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-2">AI Arbitration Panel</h3>
        <p className="text-gray-600">
          Compare GPT and Gemini responses and see the final AI decision
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('comparison')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'comparison'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            LLM Comparison
          </button>
          <button
            onClick={() => setActiveTab('decision')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'decision'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Final Decision
          </button>
          <button
            onClick={() => setActiveTab('insights')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'insights'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Merged Insights
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'comparison' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* GPT Response */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-lg font-semibold text-blue-900 flex items-center">
                <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                GPT Response
              </h4>
              <div className="text-right">
                <span className={`text-sm font-medium ${getConfidenceColor(result.gpt_response.confidence)}`}>
                  {getConfidenceLabel(result.gpt_response.confidence)}
                </span>
                <p className="text-xs text-gray-500">{result.gpt_response.confidence}%</p>
              </div>
            </div>
            
            <div className="space-y-3">
              <div>
                <p className="text-sm font-medium text-gray-700 mb-1">Analysis:</p>
                <p className="text-sm text-gray-900 bg-white p-3 rounded border">
                  {result.gpt_response.content}
                </p>
              </div>
              
              <div>
                <p className="text-sm font-medium text-gray-700 mb-1">Reasoning:</p>
                <p className="text-sm text-gray-900 bg-white p-3 rounded border">
                  {result.gpt_response.reasoning}
                </p>
              </div>
              
              <div className="text-xs text-gray-500">
                Generated: {new Date(result.gpt_response.timestamp).toLocaleString()}
              </div>
            </div>
          </div>

          {/* Gemini Response */}
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-lg font-semibold text-green-900 flex items-center">
                <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
                Gemini Response
              </h4>
              <div className="text-right">
                <span className={`text-sm font-medium ${getConfidenceColor(result.gemini_response.confidence)}`}>
                  {getConfidenceLabel(result.gemini_response.confidence)}
                </span>
                <p className="text-xs text-gray-500">{result.gemini_response.confidence}%</p>
              </div>
            </div>
            
            <div className="space-y-3">
              <div>
                <p className="text-sm font-medium text-gray-700 mb-1">Analysis:</p>
                <p className="text-sm text-gray-900 bg-white p-3 rounded border">
                  {result.gemini_response.content}
                </p>
              </div>
              
              <div>
                <p className="text-sm font-medium text-gray-700 mb-1">Reasoning:</p>
                <p className="text-sm text-gray-900 bg-white p-3 rounded border">
                  {result.gemini_response.reasoning}
                </p>
              </div>
              
              <div className="text-xs text-gray-500">
                Generated: {new Date(result.gemini_response.timestamp).toLocaleString()}
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'decision' && (
        <div className="space-y-6">
          {/* Final Decision */}
          <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-6">
            <div className="flex items-center mb-4">
              <div className="flex-shrink-0">
                <svg className="h-8 w-8 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-3">
                <h4 className="text-xl font-semibold text-purple-900">Final AI Decision</h4>
                <p className="text-sm text-purple-600">Arbitration complete with {result.confidence}% confidence</p>
              </div>
            </div>
            
            <div className="bg-white rounded-lg border border-purple-200 p-4">
              <p className="text-lg text-gray-900 font-medium">{result.final_decision}</p>
            </div>
          </div>

          {/* Arbitration Reasoning */}
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <h5 className="text-lg font-semibold text-gray-900 mb-3">Arbitration Reasoning</h5>
            <p className="text-gray-700 bg-white p-3 rounded border">
              {result.arbitration_reasoning}
            </p>
          </div>

          {/* Action Button */}
          {onApproveAction && (
            <div className="text-center">
              <button
                onClick={onApproveAction}
                className="bg-green-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-colors"
              >
                Approve Action
              </button>
              <p className="text-sm text-gray-500 mt-2">
                Confirm and execute the recommended business action
              </p>
            </div>
          )}
        </div>
      )}

      {activeTab === 'insights' && (
        <div className="space-y-4">
          <h4 className="text-lg font-semibold text-gray-900">Merged AI Insights</h4>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {result.merged_insights.map((insight, index) => (
              <div key={index} className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start">
                  <span className="text-blue-500 mr-2 mt-1">•</span>
                  <p className="text-gray-700">{insight}</p>
                </div>
              </div>
            ))}
          </div>
          
          <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-yellow-800">
                  <strong>Note:</strong> These insights combine the best analysis from both GPT and Gemini, 
                  resolving conflicts and highlighting areas of agreement.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
