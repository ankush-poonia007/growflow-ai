import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './App';

/* Import order matters: reset → tokens → typography → global */
import './styles/reset.css';
import './styles/tokens.css';
import './styles/typography.css';
import './styles/global.css';

const root = document.getElementById('root');
if (!root) throw new Error('Root element not found');

createRoot(root).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
