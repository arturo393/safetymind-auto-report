import '@testing-library/jest-dom'
import { vi } from 'vitest'

// Mock for ResizeObserver which is not present in JSDOM
class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}

vi.stubGlobal('ResizeObserver', ResizeObserver)
