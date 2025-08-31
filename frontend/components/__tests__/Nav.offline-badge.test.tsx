import { render, screen } from '@testing-library/react'
import React from 'react'
import Nav from '../../components/Nav'
import { OfflineProvider } from '../../contexts/OfflineContext'

describe('Nav offline badge', () => {
  it('shows unsynced badge when count > 0', () => {
    // seed localStorage for provider
    (global.localStorage.getItem as jest.Mock).mockReturnValue('2')
    render(
      <OfflineProvider>
        <Nav />
      </OfflineProvider>
    )
    expect(screen.getByText(/2 unsynced/i)).toBeInTheDocument()
  })
})
