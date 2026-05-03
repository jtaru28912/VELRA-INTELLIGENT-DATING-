const BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:10000';

export async function apiFetch(endpoint: string, options: RequestInit = {}) {
  const token = localStorage.getItem('velra_token');
  
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    localStorage.removeItem('velra_token');
    window.location.href = '/auth';
    throw new Error('Unauthorized');
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
    const detail = typeof errorData.detail === 'string' 
      ? errorData.detail 
      : Array.isArray(errorData.detail)
        ? errorData.detail.map((e: any) => e.msg).join(', ')
        : JSON.stringify(errorData.detail);
    throw new Error(detail || `Request failed with status ${response.status}`);
  }

  return response.json();
}
