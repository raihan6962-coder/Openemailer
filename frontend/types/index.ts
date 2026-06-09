export interface User {
  id: string;
  email: string;
  full_name: string;
  first_name?: string;
  last_name?: string;
  avatar_url?: string;
  role: string;
  is_verified: boolean;
  workspace_id?: string;
}

export interface Workspace {
  id: string;
  name: string;
  slug: string;
  plan: string;
  status: string;
  max_users: number;
  max_leads: number;
  max_campaigns: number;
  max_mailboxes: number;
}

export interface EmailAccount {
  id: string;
  workspace_id: string;
  email: string;
  provider: string;
  provider_type: string;
  is_verified: boolean;
  is_active: boolean;
  is_primary: boolean;
  daily_send_limit: number;
  daily_sent_count: number;
  status: string;
  health_score: number;
}

export interface Lead {
  id: string;
  workspace_id: string;
  list_id?: string;
  email: string;
  first_name?: string;
  last_name?: string;
  full_name?: string;
  company?: string;
  website?: string;
  country?: string;
  industry?: string;
  job_title?: string;
  phone?: string;
  tags?: string;
  source: string;
  status: string;
  quality_score: number;
  is_valid: boolean;
  validation_status: string;
}

export interface Campaign {
  id: string;
  workspace_id: string;
  name: string;
  description?: string;
  campaign_type: string;
  status: string;
  daily_limit: number;
  sending_window_start: string;
  sending_window_end: string;
  timezone: string;
  sent_count: number;
  open_count: number;
  click_count: number;
  reply_count: number;
  bounce_count: number;
  spam_count: number;
  started_at?: string;
  completed_at?: string;
}

export interface Template {
  id: string;
  workspace_id: string;
  name: string;
  subject?: string;
  body_html?: string;
  body_text?: string;
  template_type: string;
  category?: string;
  is_ai_generated: boolean;
  version: number;
}

export interface CRMContact {
  id: string;
  workspace_id: string;
  lead_id?: string;
  company_id?: string;
  email: string;
  first_name?: string;
  last_name?: string;
  phone?: string;
  job_title?: string;
  linkedin_url?: string;
  website?: string;
  country?: string;
  status: string;
  lead_score: number;
  lead_status: string;
}

export interface CRMDeal {
  id: string;
  workspace_id: string;
  contact_id?: string;
  pipeline_id: string;
  stage_id: string;
  name: string;
  value: number;
  currency: string;
  probability: number;
  status: string;
  close_date?: string;
}

export interface AnalyticsSummary {
  total_leads: number;
  total_campaigns: number;
  total_sent: number;
  total_opens: number;
  total_clicks: number;
  total_replies: number;
  total_bounces: number;
  open_rate: number;
  click_rate: number;
  reply_rate: number;
  bounce_rate: number;
  deliverability_score: number;
}
