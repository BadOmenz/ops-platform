export type VendorItemStatusFilter = "active" | "inactive" | "all";

export type VendorItem = {
  public_id: string;
  tenant_id: string;
  vendor_public_id: string;
  vendor_display_name: string;
  vendor_item_code: string | null;
  vendor_description: string;
  canonical_name: string;
  normalized_canonical_name: string;
  category_public_id: string | null;
  category_display_name: string | null;
  default_storage_location_public_id: string | null;
  default_storage_location_display_name: string | null;
  purchase_unit: string | null;
  pack_size: string | null;
  pack_unit: string | null;
  case_quantity: string | null;
  case_unit: string | null;
  last_price: string | null;
  last_price_date: string | null;
  estimated_price: string | null;
  price_unit: string | null;
  notes: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
};

export type VendorItemFilters = {
  status: VendorItemStatusFilter;
  vendor_public_id?: string;
  canonical_name?: string;
  category_public_id?: string;
  storage_location_public_id?: string;
};

export type CreateVendorItemPayload = {
  vendor_public_id: string;
  vendor_item_code?: string | null;
  vendor_description: string;
  canonical_name: string;
  category_public_id?: string | null;
  default_storage_location_public_id?: string | null;
  purchase_unit?: string | null;
  pack_size?: string | null;
  pack_unit?: string | null;
  case_quantity?: string | null;
  case_unit?: string | null;
  last_price?: string | null;
  last_price_date?: string | null;
  estimated_price?: string | null;
  price_unit?: string | null;
  notes?: string | null;
};

export type UpdateVendorItemPayload = Partial<CreateVendorItemPayload> & {
  is_active?: boolean;
};

export type VendorItemListResponse = {
  data: VendorItem[];
};
