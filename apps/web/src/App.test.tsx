import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, expect, test, vi } from 'vitest'
import { AgentResponse, App, EXAMPLE_QUESTIONS } from './App'

const success: AgentResponse = {
  answer: 'Full-time employees receive 18 days. [leave-policy]',
  domain: 'leave_and_attendance',
  sources: [{ source_id: 'leave-policy', title: 'Leave Policy', domain: 'leave_and_attendance', excerpt: 'Full-time employees receive 18 days.', relevance_score: 0.9 }],
  confidence: 0.88,
  missing_information: [],
  requires_human_review: false,
  escalation_reason: null,
  structured_data: { routing: { primary_domain: 'leave_and_attendance', detected_domains: ['leave_and_attendance'], is_multi_intent: false, confidence: 0.88, requires_employee_context: false, requires_human_review: false, reasoning_summary: 'Matched leave keywords.' }, workflow_steps: ['input_validation', 'knowledge_retrieval'], execution_ms: 1.2, provider: 'mock-v2' },
}

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})

function mockFetch(chat: AgentResponse = success) {
  vi.stubGlobal('fetch', vi.fn()
    .mockResolvedValueOnce({ ok: true })
    .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(chat) }))
}

test('renders the HR Agent page', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true }))
  render(<App />)
  expect(screen.getByRole('heading', { name: /openhr agent/i })).toBeInTheDocument()
  expect(await screen.findByText('API connected')).toBeInTheDocument()
})

test('selects an example question', () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true }))
  render(<App />)
  fireEvent.click(screen.getByRole('button', { name: /reimbursement limit/i }))
  expect(screen.getByLabelText('Question')).toHaveValue(EXAMPLE_QUESTIONS[5])
})

test('shows a successful Agent answer', async () => {
  mockFetch()
  render(<App />)
  fireEvent.click(screen.getByRole('button', { name: /run agent workflow/i }))
  expect((await screen.findAllByText(/Full-time employees receive 18 days/)).length).toBeGreaterThan(0)
  expect(screen.getByText('88%')).toBeInTheDocument()
})

test('shows cited knowledge sources', async () => {
  mockFetch()
  render(<App />)
  fireEvent.click(screen.getByRole('button', { name: /run agent workflow/i }))
  expect(await screen.findByText('Leave Policy')).toBeInTheDocument()
  expect(screen.getByText('[leave-policy]')).toBeInTheDocument()
})

test('shows human escalation warning', async () => {
  mockFetch({ ...success, requires_human_review: true, escalation_reason: 'Employment decision requires HR review.', sources: [] })
  render(<App />)
  fireEvent.click(screen.getByRole('button', { name: /run agent workflow/i }))
  expect(await screen.findByText('Human review required')).toBeInTheDocument()
  expect(screen.getAllByText(/Employment decision requires HR review/).length).toBeGreaterThan(0)
})

test('shows API failure state', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce({ ok: true }).mockResolvedValueOnce({ ok: false, status: 500 }))
  render(<App />)
  fireEvent.click(screen.getByRole('button', { name: /run agent workflow/i }))
  await waitFor(() => expect(screen.getByText('API request failed')).toBeInTheDocument())
  expect(screen.getByText('Request failed (500)')).toBeInTheDocument()
})
