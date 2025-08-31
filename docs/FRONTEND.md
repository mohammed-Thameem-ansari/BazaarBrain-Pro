# BazaarBrain Frontend Documentation

## Overview

BazaarBrain Frontend is a modern React application built with Next.js, providing an intuitive interface for shopkeepers to interact with AI-powered business intelligence tools. The application features voice interfaces, real-time analytics, and comprehensive transaction management.

### Day 6 additions:
- Collective Orders dashboard with offline-first UX (unsynced badge in nav)
- Voice page wired to Intake endpoint; TTS summaries with mute toggle
- Simulation dashboard narrates result summaries via TTS
- AuthContext for JWT storage/usage; OfflineContext for unsynced counter

## Tech Stack

### Core Technologies
- **Next.js 15.5.2** - React framework with App Router
- **React 19.1.0** - UI library with latest features
- **TypeScript 5** - Type-safe JavaScript development
- **TailwindCSS 4** - Utility-first CSS framework

### UI Libraries
- **shadcn/ui** - High-quality React components
- **Framer Motion** - Animation library for smooth transitions
- **Recharts** - Charting library for data visualization
- **Headless UI** - Unstyled, accessible UI components

### State Management & Data
- **React Context** - Lightweight state management
- **Axios** - HTTP client for API communication
- **localStorage** - Client-side data persistence

### Development Tools
- **Jest** - Testing framework
- **React Testing Library** - Component testing utilities
- **ESLint** - Code linting and formatting

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── dashboard/          # Dashboard page
│   │   ├── login/             # Authentication page
const API = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000',
│   │   ├── voice/             # Voice interface page
│   │   ├── history/           # Transaction history page
│   │   ├── globals.css        # Global styles
│   │   ├── layout.tsx         # Root layout
│   │   └── page.tsx           # Landing page
│   ├── components/            # Reusable UI components
│   │   ├── Nav.tsx            # Navigation component
│   │   ├── VoiceRecorder.tsx  # Voice recording interface
│   │   ├── SimulationDashboard.tsx # Business simulation UI
│   │   ├── UploadReceipt.tsx  # Receipt upload interface
│   │   ├── TransactionHistory.tsx # Transaction display
│   │   ├── SimulationHistory.tsx # Simulation history
│   │   ├── ArbitrationPanel.tsx # AI decision display
│   │   ├── ErrorBoundary.tsx  # Error handling component
│   │   └── SkeletonLoader.tsx # Loading state components
│   ├── contexts/              # React Context providers
│   │   └── LanguageContext.tsx # Internationalization
│   ├── lib/                   # Utility libraries
│   │   ├── api.ts             # Axios configuration
│   │   ├── auth.ts            # Authentication utilities
│   │   ├── receipts.ts        # Receipt API functions
│   │   ├── simulations.ts     # Simulation API functions
│   │   └── transactions.ts    # Transaction API functions
│   └── types/                 # TypeScript type definitions
│       └── global.d.ts        # Global type declarations
├── components/                 # Additional components (legacy)
├── public/                    # Static assets
├── tests/                     # Test files
├── package.json               # Dependencies and scripts
├── tailwind.config.ts         # TailwindCSS configuration
├── jest.config.js             # Jest testing configuration
└── README.md                  # Project documentation
```

## Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn package manager
- Modern web browser with Web Speech API support

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd BazaarBrain-Pro/frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your configuration
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

5. **Open in browser**
   Navigate to `http://localhost:3000`

### Environment Variables

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000

# Feature Flags
NEXT_PUBLIC_ENABLE_VOICE=true
NEXT_PUBLIC_ENABLE_ANALYTICS=true
```

## Core Components

### Navigation (`Nav.tsx`)

The main navigation component providing:
- Responsive navigation menu
- Language toggle (English/Spanish)
- Authentication status
- Mobile-friendly hamburger menu

**Usage:**
```tsx
import Nav from '../components/Nav';

function Layout() {
  return (
    <div>
      <Nav />
      <main>{children}</main>
    </div>
  );
  ### Collective Orders & Offline Ledger

  - Page: `src/app/dashboard/collective/page.tsx`
  - Client: `lib/collective.ts`
  - Backend endpoints:
    - POST `/api/v1/collective_order` to place/join
    - GET `/api/v1/collective_order` to read aggregates

  Offline behavior:
  - If POST fails (e.g., no network), the UI increments an unsynced counter via `OfflineContext` and shows a badge in `Nav`.
  - On subsequent GET, backend tries to sync the SQLite offline ledger into Supabase when available.

  ### Voice Integration

  - Page: `src/app/voice/page.tsx` uses `VoiceRecorder` and calls `/api/v1/intake`.
  - TTS: `lib/tts.ts` provides `useTextToSpeech()` with a mute toggle and locale from `LanguageContext`.

  ### Simulation Dashboard with TTS

  - Component: `components/SimulationDashboard.tsx`
  - Calls `/api/v1/simulate` and speaks a concise summary.

}
```

### Voice Interface (`VoiceRecorder.tsx`)

Advanced voice recording and transcription component featuring:
- Real-time speech-to-text conversion
- Audio recording and playback
- Multi-language support
- Accessibility features (ARIA labels, keyboard navigation)

**Features:**
- 🎤 Start/Stop recording with visual feedback
- 🔊 Audio playback of recorded content
- 📝 Real-time speech-to-text conversion
- 🗑️ Clear recordings and transcripts
- 🌐 Internationalization support

**Props:**
```tsx
interface VoiceRecorderProps {
  onTranscript: (text: string) => void;  // Called when transcript is available
  onError?: (error: string) => void;     // Called when errors occur
}
```

**Usage:**
```tsx
import VoiceRecorder from '../components/VoiceRecorder';

function VoicePage() {
  const handleTranscript = (text: string) => {
    console.log('User said:', text);
  };

  return (
    <VoiceRecorder
      onTranscript={handleTranscript}
      onError={(error) => console.error(error)}
    />
  );
}
```

### Business Simulation (`SimulationDashboard.tsx`)

Comprehensive business scenario analysis interface with:
- Natural language query input
- Advanced form-based simulation
- Real-time results with charts
- Impact analysis and recommendations

**Features:**
- 📊 Interactive charts (Recharts integration)
- 📈 Before/After comparisons
- 💡 AI-powered recommendations
- 🎯 Confidence scoring
- 📋 Key assumptions display

### Receipt Upload (`UploadReceipt.tsx`)

Drag-and-drop receipt processing interface:
- Image upload and preview
- OCR result display
- Integration with simulation tools
- Progress tracking and error handling

## Internationalization

### Language Support

The application supports multiple languages through the `LanguageContext`:

- **English (en)** - Default language
- **Spanish (es)** - Full translation support

### Adding New Languages

1. **Extend translations object:**
   ```tsx
   const translations = {
     en: { /* English translations */ },
     es: { /* Spanish translations */ },
     fr: { /* French translations */ }  // New language
   };
   ```

2. **Add language to LanguageToggle:**
   ```tsx
   const languages = [
     { code: 'en', name: 'English', flag: '🇺🇸' },
     { code: 'es', name: 'Español', flag: '🇪🇸' },
     { code: 'fr', name: 'Français', flag: '🇫🇷' }  // New language
   ];
   ```

### Translation Keys

Use the `useLanguage` hook to access translations:

```tsx
import { useLanguage } from '../contexts/LanguageContext';

function MyComponent() {
  const { t, language, setLanguage } = useLanguage();
  
  return (
    <div>
      <h1>{t('common.title')}</h1>
      <p>Current language: {language}</p>
      <button onClick={() => setLanguage('es')}>
        Switch to Spanish
      </button>
    </div>
  );
}
```

## API Integration

### API Client Configuration

The application uses a centralized Axios client with:
- Automatic JWT token attachment
- Request/response interceptors
- Error handling and retry logic
- Base URL configuration

**Configuration:**
```tsx
// lib/api.ts
const API = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
});

// JWT token interceptor
API.interceptors.request.use((config) => {
  const token = localStorage.getItem('BB_TOKEN');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### API Modules

Organized by feature domain:

- **`auth.ts`** - Authentication endpoints
- **`receipts.ts`** - Receipt processing
- **`simulations.ts`** - Business simulations
- **`transactions.ts`** - Transaction management

**Usage Example:**
```tsx
import { receiptsAPI } from '../lib/receipts';

const handleUpload = async (file: File) => {
  try {
    const result = await receiptsAPI.uploadReceipt(file, 'receipt');
    if (result.success) {
      console.log('Upload successful:', result.result);
    }
  } catch (error) {
    console.error('Upload failed:', error);
  }
};
```

## State Management

### React Context Pattern

Lightweight state management using React Context API:

```tsx
// contexts/LanguageContext.tsx
const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState('en');
  
  const value = {
    language,
    setLanguage: (lang: string) => {
      setLanguage(lang);
      localStorage.setItem('BB_LANGUAGE', lang);
    },
    t: (key: string) => translations[language]?.[key] || key
  };
  
  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
}
```

### Local Storage Persistence

User preferences and settings are persisted in localStorage:
- Language selection
- Authentication tokens
- User preferences

## Styling & Design System

### TailwindCSS Configuration

Custom design tokens and responsive breakpoints:

```ts
// tailwind.config.ts
const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        primary: "var(--primary)",
        // ... more custom colors
      },
      fontFamily: {
        sans: ["var(--font-geist-sans)", "Arial", "sans-serif"],
        mono: ["var(--font-geist-mono)", "monospace"],
      },
    },
  },
  plugins: [],
};
```

### CSS Custom Properties

Dynamic theming with CSS variables:

```css
:root {
  --background: #ffffff;
  --foreground: #171717;
  --primary: #3b82f6;
  --primary-foreground: #ffffff;
  /* ... more variables */
}

@media (prefers-color-scheme: dark) {
  :root {
    --background: #0a0a0a;
    --foreground: #ededed;
    /* ... dark theme variables */
  }
}
```

### Component Variants

Consistent component styling with TailwindCSS:

```tsx
const buttonVariants = {
  primary: "bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500",
  secondary: "bg-gray-100 text-gray-700 hover:bg-gray-200 focus:ring-gray-500",
  danger: "bg-red-600 text-white hover:bg-red-700 focus:ring-red-500"
};

function Button({ variant = 'primary', children, ...props }) {
  return (
    <button 
      className={`px-4 py-2 rounded-lg font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors ${buttonVariants[variant]}`}
      {...props}
    >
      {children}
    </button>
  );
}
```

## Animation & Transitions

### Framer Motion Integration

Smooth animations and micro-interactions:

```tsx
import { motion, AnimatePresence } from 'framer-motion';

function AnimatedComponent() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
    >
      Content with animation
    </motion.div>
  );
}
```

### Loading States

Skeleton loaders and loading animations:

```tsx
import { SkeletonCard, SkeletonTable } from '../components/SkeletonLoader';

function LoadingState() {
  return (
    <div className="space-y-6">
      <SkeletonCard />
      <SkeletonTable rows={5} columns={4} />
    </div>
  );
}
```

## Testing

### Testing Setup

Comprehensive testing with Jest and React Testing Library:

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

### Test Configuration

```js
// jest.config.js
const nextJest = require('next/jest');

const createJestConfig = nextJest({
  dir: './',
});

const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jsdom',
  testPathIgnorePatterns: ['<rootDir>/.next/', '<rootDir>/node_modules/'],
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
};

module.exports = createJestConfig(customJestConfig);
```

### Test Examples

**Component Testing:**
```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import VoiceRecorder from '../VoiceRecorder';

describe('VoiceRecorder', () => {
  it('renders voice recorder component', () => {
    const mockOnTranscript = jest.fn();
    const mockOnError = jest.fn();

    render(
      <VoiceRecorder 
        onTranscript={mockOnTranscript} 
        onError={mockOnError} 
      />
    );

    expect(screen.getByText(/Voice Recorder/i)).toBeInTheDocument();
    expect(screen.getByText(/Start Recording/i)).toBeInTheDocument();
  });
});
```

**Context Testing:**
```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { LanguageProvider, useLanguage } from '../LanguageContext';

const TestComponent = () => {
  const { language, setLanguage } = useLanguage();
  return (
    <div>
      <span data-testid="language">{language}</span>
      <button onClick={() => setLanguage('es')}>Spanish</button>
    </div>
  );
};

describe('LanguageContext', () => {
  it('provides language context', () => {
    render(
      <LanguageProvider>
        <TestComponent />
      </LanguageProvider>
    );

    expect(screen.getByTestId('language')).toHaveTextContent('en');
  });
});
```

## Performance Optimization

### React.memo & useCallback

Prevent unnecessary re-renders:

```tsx
import React, { useCallback, useMemo } from 'react';

const OptimizedComponent = React.memo(({ data, onAction }) => {
  const processedData = useMemo(() => {
    return data.map(item => ({ ...item, processed: true }));
  }, [data]);

  const handleAction = useCallback(() => {
    onAction(processedData);
  }, [onAction, processedData]);

  return (
    <div>
      {processedData.map(item => (
        <div key={item.id}>{item.name}</div>
      ))}
      <button onClick={handleAction}>Process</button>
    </div>
  );
});
```

### Dynamic Imports

Code splitting for better performance:

```tsx
import dynamic from 'next/dynamic';

const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
  loading: () => <SkeletonCard />,
  ssr: false
});
```

### Image Optimization

Next.js Image component for optimized images:

```tsx
import Image from 'next/image';

function OptimizedImage() {
  return (
    <Image
      src="/receipt-example.jpg"
      alt="Receipt example"
      width={400}
      height={300}
      priority={false}
      placeholder="blur"
      blurDataURL="data:image/jpeg;base64,..."
    />
  );
}
```

## Accessibility

### ARIA Labels & Roles

Comprehensive accessibility support:

```tsx
function AccessibleComponent() {
  return (
    <div>
      <button
        aria-label="Start voice recording"
        aria-describedby="recording-instructions"
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && handleClick()}
      >
        Start Recording
      </button>
      
      <div id="recording-instructions" role="region" aria-live="polite">
        Instructions for voice recording
      </div>
    </div>
  );
}
```

### Keyboard Navigation

Full keyboard accessibility:

```tsx
function KeyboardAccessibleComponent() {
  const handleKeyDown = (e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'Enter':
      case ' ':
        e.preventDefault();
        handleAction();
        break;
      case 'Escape':
        handleClose();
        break;
    }
  };

  return (
    <button
      onKeyDown={handleKeyDown}
      tabIndex={0}
      role="button"
    >
      Action Button
    </button>
  );
}
```

### Screen Reader Support

Semantic HTML and screen reader announcements:

```tsx
function ScreenReaderFriendly() {
  return (
    <div>
      <h1>Page Title</h1>
      <nav aria-label="Main navigation">
        <ul role="menubar">
          <li role="menuitem"><a href="/dashboard">Dashboard</a></li>
        </ul>
      </nav>
      
      <main role="main">
        <section aria-labelledby="section-title">
          <h2 id="section-title">Section Title</h2>
          <p>Content with proper heading structure</p>
        </section>
      </main>
    </div>
  );
}
```

## Error Handling

### Error Boundaries

React Error Boundaries for graceful error handling:

```tsx
import ErrorBoundary from '../components/ErrorBoundary';

function App() {
  return (
    <ErrorBoundary
      fallback={<CustomErrorUI />}
      onError={(error, errorInfo) => {
        console.error('App error:', error, errorInfo);
        // Send to error reporting service
      }}
    >
      <MainApp />
    </ErrorBoundary>
  );
}
```

### API Error Handling

Comprehensive error handling for API calls:

```tsx
const handleApiCall = async () => {
  try {
    const result = await api.getData();
    return { success: true, data: result };
  } catch (error) {
    if (error.response?.status === 401) {
      // Handle unauthorized
      redirectToLogin();
    } else if (error.response?.status === 500) {
      // Handle server error
      showServerError();
    } else {
      // Handle network error
      showNetworkError();
    }
    return { success: false, error: error.message };
  }
};
```

## Deployment

### Build Process

Production build optimization:

```bash
# Build for production
npm run build

# Start production server
npm start

# Export static files (if needed)
npm run export
```

### Environment Configuration

Environment-specific settings:

```bash
# Development
npm run dev

# Production
NODE_ENV=production npm start

# Staging
NODE_ENV=staging npm start
```

### Performance Monitoring

Lighthouse CI integration:

```bash
# Install Lighthouse CI
npm install -g @lhci/cli

# Run performance audit
lhci autorun
```

## Troubleshooting

### Common Issues

**Voice Recording Not Working:**
- Check browser compatibility (Chrome/Edge recommended)
- Ensure microphone permissions are granted
- Verify HTTPS connection (required for getUserMedia)

**Charts Not Rendering:**
- Check if data is properly formatted
- Verify Recharts dependencies are installed
- Ensure responsive container has proper dimensions

**Language Switching Issues:**
- Clear localStorage and refresh page
- Check if LanguageProvider wraps the component tree
- Verify translation keys exist

**Build Errors:**
- Clear `.next` folder and node_modules
- Update dependencies to compatible versions
- Check TypeScript configuration

### Debug Mode

Enable debug logging:

```tsx
// Enable debug mode
localStorage.setItem('BB_DEBUG', 'true');

// Debug logging
if (process.env.NODE_ENV === 'development' || localStorage.getItem('BB_DEBUG')) {
  console.log('Debug info:', data);
}
```

## Contributing

### Development Guidelines

1. **Code Style**
   - Use TypeScript for all new components
   - Follow ESLint configuration
   - Use Prettier for code formatting

2. **Component Structure**
   - One component per file
   - Export as default with React.memo when appropriate
   - Include proper TypeScript interfaces

3. **Testing Requirements**
   - Write tests for new components
   - Maintain test coverage above 80%
   - Use meaningful test descriptions

4. **Accessibility**
   - Include ARIA labels for interactive elements
   - Ensure keyboard navigation works
   - Test with screen readers

### Pull Request Process

1. Create feature branch from `main`
2. Implement changes with tests
3. Update documentation
4. Submit PR with detailed description
5. Address review feedback
6. Merge after approval

## Support & Resources

### Documentation
- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [TailwindCSS Documentation](https://tailwindcss.com/docs)
- [Framer Motion Documentation](https://www.framer.com/motion/)

### Community
- [GitHub Issues](https://github.com/your-repo/issues)
- [Discord Community](https://discord.gg/your-community)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/bazaarbrain)

### Performance Tools
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)
- [WebPageTest](https://www.webpagetest.org/)
- [Bundle Analyzer](https://www.npmjs.com/package/@next/bundle-analyzer)

---

**Last Updated:** December 2024  
**Version:** 1.0.0  
**Maintainer:** BazaarBrain Team
