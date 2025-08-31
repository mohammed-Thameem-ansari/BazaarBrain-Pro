'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface LanguageContextType {
  language: string;
  setLanguage: (lang: string) => void;
  t: (key: string) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

// Basic translation data
const translations = {
  en: {
    'voice.recorder': 'Voice Recorder',
    'voice.startRecording': 'Start Recording',
    'voice.stopRecording': 'Stop Recording',
    'voice.recording': 'Recording... Speak now!',
    'voice.transcript': 'Transcript:',
    'voice.play': 'Play',
    'voice.playing': 'Playing...',
    'voice.clear': 'Clear',
    'voice.howToUse': 'How to use:',
    'voice.clickStart': 'Click "Start Recording" and speak clearly',
    'voice.clickStop': 'Click "Stop Recording" when finished',
    'voice.playback': 'Use "Play" to hear your recording',
    'voice.transcriptText': 'Your speech will be converted to text automatically',
  },
  es: {
    'voice.recorder': 'Grabadora de Voz',
    'voice.startRecording': 'Iniciar Grabación',
    'voice.stopRecording': 'Detener Grabación',
    'voice.recording': '¡Grabando... Habla ahora!',
    'voice.transcript': 'Transcripción:',
    'voice.play': 'Reproducir',
    'voice.playing': 'Reproduciendo...',
    'voice.clear': 'Limpiar',
    'voice.howToUse': 'Cómo usar:',
    'voice.clickStart': 'Haz clic en "Iniciar Grabación" y habla claramente',
    'voice.clickStop': 'Haz clic en "Detener Grabación" cuando termines',
    'voice.playback': 'Usa "Reproducir" para escuchar tu grabación',
    'voice.transcriptText': 'Tu habla se convertirá en texto automáticamente',
  }
};

interface LanguageProviderProps {
  children: ReactNode;
}

export function LanguageProvider({ children }: LanguageProviderProps) {
  const [language, setLanguage] = useState('en');

  useEffect(() => {
    const savedLanguage = localStorage.getItem('BB_LANGUAGE') || 'en';
    setLanguage(savedLanguage);
  }, []);

  const handleLanguageChange = (lang: string) => {
    setLanguage(lang);
    localStorage.setItem('BB_LANGUAGE', lang);
  };

  const t = (key: string): string => {
    const langTranslations = translations[language as keyof typeof translations] || translations.en;
    return langTranslations[key as keyof typeof langTranslations] || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage: handleLanguageChange, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}
