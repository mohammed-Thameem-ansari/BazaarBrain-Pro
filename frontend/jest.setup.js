import '@testing-library/jest-dom'

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter() {
    return {
      push: jest.fn(),
      replace: jest.fn(),
      prefetch: jest.fn(),
      back: jest.fn(),
      forward: jest.fn(),
      refresh: jest.fn(),
    }
  },
  useSearchParams() {
    return new URLSearchParams()
  },
  usePathname() {
    return '/'
  },
}))

// Mock localStorage with stable function identities
const localStorageMock = (() => {
  const store = new Map()
  return {
    getItem: jest.fn((key) => (store.has(key) ? store.get(key) : null)),
    setItem: jest.fn((key, value) => { store.set(key, value) }),
    removeItem: jest.fn((key) => { store.delete(key) }),
    clear: jest.fn(() => { store.clear() }),
  }
})()
Object.defineProperty(window, 'localStorage', { value: localStorageMock, configurable: true, writable: true })
// @ts-ignore
global.localStorage = window.localStorage

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
})

// Mock Web Speech API (speechSynthesis) for tests using TTS
if (!('speechSynthesis' in window)) {
  window.speechSynthesis = {
    speak: jest.fn(),
    cancel: jest.fn(),
    paused: false,
    pending: false,
    speaking: false,
    getVoices: jest.fn(() => []),
    pause: jest.fn(),
    resume: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    onvoiceschanged: null,
  }
}

if (!('SpeechSynthesisUtterance' in window)) {
  // Minimal constructor stub
  // eslint-disable-next-line @typescript-eslint/no-empty-function
  window.SpeechSynthesisUtterance = function (text) { this.text = text; this.lang = 'en-US'; this.rate = 1; this.pitch = 1 }
}
