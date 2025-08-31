# Voice Interface - BazaarBrain Frontend

## Overview

The Voice Interface provides speech-to-text functionality using the Web Speech API, allowing users to:
- Record voice input for natural language queries
- Convert speech to text in real-time
- Play back recorded audio
- Support multiple languages (English, Spanish)

## Components

### VoiceRecorder
Main component for voice recording and transcription.

**Features:**
- 🎤 Start/Stop recording with visual feedback
- 🔊 Audio playback of recorded content
- 📝 Real-time speech-to-text conversion
- 🗑️ Clear recordings and transcripts
- 🌐 Internationalization support

**Props:**
```typescript
interface VoiceRecorderProps {
  onTranscript: (text: string) => void;  // Called when transcript is available
  onError?: (error: string) => void;     // Called when errors occur
}
```

### LanguageToggle
Component for switching between supported languages.

**Supported Languages:**
- 🇺🇸 English (en)
- 🇪🇸 Spanish (es)

## Technical Implementation

### Web Speech API
- **SpeechRecognition**: Real-time speech-to-text conversion
- **MediaRecorder**: Audio recording and playback
- **Browser Support**: Chrome, Edge, Safari (with prefixes)

### Audio Processing
- Audio captured as Blob data
- Local storage in browser memory
- WAV format for compatibility

### Error Handling
- Graceful fallback for unsupported browsers
- Microphone permission handling
- Network and API error management

## Usage

### Basic Implementation
```tsx
import VoiceRecorder from '../components/VoiceRecorder';

function MyComponent() {
  const handleTranscript = (text: string) => {
    console.log('User said:', text);
    // Process the transcript
  };

  return (
    <VoiceRecorder
      onTranscript={handleTranscript}
      onError={(error) => console.error(error)}
    />
  );
}
```

### With Language Context
```tsx
import { LanguageProvider } from '../contexts/LanguageContext';

function App() {
  return (
    <LanguageProvider>
      <VoiceRecorder onTranscript={handleTranscript} />
    </LanguageProvider>
  );
}
```

## Testing

### Running Tests
```bash
npm test              # Run all tests
npm run test:watch    # Run tests in watch mode
```

### Test Coverage
- Component rendering
- User interactions
- Error handling
- Browser compatibility
- Internationalization

## Browser Compatibility

| Feature | Chrome | Firefox | Safari | Edge |
|---------|--------|---------|--------|------|
| SpeechRecognition | ✅ | ❌ | ✅ (webkit) | ✅ |
| MediaRecorder | ✅ | ✅ | ✅ | ✅ |
| getUserMedia | ✅ | ✅ | ✅ | ✅ |

## Future Enhancements

### Planned Features
- [ ] Voice commands for navigation
- [ ] Offline speech recognition
- [ ] Custom wake word detection
- [ ] Voice biometrics
- [ ] Multi-language real-time translation

### Technical Improvements
- [ ] WebAssembly speech models
- [ ] Audio compression optimization
- [ ] Background noise reduction
- [ ] Voice activity detection

## Troubleshooting

### Common Issues

**"Speech recognition is not supported"**
- Use Chrome or Edge browser
- Check microphone permissions
- Ensure HTTPS connection (required for getUserMedia)

**"Failed to start recording"**
- Grant microphone access
- Check browser console for errors
- Verify Web Speech API support

**"No audio playback"**
- Check browser audio settings
- Ensure audio files are properly encoded
- Verify MediaRecorder support

### Debug Mode
Enable console logging for troubleshooting:
```typescript
const handleError = (error: string) => {
  console.error('Voice Error:', error);
  // Additional error handling
};
```

## Security Considerations

- Audio data stays local (no server transmission)
- Microphone access requires user consent
- HTTPS required for production use
- No persistent audio storage by default

## Performance Notes

- Real-time transcription uses browser resources
- Audio recording quality affects file size
- Speech recognition accuracy varies by accent/language
- Consider user's device capabilities

## Contributing

When adding new voice features:
1. Test across supported browsers
2. Add comprehensive error handling
3. Include accessibility features
4. Update language translations
5. Write unit tests for new functionality
