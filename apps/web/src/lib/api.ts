import { API_URL } from "@/lib/config";
import type {
  AdminStats,
  AdminUserDetail,
  AdminUserItem,
  AdminUserList,
  ApiKey,
  ApiKeyCreated,
  CheckoutSession,
  MessageResponse,
  PortalSession,
  Subscription,
  TokenPair,
  User,
} from "@/lib/types";

const ACCESS_KEY = "ff_access";
const REFRESH_KEY = "ff_refresh";

/** An API call that returned a non-2xx status. `status` is the HTTP code. */
export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

/** Tokens live in localStorage so the SPA survives reloads.
 *  ponytail: localStorage + Bearer matches the API contract (tokens returned in
 *  the body). httpOnly-cookie sessions are the XSS-hardening upgrade — needs the
 *  API to set cookies + CORS credentials, so defer until security review. */
export const tokenStore = {
  get access(): string | null {
    return typeof window === "undefined" ? null : localStorage.getItem(ACCESS_KEY);
  },
  get refresh(): string | null {
    return typeof window === "undefined" ? null : localStorage.getItem(REFRESH_KEY);
  },
  save(pair: TokenPair): void {
    localStorage.setItem(ACCESS_KEY, pair.access_token);
    localStorage.setItem(REFRESH_KEY, pair.refresh_token);
  },
  clear(): void {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
  },
};

/** The platform envelope is `{error: {code, message}}`; FastAPI's own errors
 *  (e.g. from HTTPBearer) use `detail`: a string or validation-error array. */
async function messageFrom(res: Response): Promise<string> {
  try {
    const data = await res.json();
    if (typeof data?.error?.message === "string") return data.error.message;
    const detail = data?.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg;
  } catch {
    /* non-JSON body */
  }
  return `Request failed (${res.status})`;
}

async function tryRefresh(): Promise<boolean> {
  const refresh = tokenStore.refresh;
  if (!refresh) return false;
  try {
    const res = await fetch(`${API_URL}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refresh }),
    });
    if (!res.ok) {
      tokenStore.clear();
      return false;
    }
    tokenStore.save((await res.json()) as TokenPair);
    return true;
  } catch {
    return false;
  }
}

interface RequestOptions {
  method?: string;
  body?: unknown;
  auth?: boolean;
  _retried?: boolean;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, auth = false, _retried = false } = options;

  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (auth && tokenStore.access) {
    headers.Authorization = `Bearer ${tokenStore.access}`;
  }

  const res = await fetch(`${API_URL}${path}`, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  // One transparent refresh + retry on an expired access token.
  if (res.status === 401 && auth && !_retried && (await tryRefresh())) {
    return request<T>(path, { ...options, _retried: true });
  }

  if (!res.ok) {
    throw new ApiError(res.status, await messageFrom(res));
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  register: (payload: { email: string; password: string; full_name?: string }) =>
    request<User>("/auth/register", { method: "POST", body: payload }),

  login: async (payload: { email: string; password: string }) => {
    const pair = await request<TokenPair>("/auth/login", {
      method: "POST",
      body: payload,
    });
    tokenStore.save(pair);
    return pair;
  },

  logout: () => tokenStore.clear(),

  me: () => request<User>("/auth/me", { auth: true }),

  updateProfile: (payload: { full_name: string | null }) =>
    request<User>("/auth/me", { method: "PATCH", body: payload, auth: true }),

  /** Changing the password revokes every outstanding token, so the fresh pair
   *  the API returns must replace the stored one or this tab logs itself out. */
  changePassword: async (payload: {
    current_password?: string;
    new_password: string;
  }) => {
    const pair = await request<TokenPair>("/auth/password", {
      method: "POST",
      body: payload,
      auth: true,
    });
    tokenStore.save(pair);
    return pair;
  },

  deleteAccount: (password?: string) =>
    request<void>("/auth/me", {
      method: "DELETE",
      body: { password: password ?? null },
      auth: true,
    }),

  apiKeys: {
    list: () => request<ApiKey[]>("/api-keys", { auth: true }),

    create: (name: string) =>
      request<ApiKeyCreated>("/api-keys", { method: "POST", body: { name }, auth: true }),

    revoke: (id: string) =>
      request<void>(`/api-keys/${id}`, { method: "DELETE", auth: true }),
  },

  verifyEmail: (token: string) =>
    request<MessageResponse>("/auth/verify-email", {
      method: "POST",
      body: { token },
    }),

  resendVerification: () =>
    request<MessageResponse>("/auth/verify-email/resend", {
      method: "POST",
      auth: true,
    }),

  requestPasswordReset: (email: string) =>
    request<MessageResponse>("/auth/password-reset/request", {
      method: "POST",
      body: { email },
    }),

  confirmPasswordReset: (token: string, new_password: string) =>
    request<MessageResponse>("/auth/password-reset/confirm", {
      method: "POST",
      body: { token, new_password },
    }),

  getSubscription: () => request<Subscription>("/billing/subscription", { auth: true }),

  startCheckout: () =>
    request<CheckoutSession>("/billing/checkout", { method: "POST", auth: true }),

  openPortal: () =>
    request<PortalSession>("/billing/portal", { method: "POST", auth: true }),

  admin: {
    stats: () => request<AdminStats>("/admin/stats", { auth: true }),

    users: ({ page = 1, pageSize = 20, q = "" }: { page?: number; pageSize?: number; q?: string }) => {
      const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
      if (q) params.set("q", q);
      return request<AdminUserList>(`/admin/users?${params.toString()}`, { auth: true });
    },

    user: (id: string) => request<AdminUserDetail>(`/admin/users/${id}`, { auth: true }),

    activate: (id: string) =>
      request<AdminUserItem>(`/admin/users/${id}/activate`, { method: "POST", auth: true }),

    deactivate: (id: string) =>
      request<AdminUserItem>(`/admin/users/${id}/deactivate`, { method: "POST", auth: true }),
  },
};
