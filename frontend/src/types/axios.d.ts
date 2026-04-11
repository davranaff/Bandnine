import 'axios';

declare module 'axios' {
  export interface AxiosRequestConfig {
    /**
     * Do not send `Authorization` (e.g. login, register, refresh, public pages).
     * Prevents a stale session token from being sent on auth endpoints.
     */
    skipAuth?: boolean;
    /**
     * Disable automatic refresh-and-retry flow for this request.
     * Use for `/auth/refresh` itself and requests that must fail fast on 401.
     */
    skipRefresh?: boolean;
    /** Internal marker to prevent infinite retry loops after refresh. */
    _retry?: boolean;
  }
}
