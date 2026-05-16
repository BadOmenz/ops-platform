export type Weekday =
  | "monday"
  | "tuesday"
  | "wednesday"
  | "thursday"
  | "friday"
  | "saturday"
  | "sunday";

export type VendorDeliveryRuleStatusFilter = "active" | "inactive" | "all";

export type VendorDeliveryRule = {
  public_id: string;
  tenant_id: string;
  vendor_public_id: string;
  vendor_display_name: string;
  delivery_weekday: Weekday;
  order_cutoff_weekday: Weekday;
  order_cutoff_time: string;
  lead_time_days: number | null;
  minimum_order_value: string | null;
  delivery_window_start: string | null;
  delivery_window_end: string | null;
  notes: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
};

export type CreateVendorDeliveryRulePayload = {
  delivery_weekday: Weekday;
  order_cutoff_weekday: Weekday;
  order_cutoff_time: string;
  lead_time_days?: number | null;
  minimum_order_value?: string | null;
  delivery_window_start?: string | null;
  delivery_window_end?: string | null;
  notes?: string | null;
};

export type UpdateVendorDeliveryRulePayload = Partial<CreateVendorDeliveryRulePayload> & {
  is_active?: boolean;
};

export type VendorDeliveryRuleListResponse = {
  data: VendorDeliveryRule[];
};
