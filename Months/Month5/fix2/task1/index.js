// main.js or index.js
import { loadNetworkingTab, updateBackgroundColor, appState } from './networking.js';

// When initializing your app
if (typeof window !== 'undefined') {
    // Load the CSS file
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = './styles.css';
    document.head.appendChild(link);
}

// When switching to networking tab
loadNetworkingTab();

// When updating background color from design tab
updateBackgroundColor('#your-color-here');