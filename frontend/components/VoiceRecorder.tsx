'use client';

import { useState, useRef, useEffect, useMemo, useCallback } from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import { motion, AnimatePresence } from 'framer-motion';

interface VoiceRecorderProps {
  onTranscript: (text: string) => void;
  onError?: (error: string) => void;
}

export default function VoiceRecorder({ onTranscript, onError }: VoiceRecorderProps) {
  const { t } = useLanguage();
  const [isRecording, setIsRecording] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [audioUrl, setAudioUrl] = useState<string>('');
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  useEffect(() => {
    // Check if Web Speech API is supported
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      if (onError) {
        onError('Speech recognition is not supported in this browser');
      }
    }

    // Check if MediaRecorder is supported
    if (!('MediaRecorder' in window)) {
      if (onError) {
        onError('Audio recording is not supported in this browser');
      }
    }

    return () => {
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
    };
  }, [onError, audioUrl]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        setAudioBlob(audioBlob);
        const url = URL.createObjectURL(audioBlob);
        setAudioUrl(url);
      };

      // Start speech recognition
      if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognitionRef.current = new SpeechRecognition();
        recognitionRef.current.continuous = true;
        recognitionRef.current.interimResults = true;
        recognitionRef.current.lang = 'en-US'; // Can be made dynamic based on language

        recognitionRef.current.onresult = (event) => {
          let finalTranscript = '';
          for (let i = event.resultIndex; i < event.results.length; i++) {
            if (event.results[i].isFinal) {
              finalTranscript += event.results[i][0].transcript;
            }
          }
          if (finalTranscript) {
            setTranscript(finalTranscript);
            onTranscript(finalTranscript);
          }
        };

        recognitionRef.current.onerror = (event) => {
          console.error('Speech recognition error:', event.error);
          if (onError) {
            onError(`Speech recognition error: ${event.error}`);
          }
        };

        recognitionRef.current.start();
      }

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error starting recording:', error);
      if (onError) {
        onError('Failed to start recording. Please check microphone permissions.');
      }
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
    }
    
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    
    setIsRecording(false);
  };

  const playRecording = () => {
    if (audioUrl) {
      const audio = new Audio(audioUrl);
      setIsPlaying(true);
      
      audio.onended = () => setIsPlaying(false);
      audio.onerror = () => {
        setIsPlaying(false);
        if (onError) {
          onError('Failed to play audio recording');
        }
      };
      
      audio.play();
    }
  };

  const clearRecording = () => {
    setTranscript('');
    setAudioBlob(null);
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
      setAudioUrl('');
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 sm:p-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4 space-y-3 sm:space-y-0">
        <h3 className="text-lg sm:text-xl font-semibold text-gray-900">
          🎤 {t('voice.recorder') || 'Voice Recorder'}
        </h3>
        <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2">
          {!isRecording ? (
            <button
              onClick={startRecording}
              onKeyDown={(e) => e.key === 'Enter' && startRecording()}
              aria-label={t('voice.startRecording') || 'Start voice recording'}
              aria-describedby="recording-instructions"
              className="w-full sm:w-auto inline-flex items-center justify-center px-4 py-3 sm:py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-colors text-sm sm:text-base"
            >
              <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
              {t('voice.startRecording') || 'Start Recording'}
            </button>
          ) : (
            <button
              onClick={stopRecording}
              onKeyDown={(e) => e.key === 'Enter' && stopRecording()}
              aria-label={t('voice.stopRecording') || 'Stop voice recording'}
              aria-describedby="recording-status"
              className="w-full sm:w-auto inline-flex items-center justify-center px-4 py-3 sm:py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors text-sm sm:text-base"
            >
              <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
              </svg>
              {t('voice.stopRecording') || 'Stop Recording'}
            </button>
          )}
        </div>
      </div>

      {/* Recording Status */}
      <AnimatePresence>
        {isRecording && (
          <motion.div 
            className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg"
            initial={{ opacity: 0, scale: 0.9, y: -10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: -10 }}
            transition={{ duration: 0.3 }}
          >
            <div className="flex items-center">
              <motion.div 
                className="w-3 h-3 bg-red-500 rounded-full mr-2"
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 1, repeat: Infinity }}
                role="status"
                aria-label="Recording indicator"
              />
              <span id="recording-status" className="text-red-700 font-medium" role="status" aria-live="polite">
                {t('voice.recording') || 'Recording... Speak now!'}
              </span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Transcript Display */}
      {transcript && (
        <div className="mb-4">
          <label htmlFor="transcript-display" className="block text-sm font-medium text-gray-700 mb-2">
            {t('voice.transcript') || 'Transcript:'}
          </label>
          <div 
            id="transcript-display"
            className="bg-gray-50 border border-gray-200 rounded-lg p-3"
            role="region"
            aria-label="Voice transcript"
            aria-live="polite"
          >
            <p className="text-gray-900">{transcript}</p>
          </div>
        </div>
      )}

      {/* Audio Controls */}
      {audioBlob && (
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t('voice.recording') || 'Recording:'}
          </label>
          <div className="flex space-x-2">
            <button
              onClick={playRecording}
              disabled={isPlaying}
              className="inline-flex items-center px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isPlaying ? (
                <>
                  <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {t('voice.playing') || 'Playing...'}
                </>
              ) : (
                <>
                  <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {t('voice.play') || 'Play'}
                </>
              )}
            </button>
            
            <button
              onClick={clearRecording}
              className="inline-flex items-center px-3 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
            >
              <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              {t('voice.clear') || 'Clear'}
            </button>
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="text-sm text-gray-600">
        <p className="mb-2">
          <strong>{t('voice.howToUse') || 'How to use:'}</strong>
        </p>
        <ul className="list-disc list-inside space-y-1">
          <li>{t('voice.clickStart') || 'Click "Start Recording" and speak clearly'}</li>
          <li>{t('voice.clickStop') || 'Click "Stop Recording" when finished'}</li>
          <li>{t('voice.playback') || 'Use "Play" to hear your recording'}</li>
                     <li>{t('voice.transcriptText') || 'Your speech will be converted to text automatically'}</li>
        </ul>
      </div>
    </div>
  );
}
