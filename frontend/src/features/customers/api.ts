import { api } from "../../shared/api/client";
import type {
  CreateCustomerPayload,
  Customer,
  CustomerListResponse,
  CustomerStatusFilter,
  UpdateCustomerPayload,
} from "./types";

export async function getCustomers(
  tenantId: string,
  status: CustomerStatusFilter = "active",
): Promise<Customer[]> {
  const response = await api.get<CustomerListResponse>(`/tenants/${tenantId}/customers?status=${status}`);
  return response.data.data;
}

export async function getCustomer(tenantId: string, customerPublicId: string): Promise<Customer> {
  const response = await api.get<Customer>(`/tenants/${tenantId}/customers/${customerPublicId}`);
  return response.data;
}

export async function createCustomer(
  tenantId: string,
  payload: CreateCustomerPayload,
): Promise<Customer> {
  const response = await api.post<Customer>(`/tenants/${tenantId}/customers`, payload);
  return response.data;
}

export async function updateCustomer(
  tenantId: string,
  customerPublicId: string,
  payload: UpdateCustomerPayload,
): Promise<Customer> {
  const response = await api.patch<Customer>(`/tenants/${tenantId}/customers/${customerPublicId}`, payload);
  return response.data;
}

export async function deleteCustomer(tenantId: string, customerPublicId: string): Promise<Customer> {
  const response = await api.delete<Customer>(`/tenants/${tenantId}/customers/${customerPublicId}`);
  return response.data;
}
