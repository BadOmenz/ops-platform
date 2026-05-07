import { api } from "../../shared/api/client";
import type {
  CreateVendorPayload,
  UpdateVendorPayload,
  Vendor,
  VendorListResponse,
  VendorStatusFilter,
} from "./types";

export async function getVendors(
  tenantId: string,
  status: VendorStatusFilter = "active",
): Promise<Vendor[]> {
  const response = await api.get<VendorListResponse>(`/tenants/${tenantId}/vendors?status=${status}`);
  return response.data.data;
}

export async function getVendor(tenantId: string, vendorPublicId: string): Promise<Vendor> {
  const response = await api.get<Vendor>(`/tenants/${tenantId}/vendors/${vendorPublicId}`);
  return response.data;
}

export async function createVendor(
  tenantId: string,
  payload: CreateVendorPayload,
): Promise<Vendor> {
  const response = await api.post<Vendor>(`/tenants/${tenantId}/vendors`, payload);
  return response.data;
}

export async function updateVendor(
  tenantId: string,
  vendorPublicId: string,
  payload: UpdateVendorPayload,
): Promise<Vendor> {
  const response = await api.patch<Vendor>(`/tenants/${tenantId}/vendors/${vendorPublicId}`, payload);
  return response.data;
}

export async function deleteVendor(tenantId: string, vendorPublicId: string): Promise<Vendor> {
  const response = await api.delete<Vendor>(`/tenants/${tenantId}/vendors/${vendorPublicId}`);
  return response.data;
}
