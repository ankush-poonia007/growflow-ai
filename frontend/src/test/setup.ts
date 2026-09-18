import '@testing-library/jest-dom/vitest';
import { afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';

// Automatically unmount React trees after each test
afterEach(() => {
  cleanup();
});
