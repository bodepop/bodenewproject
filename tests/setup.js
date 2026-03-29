// Test setup for Jest and jsdom
import { readFileSync } from 'fs';
import { join } from 'path';

// Load HTML and CSS for testing
const htmlContent = readFileSync(join(process.cwd(), 'index.html'), 'utf8');
const cssContent = readFileSync(join(process.cwd(), 'css/styles.css'), 'utf8');

// Setup DOM for each test
beforeEach(() => {
  document.documentElement.innerHTML = htmlContent;
  
  // Add CSS to the document
  const style = document.createElement('style');
  style.textContent = cssContent;
  document.head.appendChild(style);
});

// Clean up after each test
afterEach(() => {
  document.documentElement.innerHTML = '';
});