export type VendorStatusFilter = "active" | "inactive" | "all";

export type Vendor = {
  id: string;
  public_id: string;
  tenant_id: string;
  organization_id: string;
  organization_display_name: string;
  vendor_code: string | null;
  account_number: string | null;
  ordering_email: string | null;
  ordering_phone: string | null;
  website: string | null;
  notes: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
};

export type CreateVendorPayload = {
  organization_id: string;
  vendor_code?: string | null;
  account_number?: string | null;
  ordering_email?: string | null;
  ordering_phone?: string | null;
  website?: string | null;
  notes?: string | null;
};

export type UpdateVendorPayload = Partial<Omit<CreateVendorPayload, "organization_id">> & {
  is_active?: boolean;
};

export type VendorListResponse = {
  data: Vendor[];
};
