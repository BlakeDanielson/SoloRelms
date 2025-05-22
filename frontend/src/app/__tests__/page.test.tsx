import React from 'react';
import { render, screen } from '@testing-library/react';
import Home from '../page'; // Adjust path to your Home page component

describe('Home Page', () => {
  it('renders a heading', () => {
    render(<Home />);
    // The default Next.js page has text like "Get started by editing src/app/page.tsx"
    // We look for part of this text. Adjust if your page.tsx is different.
    const mainContent = screen.getByText(/Get started by editing/i, { selector: 'p > code' });
    expect(mainContent).toBeInTheDocument();
  });
}); 