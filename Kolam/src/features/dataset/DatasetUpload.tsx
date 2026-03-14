import { useRef, useState } from 'react';
import { useDatasetUpload } from './useDatasetUpload';
import type { DatasetUploadResponse } from '../../types/dataset';
import './DatasetUpload.css';

interface DatasetUploadProps {
  onUploadComplete: (dataset: DatasetUploadResponse) => void;
}

export default function DatasetUpload({ onUploadComplete }: DatasetUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const uploadMutation = useDatasetUpload();

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (!file.name.endsWith('.csv')) {
        alert('Please select a CSV file');
        return;
      }
      setSelectedFile(file);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    try {
      const result = await uploadMutation.mutateAsync(selectedFile);
      onUploadComplete(result);
    } catch (error) {
      console.error('Upload failed:', error);
    }
  };

  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="dataset-upload">
      <div className="upload-area">
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv"
          onChange={handleFileChange}
          className="file-input"
        />

        <button
          type="button"
          className="upload-button"
          onClick={handleButtonClick}
          disabled={uploadMutation.isPending}
        >
          {selectedFile ? 'Change File' : 'Select CSV File'}
        </button>

        {selectedFile && (
          <div className="file-info">
            <p className="file-name">{selectedFile.name}</p>
            <p className="file-size">
              {(selectedFile.size / 1024).toFixed(2)} KB
            </p>
          </div>
        )}
      </div>

      {selectedFile && (
        <button
          type="button"
          className="upload-action"
          onClick={handleUpload}
          disabled={uploadMutation.isPending}
        >
          {uploadMutation.isPending ? 'Uploading...' : 'Upload Dataset'}
        </button>
      )}

      {uploadMutation.isError && (
        <div className="upload-error">
          <p>Upload failed. Please try again.</p>
        </div>
      )}
    </div>
  );
}
