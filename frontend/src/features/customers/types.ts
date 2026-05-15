export type CustomerStatusFilter = "active" | "inactive" | "all";

export type Customer = {
  id: string;
  public_id: string;
  tenant_id: string;
  organization_id: string;
  organization_display_name: string;
  customer_code: string | null;
  billing_email: string | null;
  billing_phone: string | null;
  accounts_payable_email: string | null;
  accounts_payable_phone: string | null;
  primary_contact_name: string | null;
  notes: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
};

export type CreateCustomerPayload = {
  organization_id: string;
  customer_code?: string | null;
  billing_email?: string | null;
  billing_phone?: string | null;
  accounts_payable_email?: string | null;
  accounts_payable_phone?: string | null;
  primary_contact_name?: string | null;
  notes?: string | null;
};

export type UpdateCustomerPayload = Partial<Omit<CreateCustomerPayload, "organization_id">> & {
  is_active?: boolean;
};

export type CustomerListResponse = {
  data: Customer[];
};
