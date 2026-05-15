export type ItemCategoryStatusFilter = "active" | "inactive" | "all";

export type ItemCategory = {
  public_id: string;
  tenant_id: string;
  parent_id: string | null;
  parent_display_name: string | null;
  display_name: string;
  normalized_name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
};

export type CreateItemCategoryPayload = {
  parent_id?: string | null;
  display_name: string;
};

export type UpdateItemCategoryPayload = Partial<CreateItemCategoryPayload> & {
  is_active?: boolean;
};

export type ItemCategoryListResponse = {
  data: ItemCategory[];
};
