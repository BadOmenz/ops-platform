import { api } from "../../shared/api/client";
import type { Tenant, TenantListResponse } from "./types";

export async function getTenants(): Promise<Tenant[]> {
  const response = await api.get<TenantListResponse>("/tenants");
  return response.data.data;
}

export async function createTenant(payload: { name: string; slug?: string }): Promise<Tenant> {
  const response = await api.post<Tenant>("/tenants", payload);
  return response.data;
}

