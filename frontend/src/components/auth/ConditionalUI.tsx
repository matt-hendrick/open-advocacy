import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Button, Tooltip } from '@mui/material';
import LoginIcon from '@mui/icons-material/Login';

type ConditionalUIProps = {
  // Component or content to render if permissions pass
  children: React.ReactNode;
  // Optional array of roles that are allowed to see the component
  requiredRoles?: string[];
  // Whether authentication is required (defaults to true)
  requireAuth?: boolean;
  // What to show when the user doesn't have permission (defaults to nothing)
  // If 'login', will show a login button
  // If 'message', will show the specified message
  // If 'element', will show the fallback element
  fallback?: 'none' | 'login' | 'message' | 'element';
  // Message to show when user doesn't have permission (used with fallback='message')
  fallbackMessage?: string;
  // Element to show when user doesn't have permission (used with fallback='element')
  fallbackElement?: React.ReactNode;
  // Optional tooltip to display on the login button
  loginTooltip?: string;
  // Optional classes to apply to the container
  className?: string;
};

/**
 * Conditionally renders UI components based on user authentication and roles
 *
 * This component provides fine-grained access control at the UI element level
 * rather than protecting entire routes.
 */
const ConditionalUI: React.FC<ConditionalUIProps> = ({
  children,
  requiredRoles,
  requireAuth = true,
  fallback = 'none',
  fallbackMessage = 'You need additional permissions to access this feature',
  fallbackElement,
  loginTooltip = 'Sign in to access this feature',
  className,
}) => {
  const { checkPermission, redirectToLogin } = useAuth();

  // Check if user has permission to see this UI element
  const hasPermission = checkPermission(requiredRoles || null, requireAuth);

  // If user has permission, render the children
  if (hasPermission) {
    return <>{children}</>;
  }

  // Otherwise, render the appropriate fallback
  switch (fallback) {
    case 'login':
      return (
        <div className={className}>
          <Tooltip title={loginTooltip}>
            <Button
              variant="outlined"
              size="small"
              startIcon={<LoginIcon />}
              onClick={redirectToLogin}
            >
              Sign In
            </Button>
          </Tooltip>
        </div>
      );

    case 'message':
      return <div className={className}>{fallbackMessage}</div>;

    case 'element':
      return <div className={className}>{fallbackElement}</div>;

    case 'none':
    default:
      return null;
  }
};

export default ConditionalUI;
