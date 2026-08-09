export const getAuthToken = () => localStorage.getItem('prompt_sentinel_token');
export const setAuthToken = (token: string) => localStorage.setItem('prompt_sentinel_token', token);
export const removeAuthToken = () => localStorage.removeItem('prompt_sentinel_token');

export const apiClient = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
  const url = typeof input === 'string' ? input : input.toString();
  const options = init || {};
  
  const token = getAuthToken();
  const headers = new Headers(options.headers || {});
  
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(input, {
    ...options,
    headers,
  });

  if (response.status === 401 && !url.includes('/api/v1/auth/')) {
    removeAuthToken();
    window.dispatchEvent(new CustomEvent('unauthorized'));
  }

  return response;
};
