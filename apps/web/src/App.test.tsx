import { render, screen } from '@testing-library/react'
import { expect, test, vi } from 'vitest'
import { App } from './App'

test('renders the welcome page and connected API state', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: () => Promise.resolve({ status: 'ok' }) }))
  render(<App />)
  expect(screen.getByRole('heading', { name: /build safer hr agents/i })).toBeInTheDocument()
  expect(await screen.findByText('API connected')).toBeInTheDocument()
  vi.unstubAllGlobals()
})
