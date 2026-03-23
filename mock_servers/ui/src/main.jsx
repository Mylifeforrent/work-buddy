import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

// The TOOL_ID is injected by the FastAPI server in index.html
window.TOOL_ID = window.TOOL_ID || 'react-app';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
