import { useCallback, useEffect, useState } from "react";

import {
  createItemCategory,
  deleteItemCategory,
  getItemCategories,
  updateItemCategory,
} from "../api";
import type {
  CreateItemCategoryPayload,
  ItemCategory,
  ItemCategoryStatusFilter,
  UpdateItemCategoryPayload,
} from "../types";

export function useItemCategories(tenantId: string) {
  const [categories, setCategories] = useState<ItemCategory[]>([]);
  const [parentOptions, setParentOptions] = useState<ItemCategory[]>([]);
  const [status, setStatus] = useState<ItemCategoryStatusFilter>("active");
  const [loadState, setLoadState] = useState<"idle" | "loading" | "ready" | "error">("idle");
  const [errorMessage, setErrorMessage] = useState("");

  const refreshCategories = useCallback(() => {
    if (!tenantId) {
      setCategories([]);
      setParentOptions([]);
      return;
    }

    setErrorMessage("");
    setLoadState("loading");
    Promise.all([getItemCategories(tenantId, status), getItemCategories(tenantId, "active")])
      .then(([records, activeRecords]) => {
        setCategories(records);
        setParentOptions(activeRecords);
        setLoadState("ready");
      })
      .catch(() => {
        setCategories([]);
        setParentOptions([]);
        setLoadState("error");
        setErrorMessage("Unable to load item categories.");
      });
  }, [tenantId, status]);

  useEffect(() => {
    refreshCategories();
  }, [refreshCategories]);

  const createNewCategory = (payload: CreateItemCategoryPayload) => {
    setErrorMessage("");
    return createItemCategory(tenantId, payload)
      .then(() => refreshCategories())
      .catch((error) => {
        setErrorMessage(readApiError(error));
        throw error;
      });
  };

  const saveCategory = (categoryPublicId: string, payload: UpdateItemCategoryPayload) => {
    setErrorMessage("");
    return updateItemCategory(tenantId, categoryPublicId, payload)
      .then(() => refreshCategories())
      .catch((error) => {
        setErrorMessage(readApiError(error));
        throw error;
      });
  };

  const toggleCategoryActive = (category: ItemCategory) => {
    const request = category.is_active
      ? deleteItemCategory(tenantId, category.public_id)
      : updateItemCategory(tenantId, category.public_id, { is_active: true });

    return request
      .then(() => refreshCategories())
      .catch((error) => {
        setErrorMessage(readApiError(error));
        throw error;
      });
  };

  return {
    categories,
    createNewCategory,
    errorMessage,
    loadState,
    parentOptions,
    refreshCategories,
    saveCategory,
    setStatus,
    status,
    toggleCategoryActive,
  };
}

function readApiError(error: unknown) {
  if (
    typeof error === "object" &&
    error !== null &&
    "response" in error &&
    typeof error.response === "object" &&
    error.response !== null &&
    "data" in error.response
  ) {
    const data = error.response.data as { detail?: unknown };
    if (typeof data.detail === "string") {
      return data.detail;
    }
  }
  return "The item category request could not be completed.";
}
