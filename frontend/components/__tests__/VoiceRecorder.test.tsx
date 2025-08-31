import { render, screen, fireEvent } from '@testing-library/react';
import VoiceRecorder from '../VoiceRecorder';
import { LanguageProvider } from '../../contexts/LanguageContext';

// Mock the Web Speech API
const mockSpeechRecognition = {
  continuous: false,
  interimResults: false,
  lang: 'en-US',
  start: jest.fn(),
  stop: jest.fn(),
  onresult: null,
  onerror: null,
};

const mockMediaRecorder = {
  start: jest.fn(),
  stop: jest.fn(),
  stream: {
    getTracks: jest.fn().mockReturnValue([{ stop: jest.fn() }]),
  },
  ondataavailable: null,
  onstop: null,
};

// Mock navigator.mediaDevices
Object.defineProperty(navigator, 'mediaDevices', {
  value: {
    getUserMedia: jest.fn().mockResolvedValue('mock-stream'),
  },
  writable: true,
});

// Mock MediaRecorder
global.MediaRecorder = jest.fn().mockImplementation(() => mockMediaRecorder);

// Mock SpeechRecognition
Object.defineProperty(window, 'SpeechRecognition', {
  value: jest.fn().mockImplementation(() => mockSpeechRecognition),
  writable: true,
});

Object.defineProperty(window, 'webkitSpeechRecognition', {
  value: jest.fn().mockImplementation(() => mockSpeechRecognition),
  writable: true,
});

const renderWithLanguageProvider = (component: React.ReactElement) => {
  return render(<LanguageProvider>{component}</LanguageProvider>);
};

describe('VoiceRecorder', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders voice recorder component', () => {
    const mockOnTranscript = jest.fn();
    const mockOnError = jest.fn();

    renderWithLanguageProvider(
      <VoiceRecorder onTranscript={mockOnTranscript} onError={mockOnError} />
    );

  expect(screen.getByText(/Voice Recorder/i)).toBeInTheDocument();
  // Select the actionable button by role+name to avoid collisions with instructional text
  expect(screen.getByRole('button', { name: /Start Recording/i })).toBeInTheDocument();
  });

  it('shows start recording button initially', () => {
    const mockOnTranscript = jest.fn();
    const mockOnError = jest.fn();

    renderWithLanguageProvider(
      <VoiceRecorder onTranscript={mockOnTranscript} onError={mockOnError} />
    );

  expect(screen.getByRole('button', { name: /Start Recording/i })).toBeInTheDocument();
  // Ensure the Stop Recording button is not present yet
  expect(screen.queryByRole('button', { name: /Stop Recording/i })).not.toBeInTheDocument();
  });

  it('shows instructions', () => {
    const mockOnTranscript = jest.fn();
    const mockOnError = jest.fn();

    renderWithLanguageProvider(
      <VoiceRecorder onTranscript={mockOnTranscript} onError={mockOnError} />
    );

    expect(screen.getByText(/How to use:/i)).toBeInTheDocument();
    expect(screen.getByText(/Click "Start Recording" and speak clearly/i)).toBeInTheDocument();
  });

  it('handles missing Web Speech API gracefully', () => {
    // Remove SpeechRecognition mock to simulate unsupported browser
    delete (window as any).SpeechRecognition;
    delete (window as any).webkitSpeechRecognition;

    const mockOnTranscript = jest.fn();
    const mockOnError = jest.fn();

    renderWithLanguageProvider(
      <VoiceRecorder onTranscript={mockOnTranscript} onError={mockOnError} />
    );

    // Component should still render without crashing
    expect(screen.getByText(/Voice Recorder/i)).toBeInTheDocument();
  });
});
