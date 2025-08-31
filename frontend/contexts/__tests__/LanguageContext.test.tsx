import { render, screen, fireEvent } from '@testing-library/react';
import { LanguageProvider, useLanguage } from '../LanguageContext';

// Test component that uses the context
const TestComponent = () => {
  const { language, setLanguage, t } = useLanguage();
  
  return (
    <div>
      <div data-testid="current-language">{language}</div>
      <button onClick={() => setLanguage('es')} data-testid="change-to-spanish">
        Change to Spanish
      </button>
      <button onClick={() => setLanguage('en')} data-testid="change-to-english">
        Change to English
      </button>
      <div data-testid="translation">{t('voice.recorder')}</div>
    </div>
  );
};

const renderWithLanguageProvider = (component: React.ReactElement) => {
  return render(<LanguageProvider>{component}</LanguageProvider>);
};

describe('LanguageContext', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
  });

  it('provides default English language', () => {
    renderWithLanguageProvider(<TestComponent />);
    
    expect(screen.getByTestId('current-language')).toHaveTextContent('en');
  });

  it('allows language switching', () => {
    renderWithLanguageProvider(<TestComponent />);
    
    const spanishButton = screen.getByTestId('change-to-spanish');
    fireEvent.click(spanishButton);
    
    expect(screen.getByTestId('current-language')).toHaveTextContent('es');
  });

  it('provides correct translations', () => {
    renderWithLanguageProvider(<TestComponent />);
    
    // Default English
    expect(screen.getByTestId('translation')).toHaveTextContent('Voice Recorder');
    
    // Switch to Spanish
    const spanishButton = screen.getByTestId('change-to-spanish');
    fireEvent.click(spanishButton);
    
    expect(screen.getByTestId('translation')).toHaveTextContent('Grabadora de Voz');
  });

  it('persists language selection in localStorage', () => {
    renderWithLanguageProvider(<TestComponent />);
    
    const spanishButton = screen.getByTestId('change-to-spanish');
    fireEvent.click(spanishButton);
    
    expect(localStorage.getItem('BB_LANGUAGE')).toBe('es');
  });

  it('loads language from localStorage on mount', () => {
    localStorage.setItem('BB_LANGUAGE', 'es');
    
    renderWithLanguageProvider(<TestComponent />);
    
    expect(screen.getByTestId('current-language')).toHaveTextContent('es');
  });

  it('falls back to English for unknown translation keys', () => {
    const TestComponentWithUnknownKey = () => {
      const { t } = useLanguage();
      return <div data-testid="unknown-key">{t('unknown.key')}</div>;
    };

    renderWithLanguageProvider(<TestComponentWithUnknownKey />);

    expect(screen.getByTestId('unknown-key')).toHaveTextContent('unknown.key');
  });
});
