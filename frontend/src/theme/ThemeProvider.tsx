import React, { createContext, useState, useContext, useMemo, ReactNode } from 'react';
import { ThemeProvider as MuiThemeProvider, createTheme } from '@mui/material';
import { ThemeConfig, lightTheme } from './themes';
import CssBaseline from '@mui/material/CssBaseline';

interface ThemeContextProps {
  currentTheme: ThemeConfig;
  setTheme: (theme: ThemeConfig) => void;
}

const ThemeContext = createContext<ThemeContextProps>({
  currentTheme: lightTheme,
  setTheme: () => {},
});

export const useTheme = () => useContext(ThemeContext);

interface ThemeProviderProps {
  children: ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [currentTheme, setCurrentTheme] = useState<ThemeConfig>(lightTheme);

  const theme = useMemo(() => {
    return createTheme({
      palette: currentTheme.palette,
      typography: {
        fontFamily: currentTheme.fontFamily,
        h1: {
          fontWeight: 600,
        },
        h2: {
          fontWeight: 600,
        },
        h3: {
          fontWeight: 600,
        },
        h4: {
          fontWeight: 600,
        },
        h5: {
          fontWeight: 600,
        },
        h6: {
          fontWeight: 600,
        },
      },
      shape: {
        borderRadius: currentTheme.borderRadius,
      },
      components: {
        MuiCard: {
          styleOverrides: {
            root: {
              boxShadow: '0 4px 12px 0 rgba(0,0,0,0.05)',
              borderRadius: currentTheme.borderRadius,
            },
          },
        },
        MuiButton: {
          styleOverrides: {
            root: {
              textTransform: 'none',
              fontWeight: 600,
              borderRadius: currentTheme.borderRadius,
            },
          },
        },
        MuiChip: {
          styleOverrides: {
            root: {
              fontWeight: 500,
            },
          },
        },
      },
    });
  }, [currentTheme]);

  const contextValue = useMemo(() => {
    return {
      currentTheme,
      setTheme: setCurrentTheme,
    };
  }, [currentTheme]);

  return (
    <ThemeContext.Provider value={contextValue}>
      <MuiThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </MuiThemeProvider>
    </ThemeContext.Provider>
  );
};
