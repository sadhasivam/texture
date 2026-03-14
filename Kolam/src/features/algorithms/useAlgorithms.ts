import { useQuery } from '@tanstack/react-query';
import { api } from '../../services/api';

export function useAlgorithms() {
  return useQuery({
    queryKey: ['algorithms'],
    queryFn: api.listAlgorithms,
  });
}

export function useAlgorithmMetadata(algorithmId: string | null) {
  return useQuery({
    queryKey: ['algorithm', algorithmId],
    queryFn: () => api.getAlgorithmMetadata(algorithmId!),
    enabled: !!algorithmId,
  });
}
