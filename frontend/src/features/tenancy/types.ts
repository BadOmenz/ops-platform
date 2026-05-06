export type Tenant = {
  id: string;
  name: string;
  slug: string;
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
};

export type TenantListResponse = {
  data: Tenant[];
};

