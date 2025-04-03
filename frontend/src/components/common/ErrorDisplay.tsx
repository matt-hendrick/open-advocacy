import React from 'react';
import { Alert, AlertTitle, Box, Button } from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';

interface ErrorDisplayProps {
  message: string;
  onRetry?: () => void;
}

const ErrorDisplay: React.FC<ErrorDisplayProps> = ({ message, onRetry }) => {
  return (
    <Box my={3}>
      <Alert
        severity="error"
        action={
          onRetry ? (
            <Button color="inherit" size="small" startIcon={<RefreshIcon />} onClick={onRetry}>
              Retry
            </Button>
          ) : undefined
        }
      >
        <AlertTitle>Error</AlertTitle>
        {message}
      </Alert>
    </Box>
  );
};

export default ErrorDisplay;
