import '../styles/tokens.css';
import { Providers } from './providers';
import DashboardPage from '../pages/DashboardPage';
import LoginPage from '../pages/LoginPage';
import { useUser } from '@clerk/react';
import { useState } from 'react';
import { useAuthSetup } from '../hooks/useAuthSetup';

function App() {
  return (
    <Providers>
      <AuthRouter />
    </Providers>
  );
}

function AuthRouter() {
  const { isSignedIn, isLoaded } = useUser();
  const [hasLoggedIn, setHasLoggedIn] = useState(false);

  useAuthSetup();

  if (!isLoaded) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh'
      }}>
        Loading...
      </div>
    );
  }

  if (!isSignedIn && !hasLoggedIn) {
    return <LoginPage onLoginSuccess={() => setHasLoggedIn(true)} />;
  }

  return <DashboardPage />;
}

export default App;
