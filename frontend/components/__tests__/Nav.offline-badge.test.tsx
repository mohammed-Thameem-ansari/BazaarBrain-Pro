import { render, screen } from '@testing-library/react'
import React from 'react'
import Nav from '../../components/Nav'
import { OfflineProvider } from '../../contexts/OfflineContext'
import { LanguageProvider } from '../../contexts/LanguageContext'

describe('Nav offline badge', () => {
  it('shows unsynced badge when count > 0', () => {
    // seed localStorage for provider
    global.localStorage.setItem('BB_UNSYNCED', '2')
    render(
      <LanguageProvider>
        <OfflineProvider>
          <Nav />
        </OfflineProvider>
      </LanguageProvider>
    )
    expect(screen.getByText(/2 unsynced/i)).toBeInTheDocument()
  })
})
