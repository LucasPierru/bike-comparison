export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

export const api = async (endpoint: string, options = {}) => {
  return fetch(`${API_BASE_URL}${endpoint}`, options);
};
