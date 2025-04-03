// src/theme/themes.ts
import { ThemeOptions, PaletteOptions } from '@mui/material';

export interface ThemeConfig {
  name: string;
  palette: PaletteOptions;
  borderRadius: number;
  fontFamily: string;
}

export const lightTheme: ThemeConfig = {
  name: 'light',
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2', // Vibrant blue
      light: '#42a5f5',
      dark: '#1565c0',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#26a69a', // Teal-like
      light: '#4db6ac',
      dark: '#00897b',
      contrastText: '#ffffff',
    },
    background: {
      default: '#f5f7fa',
      paper: '#ffffff',
    },
    text: {
      primary: '#2c3e50',
      secondary: '#546e7a',
    },
  },
  borderRadius: 8,
  fontFamily: '"Poppins", "Roboto", "Helvetica", "Arial", sans-serif',
};

export const darkTheme: ThemeConfig = {
  name: 'dark',
  palette: {
    mode: 'dark',
    primary: {
      main: '#42a5f5', // Lighter blue for dark mode
      light: '#64b5f6',
      dark: '#1e88e5',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#4db6ac', // Lighter teal for dark mode
      light: '#80cbc4',
      dark: '#26a69a',
      contrastText: '#ffffff',
    },
    background: {
      default: '#121212',
      paper: '#1e1e1e',
    },
    text: {
      primary: '#f5f5f5',
      secondary: '#b0bec5',
    },
  },
  borderRadius: 8,
  fontFamily: '"Poppins", "Roboto", "Helvetica", "Arial", sans-serif',
};

// Add more themes as needed
export const availableThemes = [lightTheme, darkTheme];
