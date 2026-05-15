import { api } from "../../shared/api/client";
import type {
  CreateItemCategoryPayload,
  ItemCategory,
  ItemCategoryListResponse,
  ItemCategoryStatusFilter,
  UpdateItemCategoryPayload,
} from "./types";

export async function getItemCategories(
  tenantId: string,
  status: ItemCategoryStatusFilter = "active",
): Promise<ItemCategory[]> {
  const response = await api.get<ItemCategoryListResponse>(
    `/tenants/${tenantId}/item-categories?status=${status}`,
  );
  return response.data.data;
}

export async function createItemCategory(
  tenantId: string,
  payload: CreateItemCategoryPayload,
): Promise<ItemCategory> {
  const response = await api.post<ItemCategory>(`/tenants/${tenantId}/item-categories`, payload);
  return response.data;
}

export async function updateItemCategory(
  tenantId: string,
  categoryPublicId: string,
  payload: UpdateItemCategoryPayload,
): Promise<ItemCategory> {
  const response = await api.patch<ItemCategory>(
    `/tenants/${tenantId}/item-categories/${categoryPublicId}`,
    payload,
  );
  return response.data;
}

export async function deleteItemCategory(
  tenantId: string,
  categoryPublicId: string,
): Promise<ItemCategory> {
  const response = await api.delete<ItemCategory>(
    `/tenants/${tenantId}/item-categories/${categoryPublicId}`,
  );
  return response.data;
}
