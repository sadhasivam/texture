import { useMutation } from '@tanstack/react-query';
import { api } from '../../services/api';

export function useDatasetUpload() {
  return useMutation({
    mutationFn: (file: File) => api.uploadDataset(file),
  });
}
