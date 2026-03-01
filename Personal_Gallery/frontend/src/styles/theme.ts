export const theme = {
  colors: {
    primary: '#4285F4',      // Google Blue
    secondary: '#34A853',    // Google Green
    danger: '#EA4335',       // Google Red
    warning: '#FBBC04',      // Google Yellow
    
    background: '#FFFFFF',
    backgroundDark: '#F5F5F5',
    buttonSecondary: '#D0D0D0',
    text: '#202124',
    textLight: '#5F6368',
    border: '#DADCE0',
  },
  
  spacing: {
    xs: '4px',
    sm: '8px',
    md: '16px',
    lg: '24px',
    xl: '32px',
    xxl: '48px',
  },
  
  borderRadius: {
    sm: '4px',
    md: '8px',
    lg: '12px',
    full: '9999px',
  },
  
  shadows: {
    sm: '0 1px 2px rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px rgba(0, 0, 0, 0.1)',
    lg: '0 10px 15px rgba(0, 0, 0, 0.1)',
  },
  
  breakpoints: {
    mobile: '480px',
    tablet: '768px',
    desktop: '1024px',
  },
};

export type Theme = typeof theme;