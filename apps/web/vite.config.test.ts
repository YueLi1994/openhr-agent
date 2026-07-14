import { expect, test } from 'vitest'

import { DEV_PROXY } from './vite.config'

test('development proxy preserves API paths and proxies health separately', () => {
  expect(DEV_PROXY['/api']).toEqual({ target: 'http://127.0.0.1:8000' })
  expect(DEV_PROXY['/health']).toEqual({ target: 'http://127.0.0.1:8000' })
  expect(DEV_PROXY['/api']).not.toHaveProperty('rewrite')
})
