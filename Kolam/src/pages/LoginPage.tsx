import { SignIn, useUser } from '@clerk/react';
import { useEffect } from 'react';

interface LoginPageProps {
  onLoginSuccess: () => void;
}

export default function LoginPage({ onLoginSuccess }: LoginPageProps) {
  const { isSignedIn } = useUser();

  useEffect(() => {
    if (isSignedIn) {
      onLoginSuccess();
    }
  }, [isSignedIn, onLoginSuccess]);

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      background: '#fafafa'
    }}>
      <div style={{ textAlign: 'center' }}>
        <h1 style={{ marginBottom: '2rem', fontSize: '2rem', fontWeight: 600 }}>
          Texture
        </h1>
        <SignIn
          appearance={{
            elements: {
              rootBox: {
                margin: '0 auto',
              },
            },
          }}
        />
      </div>
    </div>
  );
}
