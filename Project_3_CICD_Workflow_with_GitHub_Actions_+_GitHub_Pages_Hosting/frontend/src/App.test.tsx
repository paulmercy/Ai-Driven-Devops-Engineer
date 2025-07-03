import { render } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import App from './App';

describe('App Component', () => {
  it('renders without crashing', () => {
    const { container } = render(<App />);
    expect(container).toBeTruthy();
  });

  it('contains main heading', () => {
    const { container } = render(<App />);
    expect(container.textContent).toContain('CI/CD Demo Application');
  });

  it('displays deployment information', () => {
    const { container } = render(<App />);
    expect(container.textContent).toContain('Version:');
    expect(container.textContent).toContain('Build Time:');
    expect(container.textContent).toContain('Commit:');
  });

  it('shows pipeline features', () => {
    const { container } = render(<App />);
    expect(container.textContent).toContain('Pipeline Features Demonstrated');
    expect(container.textContent).toContain('Code linting with ESLint');
  });

  it('has interactive elements', () => {
    const { container } = render(<App />);
    expect(container.textContent).toContain('Interactive Counter');
    expect(container.textContent).toContain('Todo List');
  });
});