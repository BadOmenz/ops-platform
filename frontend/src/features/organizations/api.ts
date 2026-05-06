import { api } from "../../shared/api/client";
import type {
  CreateOrganizationPayload,
  Organization,
  OrganizationListResponse,
  OrganizationStatusFilter,
  OrganizationType,
  OrganizationTypeListResponse,
  UpdateOrganizationPayload,
} from "./types";

export async function getOrganizations(
  tenantId: string,
  status: OrganizationStatusFilter = "active",
): Promise<Organization[]> {
  const response = await api.get<OrganizationListResponse>(
    `/tenants/${tenantId}/organizations?status=${status}`,
  );
  return response.data.data;
}

export async function createOrganization(
  tenantId: string,
  payload: CreateOrganizationPayload,
): Promise<Organization> {
  const response = await api.post<Organization>(`/tenants/${tenantId}/organizations`, payload);
  return response.data;
}

export async function updateOrganization(
  tenantId: string,
  organizationId: string,
  payload: UpdateOrganizationPayload,
): Promise<Organization> {
  const response = await api.patch<Organization>(
    `/tenants/${tenantId}/organizations/${organizationId}`,
    payload,
  );
  return response.data;
}

export async function deleteOrganization(
  tenantId: string,
  organizationId: string,
): Promise<Organization> {
  const response = await api.delete<Organization>(
    `/tenants/${tenantId}/organizations/${organizationId}`,
  );
  return response.data;
}

export async function getOrganizationTypes(): Promise<OrganizationType[]> {
  const response = await api.get<OrganizationTypeListResponse>("/organization-types");
  return response.data.data;
}
