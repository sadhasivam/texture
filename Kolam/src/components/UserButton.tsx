import { UserButton as ClerkUserButton } from '@clerk/react';

export default function UserButton() {
  return (
    <div style={{
      position: 'fixed',
      top: '1rem',
      right: '1rem',
      zIndex: 1000
    }}>
      <ClerkUserButton
        appearance={{
          elements: {
            avatarBox: {
              width: '40px',
              height: '40px',
            },
          },
        }}
      />
    </div>
  );
}
