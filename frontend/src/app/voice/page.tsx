'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Nav from '../../../components/Nav';
import VoiceRecorder from '../../../components/VoiceRecorder';
import API from '../../../lib/api';
import { useTextToSpeech } from '../../../lib/tts';

export default function VoicePage() {
  const [isLoading, setIsLoading] = useState(true);
  const [transcript, setTranscript] = useState('');
  const router = useRouter();
  const { speak, muted, toggleMute } = useTextToSpeech();

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem('BB_TOKEN');
    if (!token) {
      router.push('/login');
      return;
    }
    setIsLoading(false);
  }, [router]);

  const handleTranscript = (text: string) => {
    setTranscript(text);
    // Auto-send to intake when user pauses speaking
    if (text && text.length > 4) {
      API.post('/api/v1/intake', { text })
        .then((res) => {
          const routed = res.data?.routed;
          const message = routed?.message || routed?.result?.recommendations?.[0] || 'Processed.';
          speak(`Got it. ${message}`);
        })
        .catch(() => {
          // swallow for UX; error banner below
        });
    }
  };

  const handleError = (error: string) => {
    console.error('Voice error:', error);
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
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">Voice Interface</h1>
            <p className="text-lg text-gray-600">
              Test voice recording and speech-to-text functionality
            </p>
            <button onClick={toggleMute} className="mt-3 text-sm text-blue-600 hover:text-blue-700">
              {muted ? 'Unmute voice' : 'Mute voice'}
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Voice Recorder */}
            <div>
              <VoiceRecorder
                onTranscript={handleTranscript}
                onError={handleError}
              />
            </div>

            {/* Transcript Display */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Live Transcript
              </h3>
              {transcript ? (
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <p className="text-gray-900">{transcript}</p>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <svg className="w-12 h-12 mx-auto mb-4 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  <p>Start recording to see your transcript here</p>
                </div>
              )}
            </div>
          </div>

          {/* Instructions */}
          <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-blue-900 mb-3">
              How to Use Voice Interface
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-blue-800">
              <div>
                <h4 className="font-medium mb-2">🎤 Recording</h4>
                <ul className="space-y-1">
                  <li>• Click "Start Recording" and speak clearly</li>
                  <li>• Your speech is converted to text in real-time</li>
                  <li>• Click "Stop Recording" when finished</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium mb-2">🔊 Playback</h4>
                <ul className="space-y-1">
                  <li>• Use "Play" to hear your recording</li>
                  <li>• Audio is saved locally in your browser</li>
                  <li>• Use "Clear" to reset everything</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}
