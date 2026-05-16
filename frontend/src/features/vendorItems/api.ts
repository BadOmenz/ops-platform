import { api } from "../../shared/api/client";
import type {
  CreateVendorItemPayload,
  UpdateVendorItemPayload,
  VendorItem,
  VendorItemFilters,
  VendorItemListResponse,
} from "./types";

export async function getVendorItems(
  tenantId: string,
  filters: VendorItemFilters,
): Promise<VendorItem[]> {
  const params = new URLSearchParams({ status: filters.status });
  if (filters.vendor_public_id) {
    params.set("vendor_public_id", filters.vendor_public_id);
  }
  if (filters.canonical_name?.trim()) {
    params.set("canonical_name", filters.canonical_name.trim());
  }
  if (filters.category_public_id) {
    params.set("category_public_id", filters.category_public_id);
  }
  if (filters.storage_location_public_id) {
    params.set("storage_location_public_id", filters.storage_location_public_id);
  }

  const response = await api.get<VendorItemListResponse>(
    `/tenants/${tenantId}/vendor-items?${params.toString()}`,
  );
  return response.data.data;
}

export async function createVendorItem(
  tenantId: string,
  payload: CreateVendorItemPayload,
): Promise<VendorItem> {
  const response = await api.post<VendorItem>(`/tenants/${tenantId}/vendor-items`, payload);
  return response.data;
}

export async function updateVendorItem(
  tenantId: string,
  vendorItemPublicId: string,
  payload: UpdateVendorItemPayload,
): Promise<VendorItem> {
  const response = await api.patch<VendorItem>(
    `/tenants/${tenantId}/vendor-items/${vendorItemPublicId}`,
    payload,
  );
  return response.data;
}

export async function deleteVendorItem(
  tenantId: string,
  vendorItemPublicId: string,
): Promise<VendorItem> {
  const response = await api.delete<VendorItem>(
    `/tenants/${tenantId}/vendor-items/${vendorItemPublicId}`,
  );
  return response.data;
}

export async function reactivateVendorItem(
  tenantId: string,
  vendorItemPublicId: string,
): Promise<VendorItem> {
  const response = await api.post<VendorItem>(
    `/tenants/${tenantId}/vendor-items/${vendorItemPublicId}/reactivate`,
  );
  return response.data;
}
