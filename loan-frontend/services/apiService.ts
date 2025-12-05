const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api';

export interface CreateApplicantResponse {
  id: string;
  name: string;
  applicationDate: string;
  riskScore: number;
  summary: string;
  documents: Array<{ name: string; url: string }>;
  fraudChecks?: Array<{
    label: string;
    status: 'pass' | 'fail' | 'warning';
    details?: string;
  }>;
}

export async function createApplicant(
  name: string,
  files: File[]
): Promise<CreateApplicantResponse> {
  const formData = new FormData();
  formData.append('name', name);
  
  files.forEach((file) => {
    formData.append('files', file);
  });

  const response = await fetch(`${API_BASE_URL}/applicants`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
    throw new Error(error.detail || 'Failed to create applicant');
  }

  return response.json();
}

export async function getApplicants(): Promise<CreateApplicantResponse[]> {
  const response = await fetch(`${API_BASE_URL}/applicants`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch applicants');
  }
  
  return response.json();
}
