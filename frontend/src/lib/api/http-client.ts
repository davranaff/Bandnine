import axios, {
  AxiosRequestTransformer,
  AxiosResponseTransformer,
  InternalAxiosRequestConfig,
} from 'axios';
// eslint-disable-next-line import/no-extraneous-dependencies -- humps is a runtime dep; types are dev-only @types/humps
import humps from 'humps';

import { AUTH_USER_KEY, REFRESH_TOKEN_KEY } from 'src/auth/api/storage-keys';
import { HOST_API } from 'src/config-global';
import { API_ENDPOINTS } from 'src/lib/api/endpoints';

// ----------------------------------------------------------------------

const root = String(HOST_API ?? '').replace(/\/$/, '');
const ACCESS_TOKEN_KEY = 'accessToken';

type RefreshResponse = {
  tokens: {
    accessToken: string;
    refreshToken: string;
  };
};

let refreshPromise: Promise<string | null> | null = null;

function asRequestTransformers(
  value: AxiosRequestTransformer | AxiosRequestTransformer[] | undefined
): AxiosRequestTransformer[] {
  if (!value) {
    return [];
  }
  return Array.isArray(value) ? value : [value];
}

function asResponseTransformers(
  value: AxiosResponseTransformer | AxiosResponseTransformer[] | undefined
): AxiosResponseTransformer[] {
  if (!value) {
    return [];
  }
  return Array.isArray(value) ? value : [value];
}

function decamelizeRequestBody(data: unknown): unknown {
  if (data instanceof FormData) {
    return data;
  }
  if (data == null || typeof data === 'string' || typeof data === 'number' || typeof data === 'boolean') {
    return data;
  }
  if (Array.isArray(data)) {
    return data;
  }
  if (typeof data === 'object') {
    return humps.decamelizeKeys(data as Record<string, unknown>);
  }
  return data;
}

function camelizeResponseData(data: unknown): unknown {
  if (data == null || typeof data !== 'object' || Array.isArray(data)) {
    return data;
  }
  return humps.camelizeKeys(data as Record<string, unknown>);
}

function clearStoredSession() {
  if (typeof window === 'undefined') {
    return;
  }

  sessionStorage.removeItem(ACCESS_TOKEN_KEY);
  sessionStorage.removeItem(REFRESH_TOKEN_KEY);
  sessionStorage.removeItem(AUTH_USER_KEY);
}

async function refreshAccessToken(): Promise<string | null> {
  if (typeof window === 'undefined') {
    return null;
  }

  const refreshToken = sessionStorage.getItem(REFRESH_TOKEN_KEY);
  if (!refreshToken) {
    return null;
  }

  const response = await apiClient.request<RefreshResponse>({
    method: 'POST',
    url: API_ENDPOINTS.auth.refresh,
    data: { refreshToken },
    skipAuth: true,
    skipRefresh: true,
  });

  const nextAccess = response.data.tokens.accessToken;
  const nextRefresh = response.data.tokens.refreshToken;

  if (!nextAccess || !nextRefresh) {
    return null;
  }

  sessionStorage.setItem(ACCESS_TOKEN_KEY, nextAccess);
  sessionStorage.setItem(REFRESH_TOKEN_KEY, nextRefresh);

  return nextAccess;
}

async function getRefreshPromise() {
  if (!refreshPromise) {
    refreshPromise = refreshAccessToken()
      .then((token) => {
        if (!token) {
          clearStoredSession();
        }
        return token;
      })
      .catch(() => {
        clearStoredSession();
        return null;
      })
      .finally(() => {
        refreshPromise = null;
      });
  }

  return refreshPromise;
}

/**
 * Axios instance for this app: `HOST_API` origin, snake_case ↔ camelCase for JSON bodies
 * and plain object query params, JWT from `sessionStorage` unless `skipAuth` is set.
 */
export const apiClient = axios.create({
  baseURL: root || undefined,
  headers: {
    'Content-Type': 'application/json',
  },
  transformRequest: [decamelizeRequestBody, ...asRequestTransformers(axios.defaults.transformRequest)],
  transformResponse: [
    ...asResponseTransformers(axios.defaults.transformResponse),
    camelizeResponseData,
  ],
});

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const next: InternalAxiosRequestConfig = { ...config };

  if (next.data instanceof FormData && next.headers) {
    delete (next.headers as Record<string, unknown>)['Content-Type'];
  }

  const { params } = next;
  if (
    params &&
    typeof params === 'object' &&
    !(params instanceof URLSearchParams) &&
    !Array.isArray(params)
  ) {
    next.params = humps.decamelizeKeys(params as Record<string, unknown>);
  }

  if (!next.skipAuth && typeof window !== 'undefined') {
    const token = sessionStorage.getItem(ACCESS_TOKEN_KEY);
    if (token) {
      next.headers = next.headers ?? {};
      (next.headers as Record<string, string>).Authorization = `Bearer ${token}`;
    }
  }

  return next;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error: unknown) => {
    if (axios.isAxiosError(error)) {
      const status = error.response?.status;
      const originalRequest = error.config;

      if (
        status === 401 &&
        originalRequest &&
        !originalRequest.skipAuth &&
        !originalRequest.skipRefresh &&
        !originalRequest._retry
      ) {
        originalRequest._retry = true;

        const nextAccess = await getRefreshPromise();
        if (nextAccess) {
          originalRequest.headers = originalRequest.headers ?? {};
          (originalRequest.headers as Record<string, string>).Authorization = `Bearer ${nextAccess}`;
          return apiClient.request(originalRequest);
        }
      }

      return Promise.reject(error);
    }
    return Promise.reject(error);
  }
);
