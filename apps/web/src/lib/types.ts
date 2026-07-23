/** Types mirroring the FastForge API response schemas. */

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  avatar_url: string | null;
  is_active: boolean;
  is_verified: boolean;
  last_login_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface MessageResponse {
  detail: string;
}

export interface Subscription {
  status: string | null;
  price_id: string | null;
  current_period_end: string | null;
  cancel_at_period_end: boolean;
  is_active: boolean;
}

export interface CheckoutSession {
  url: string;
}

export interface PortalSession {
  url: string;
}

// --- Admin panel ---

export interface AdminUserItem {
  id: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_verified: boolean;
  last_login_at: string | null;
  created_at: string;
}

export interface AdminUserList {
  items: AdminUserItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface AdminSubscriptionInfo {
  status: string | null;
  price_id: string | null;
  current_period_end: string | null;
  cancel_at_period_end: boolean;
  stripe_customer_id: string;
  is_active: boolean;
}

export interface AdminUserDetail extends AdminUserItem {
  avatar_url: string | null;
  updated_at: string;
  subscription: AdminSubscriptionInfo | null;
}

export interface AdminStats {
  total_users: number;
  total_subscriptions: number;
  active_subscriptions: number;
}
