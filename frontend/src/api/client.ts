import type { CombinedAnalysisResponse, ApiError } from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export class ApiClientError extends Error {
  public status: number;
  public error_code?: string | null;

  constructor(message: string, status: number, error_code?: string | null) {
    super(message);
    this.name = 'ApiClientError';
    this.status = status;
    this.error_code = error_code;
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (response.ok) {
    return (await response.json()) as T;
  }

  let errorData: ApiError;
  try {
    errorData = (await response.json()) as ApiError;
  } catch {
    errorData = { detail: `Server returned ${response.status}`, status_code: response.status };
  }

  const message = errorData.detail || `Request failed with status ${response.status}`;
  throw new ApiClientError(message, response.status, errorData.error_code);
}

export async function analyzeCrop(
  image: File,
  latitude: number,
  longitude: number,
): Promise<CombinedAnalysisResponse> {
  const formData = new FormData();
  formData.append('image', image);
  formData.append('latitude', String(latitude));
  formData.append('longitude', String(longitude));

  const response = await fetch(`${API_BASE_URL}/api/v1/analyze`, {
    method: 'POST',
    body: formData,
  });

  return handleResponse<CombinedAnalysisResponse>(response);
}

export async function checkHealth(): Promise<{ status: string; service: string; model_loaded: boolean }> {
  const response = await fetch(`${API_BASE_URL}/api/v1/health`);
  return handleResponse<{ status: string; service: string; model_loaded: boolean }>(response);
}
