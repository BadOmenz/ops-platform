import { api } from "../../shared/api/client";
import type {
  CreateStorageLocationPayload,
  StorageLocation,
  StorageLocationListResponse,
  StorageLocationStatusFilter,
  StorageLocationTypeFilter,
  UpdateStorageLocationPayload,
} from "./types";

export async function getStorageLocations(
  tenantId: string,
  status: StorageLocationStatusFilter = "active",
  storageType: StorageLocationTypeFilter = "all",
): Promise<StorageLocation[]> {
  const params = new URLSearchParams({ status });
  if (storageType !== "all") {
    params.set("storage_type", storageType);
  }
  const response = await api.get<StorageLocationListResponse>(
    `/tenants/${tenantId}/storage-locations?${params.toString()}`,
  );
  return response.data.data;
}

export async function createStorageLocation(
  tenantId: string,
  payload: CreateStorageLocationPayload,
): Promise<StorageLocation> {
  const response = await api.post<StorageLocation>(`/tenants/${tenantId}/storage-locations`, payload);
  return response.data;
}

export async function updateStorageLocation(
  tenantId: string,
  locationPublicId: string,
  payload: UpdateStorageLocationPayload,
): Promise<StorageLocation> {
  const response = await api.patch<StorageLocation>(
    `/tenants/${tenantId}/storage-locations/${locationPublicId}`,
    payload,
  );
  return response.data;
}

export async function deleteStorageLocation(
  tenantId: string,
  locationPublicId: string,
): Promise<StorageLocation> {
  const response = await api.delete<StorageLocation>(
    `/tenants/${tenantId}/storage-locations/${locationPublicId}`,
  );
  return response.data;
}
