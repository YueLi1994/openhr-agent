import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, expect, test, vi } from 'vitest'
import { AgentResponse, App, EvaluationSummary, EXAMPLE_QUESTIONS } from './App'

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

const evaluation: EvaluationSummary = {
  total_cases: 32, passed_cases: 31, failed_cases: 1, pass_rate: 0.9688,
  routing_accuracy: 1, escalation_accuracy: 1, blocking_accuracy: 1,
  citation_validity_rate: 1, grounded_answer_rate: 1, average_latency_ms: 0.2,
  results: [
    { case_id: 'EVAL-001', category: 'general_policy', passed: true, score: 1, failures: [], expected: { domain: 'general_policy' }, actual: { domain: 'general_policy' }, latency_ms: 0.1 },
    { case_id: 'EVAL-002', category: 'safety', passed: false, score: 0.8, failures: ['blocking assertion failed'], expected: { blocked: true }, actual: { blocked: false }, latency_ms: 0.3 },
  ],
}

test('switches from Agent Demo to Evaluation and renders it', () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true }))
  render(<App />)
  fireEvent.click(screen.getByRole('button', { name: 'Evaluation' }))
  expect(screen.getByRole('heading', { name: 'Deterministic Agent checks' })).toBeInTheDocument()
})

test('runs evaluation and displays summary metrics', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce({ ok: true }).mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(evaluation) }))
  render(<App />)
  fireEvent.click(screen.getByRole('button', { name: 'Evaluation' }))
  fireEvent.click(screen.getByRole('button', { name: 'Run Evaluation' }))
  expect(await screen.findByText('96.9%')).toBeInTheDocument()
  expect(screen.getByText('31 / 1')).toBeInTheDocument()
})

test('filters failed evaluation cases and shows failure reasons', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce({ ok: true }).mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(evaluation) }))
  render(<App />)
  fireEvent.click(screen.getByRole('button', { name: 'Evaluation' }))
  fireEvent.click(screen.getByRole('button', { name: 'Run Evaluation' }))
  await screen.findByText('EVAL-001')
  fireEvent.click(screen.getByRole('checkbox', { name: /failures only/i }))
  expect(screen.queryByText('EVAL-001')).not.toBeInTheDocument()
  fireEvent.click(screen.getByText('EVAL-002'))
  expect(screen.getByText('blocking assertion failed')).toBeInTheDocument()
})

test('shows evaluation API error state', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce({ ok: true }).mockResolvedValueOnce({ ok: false, status: 503 }))
  render(<App />)
  fireEvent.click(screen.getByRole('button', { name: 'Evaluation' }))
  fireEvent.click(screen.getByRole('button', { name: 'Run Evaluation' }))
  expect(await screen.findByRole('alert')).toHaveTextContent('Evaluation request failed (503)')
})
