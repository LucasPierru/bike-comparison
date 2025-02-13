export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;
export const API_KEY = process.env.NEXT_PUBLIC_API_KEY!;

export const api = async (endpoint: string, options: RequestInit) => {
  const opts = {
    ...options,
    headers: { "x-api-key": API_KEY },
  };

  return fetch(`${API_BASE_URL}${endpoint}`, opts);
};
