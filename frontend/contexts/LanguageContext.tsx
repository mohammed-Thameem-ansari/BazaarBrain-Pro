'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface LanguageContextType {
  language: string; // 'en' | 'hi' | ...
  setLanguage: (lang: string) => void;
  t: (key: string) => string;
  speechLocale: string; // e.g., 'en-US' | 'hi-IN'
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
    'voice.mute': 'Mute',
    'voice.unmute': 'Unmute',
  },
  hi: {
    'voice.recorder': 'आवाज़ रिकॉर्डर',
    'voice.startRecording': 'रिकॉर्डिंग शुरू करें',
    'voice.stopRecording': 'रिकॉर्डिंग रोकें',
    'voice.recording': 'रिकॉर्डिंग... अभी बोलें!',
    'voice.transcript': 'ट्रांसक्रिप्ट:',
    'voice.play': 'चलाएँ',
    'voice.playing': 'चल रहा है...',
    'voice.clear': 'साफ़ करें',
    'voice.howToUse': 'कैसे उपयोग करें:',
    'voice.clickStart': '"रिकॉर्डिंग शुरू करें" पर क्लिक करें और स्पष्ट रूप से बोलें',
    'voice.clickStop': 'खत्म होने पर "रिकॉर्डिंग रोकें" पर क्लिक करें',
    'voice.playback': 'अपनी रिकॉर्डिंग सुनने के लिए "चलाएँ" का उपयोग करें',
    'voice.transcriptText': 'आपकी आवाज़ स्वतः पाठ में बदल दी जाएगी',
    'voice.mute': 'म्यूट',
    'voice.unmute': 'अनम्यूट',
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
  <LanguageContext.Provider value={{ language, setLanguage: handleLanguageChange, t, speechLocale: language === 'hi' ? 'hi-IN' : 'en-US' }}>
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
