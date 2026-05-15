export type StorageLocationStatusFilter = "active" | "inactive" | "all";
export type StorageLocationType = "cooler" | "freezer" | "dry" | "ambient" | "other";
export type StorageLocationTypeFilter = StorageLocationType | "all";

export type StorageLocation = {
  public_id: string;
  tenant_id: string;
  display_name: string;
  normalized_name: string;
  storage_type: StorageLocationType;
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
};

export type CreateStorageLocationPayload = {
  display_name: string;
  storage_type: StorageLocationType;
};

export type UpdateStorageLocationPayload = Partial<CreateStorageLocationPayload> & {
  is_active?: boolean;
};

export type StorageLocationListResponse = {
  data: StorageLocation[];
};
