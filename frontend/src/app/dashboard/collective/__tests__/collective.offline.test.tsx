import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import React from 'react'
import CollectivePage from '../page'
import * as collective from '../../../../lib/collective'

jest.mock('../../../../lib/collective')

describe('CollectivePage offline', () => {
  beforeEach(() => {
    (global.localStorage.getItem as jest.Mock).mockReturnValue('0')
    ;(collective.collectiveAPI.getMyOrders as jest.Mock).mockResolvedValue({ success: true, orders: [] })
  })

  it('increments offline badge when POST fails', async () => {
    ;(collective.collectiveAPI.placeOrder as jest.Mock).mockRejectedValue(new Error('offline'))
    render(<CollectivePage />)

    const button = await screen.findByRole('button', { name: /place/i })
    fireEvent.click(button)

    // OfflineProvider updates localStorage; verify setItem called with increment
    await waitFor(() => {
      expect(global.localStorage.setItem).toHaveBeenCalledWith('BB_UNSYNCED', '1')
    })
  })
})
