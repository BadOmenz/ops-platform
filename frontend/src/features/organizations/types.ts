export type OrganizationStatusFilter = "active" | "inactive" | "all";

export type OrganizationType = {
  id: string;
  name: string;
  description: string | null;
  is_active: boolean;
};

export type Organization = {
  id: string;
  tenant_id: string;
  display_name: string;
  legal_name: string | null;
  main_phone: string | null;
  main_email: string | null;
  website: string | null;
  notes: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
  organization_types: OrganizationType[];
};

export type CreateOrganizationPayload = {
  display_name: string;
  legal_name?: string | null;
  main_phone?: string | null;
  main_email?: string | null;
  website?: string | null;
  notes?: string | null;
  organization_type_ids?: string[];
};

export type UpdateOrganizationPayload = Partial<CreateOrganizationPayload> & {
  is_active?: boolean;
};

export type OrganizationListResponse = {
  data: Organization[];
};

export type OrganizationTypeListResponse = {
  data: OrganizationType[];
};
