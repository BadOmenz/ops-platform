import { api } from "../../shared/api/client";
import type {
  CreateVendorDeliveryRulePayload,
  UpdateVendorDeliveryRulePayload,
  VendorDeliveryRule,
  VendorDeliveryRuleListResponse,
  VendorDeliveryRuleStatusFilter,
} from "./types";

export async function getVendorDeliveryRules(
  tenantId: string,
  vendorPublicId: string,
  status: VendorDeliveryRuleStatusFilter,
): Promise<VendorDeliveryRule[]> {
  if (!tenantId || !vendorPublicId) {
    return [];
  }

  const response = await api.get<VendorDeliveryRuleListResponse>(
    `/tenants/${tenantId}/vendors/${vendorPublicId}/delivery-rules?status=${status}`,
  );
  return Array.isArray(response.data?.data) ? response.data.data : [];
}

export async function createVendorDeliveryRule(
  tenantId: string,
  vendorPublicId: string,
  payload: CreateVendorDeliveryRulePayload,
): Promise<VendorDeliveryRule> {
  const response = await api.post<VendorDeliveryRule>(
    `/tenants/${tenantId}/vendors/${vendorPublicId}/delivery-rules`,
    payload,
  );
  return response.data;
}

export async function updateVendorDeliveryRule(
  tenantId: string,
  deliveryRulePublicId: string,
  payload: UpdateVendorDeliveryRulePayload,
): Promise<VendorDeliveryRule> {
  const response = await api.patch<VendorDeliveryRule>(
    `/tenants/${tenantId}/vendor-delivery-rules/${deliveryRulePublicId}`,
    payload,
  );
  return response.data;
}

export async function deleteVendorDeliveryRule(
  tenantId: string,
  deliveryRulePublicId: string,
): Promise<VendorDeliveryRule> {
  const response = await api.delete<VendorDeliveryRule>(
    `/tenants/${tenantId}/vendor-delivery-rules/${deliveryRulePublicId}`,
  );
  return response.data;
}

export async function reactivateVendorDeliveryRule(
  tenantId: string,
  deliveryRulePublicId: string,
): Promise<VendorDeliveryRule> {
  const response = await api.post<VendorDeliveryRule>(
    `/tenants/${tenantId}/vendor-delivery-rules/${deliveryRulePublicId}/reactivate`,
  );
  return response.data;
}
