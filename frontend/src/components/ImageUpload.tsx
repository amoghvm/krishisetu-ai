import React, { useState, useEffect, useCallback } from 'react';

interface ImageUploadProps {
  selectedImage: File | null;
  onImageSelect: (file: File | null) => void;
  error?: string | null;
}

const SUPPORTED_FORMATS: ReadonlyArray<string> = ['image/jpeg', 'image/png', 'image/webp'];
const MAX_SIZE_MB = 10;

export default function ImageUpload({ selectedImage, onImageSelect, error }: ImageUploadProps) {
  const [preview, setPreview] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [localError, setLocalError] = useState<string | null>(error || null);

  useEffect(() => {
    if (selectedImage) {
      const url = URL.createObjectURL(selectedImage);
      setPreview(url);
      return () => URL.revokeObjectURL(url);
    } else {
      setPreview(null);
    }
  }, [selectedImage]);

  useEffect(() => {
    setLocalError(error || null);
  }, [error]);

  const validateFile = (file: File): string | null => {
    if (!SUPPORTED_FORMATS.includes(file.type)) {
      return `Unsupported format: ${file.type || 'unknown'}. Supported: JPEG, PNG, WEBP`;
    }
    if (file.size > MAX_SIZE_MB * 1024 * 1024) {
      return `File too large (${(file.size / (1024 * 1024)).toFixed(1)} MB). Maximum is ${MAX_SIZE_MB} MB.`;
    }
    return null;
  };

  const handleFileSelect = useCallback((file: File) => {
    const validationError = validateFile(file);
    if (validationError) {
      setLocalError(validationError);
      return;
    }
    setLocalError(null);
    onImageSelect(file);
  }, [onImageSelect]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
    e.target.value = '';
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleRemove = () => {
    onImageSelect(null);
    setPreview(null);
    setLocalError(null);
  };

  if (preview) {
    return (
      <div className="border-2 border-dashed border-agri-green-300 rounded-lg p-4 text-center">
        <div className="flex items-center justify-center">
          <img src={preview} alt="Preview" className="max-h-48 max-w-full rounded object-contain" />
        </div>
        <div className="mt-3 flex gap-3 justify-center">
          <label className="px-4 py-2 bg-agri-green-600 text-white rounded cursor-pointer hover:bg-agri-green-700 transition-colors text-sm">
            Replace
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={handleFileChange}
              className="hidden"
            />
          </label>
          <button
            type="button"
            onClick={handleRemove}
            className="px-4 py-2 bg-earth-200 text-earth-700 rounded hover:bg-earth-300 transition-colors text-sm"
          >
            Remove
          </button>
        </div>
        {localError && <p className="mt-2 text-sm text-red-600">{localError}</p>}
      </div>
    );
  }

  return (
    <div
      className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
        isDragging
          ? 'border-agri-green-500 bg-agri-green-50'
          : 'border-earth-300 hover:border-agri-green-400 hover:bg-agri-green-50'
      }`}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
    >
      <svg
        className="mx-auto h-12 w-12 text-earth-400"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M7 16V8m0 0l-3 3m3-3l3 3m-3-3v8m9-8v8m0 0l-3-3m3 3l3 3"
        />
      </svg>
      <div className="mt-2">
        <label className="cursor-pointer text-agri-green-600 font-medium">
          Upload a leaf image
          <input
            type="file"
            accept="image/jpeg,image/png,image/webp"
            onChange={handleFileChange}
            className="hidden"
          />
        </label>
        <p className="text-xs text-earth-500 mt-1">JPEG, PNG, or WEBP — up to 10 MB</p>
      </div>
      {localError && <p className="mt-2 text-sm text-red-600">{localError}</p>}
    </div>
  );
}
