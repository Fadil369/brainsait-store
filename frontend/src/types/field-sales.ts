/**
 * Field Sales types for TypeScript
 */

export enum SalesRepStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  ON_LEAVE = 'on_leave',
  SUSPENDED = 'suspended',
}

export enum CheckInStatus {
  PENDING = 'pending',
  APPROVED = 'approved',
  REJECTED = 'rejected',
}

export enum CreditStatus {
  PENDING = 'pending',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  EXPIRED = 'expired',
}

export enum BadgeType {
  BRONZE = 'bronze',
  SILVER = 'silver',
  GOLD = 'gold',
  PLATINUM = 'platinum',
}

export interface SalesRep {
  id: string;
  user_id: string;
  tenant_id: string;
  rep_code: string;
  territory?: string;
  status: SalesRepStatus;
  monthly_target: number;
  current_month_sales: number;
  total_sales: number;
  commission_rate: number;
  total_commission: number;
  points: number;
  level: number;
  badges?: string[];
  csat_score?: number;
  total_visits: number;
  successful_visits: number;
  created_at: string;
  updated_at?: string;
  last_active_at?: string;
}

export interface OutletCheckIn {
  id: string;
  sales_rep_id: string;
  outlet_name: string;
  outlet_id?: string;
  latitude: number;
  longitude: number;
  address?: string;
  geofence_verified: boolean;
  distance_from_outlet?: number;
  photo_url?: string;
  check_in_time: string;
  check_out_time?: string;
  duration_minutes?: number;
  status: CheckInStatus;
  visit_notes?: string;
  products_discussed?: string[];
  orders_placed?: string[];
  created_at: string;
}

export interface VoiceOrder {
  id: string;
  sales_rep_id: string;
  language: string;
  audio_duration_seconds?: number;
  raw_transcription?: string;
  processed_text?: string;
  confidence_score?: number;
  extracted_products?: any[];
  extracted_customer?: any;
  order_id?: string;
  processing_status: string;
  error_message?: string;
  created_at: string;
  processed_at?: string;
}

export interface CreditRequest {
  id: string;
  sales_rep_id: string;
  customer_name: string;
  customer_email?: string;
  customer_phone: string;
  customer_business?: string;
  requested_amount: number;
  credit_term_days: number;
  purpose?: string;
  ai_score?: number;
  ai_recommendation?: string;
  risk_factors?: string[];
  status: CreditStatus;
  approved_amount?: number;
  approved_term_days?: number;
  decision_notes?: string;
  decided_at?: string;
  created_at: string;
  updated_at?: string;
  expires_at?: string;
}

export interface LeaderboardEntry {
  rank: number;
  sales_rep_id: string;
  rep_name: string;
  total_sales: number;
  total_orders: number;
  points_earned: number;
  territory?: string;
}

export interface Achievement {
  id: string;
  code: string;
  name: string;
  name_ar: string;
  description?: string;
  description_ar?: string;
  badge_type: BadgeType;
  badge_icon?: string;
  requirement_type: string;
  requirement_value: number;
  points_reward: number;
  is_earned: boolean;
  earned_at?: string;
}

export interface TargetProgress {
  monthly_target: number;
  current_sales: number;
  progress_percentage: number;
  days_remaining: number;
  daily_average_required: number;
}

export interface SalesRepDashboard {
  rep_info: SalesRep;
  target_progress: TargetProgress;
  recent_check_ins: OutletCheckIn[];
  pending_credits: CreditRequest[];
  leaderboard_position: {
    rank: number;
    total_participants: number;
    percentile: number;
  };
  achievements: Achievement[];
  route_summary: {
    total_visits_today: number;
    completed_visits: number;
    in_progress: number;
  };
}

export interface CheckInFormData {
  outlet_name: string;
  outlet_id?: string;
  latitude: number;
  longitude: number;
  address?: string;
  photo_base64?: string;
  visit_notes?: string;
  products_discussed?: string[];
}

export interface VoiceOrderFormData {
  audio_base64: string;
  language: 'ar' | 'en';
  audio_duration_seconds?: number;
}

export interface CreditRequestFormData {
  customer_name: string;
  customer_email?: string;
  customer_phone: string;
  customer_business?: string;
  requested_amount: number;
  credit_term_days: number;
  purpose?: string;
}

export interface OfflineSyncData {
  check_ins?: CheckInFormData[];
  voice_orders?: VoiceOrderFormData[];
  credit_requests?: CreditRequestFormData[];
  last_sync_at?: string;
}

export interface ARProduct {
  id: string;
  name: string;
  name_ar: string;
  description?: string;
  description_ar?: string;
  price: number;
  image_url?: string;
  ar_model_url: string;
  ar_scale: number;
  ar_placement: 'floor' | 'wall';
}
