import { render, screen, fireEvent } from '@testing-library/react';
import LanguageToggle from '../LanguageToggle';
import { LanguageProvider } from '../../contexts/LanguageContext';

const renderWithLanguageProvider = (component: React.ReactElement) => {
  return render(<LanguageProvider>{component}</LanguageProvider>);
};

describe('LanguageToggle', () => {
  it('renders language toggle component', () => {
    renderWithLanguageProvider(<LanguageToggle />);
    
    expect(screen.getByRole('combobox')).toBeInTheDocument();
  });

  it('shows English and Spanish options', () => {
    renderWithLanguageProvider(<LanguageToggle />);
    
    expect(screen.getByText('🇺🇸 English')).toBeInTheDocument();
    expect(screen.getByText('🇪🇸 Español')).toBeInTheDocument();
  });

  it('defaults to English language', () => {
    renderWithLanguageProvider(<LanguageToggle />);
    
    const select = screen.getByRole('combobox') as HTMLSelectElement;
    expect(select.value).toBe('en');
  });

  it('allows language selection', () => {
    renderWithLanguageProvider(<LanguageToggle />);
    
    const select = screen.getByRole('combobox') as HTMLSelectElement;
    fireEvent.change(select, { target: { value: 'es' } });
    
    expect(select.value).toBe('es');
  });

  it('has proper accessibility attributes', () => {
    renderWithLanguageProvider(<LanguageToggle />);
    
    const select = screen.getByRole('combobox');
    expect(select).toHaveAttribute('aria-label');
  });
});
