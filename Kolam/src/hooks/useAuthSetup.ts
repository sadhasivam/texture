import { useAuth } from '@clerk/react';
import { useEffect } from 'react';
import { setAuthTokenGetter } from '../services/api';

export function useAuthSetup() {
  const { getToken } = useAuth();

  useEffect(() => {
    setAuthTokenGetter(() => getToken());
  }, [getToken]);
}
