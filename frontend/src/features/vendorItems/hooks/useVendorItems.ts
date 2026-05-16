import { useCallback, useEffect, useState } from "react";

import { getItemCategories } from "../../itemCategories/api";
import type { ItemCategory } from "../../itemCategories/types";
import { getStorageLocations } from "../../storageLocations/api";
import type { StorageLocation } from "../../storageLocations/types";
import { getVendors } from "../../vendors/api";
import type { Vendor } from "../../vendors/types";
import {
  createVendorItem,
  deleteVendorItem,
  getVendorItems,
  reactivateVendorItem,
  updateVendorItem,
} from "../api";
import type {
  CreateVendorItemPayload,
  UpdateVendorItemPayload,
  VendorItem,
  VendorItemStatusFilter,
} from "../types";

type UseVendorItemsOptions = {
  tenantId: string;
  fixedVendorPublicId?: string;
};

export function useVendorItems({ tenantId, fixedVendorPublicId = "" }: UseVendorItemsOptions) {
  const [items, setItems] = useState<VendorItem[]>([]);
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [categories, setCategories] = useState<ItemCategory[]>([]);
  const [storageLocations, setStorageLocations] = useState<StorageLocation[]>([]);
  const [status, setStatus] = useState<VendorItemStatusFilter>("active");
  const [vendorPublicId, setVendorPublicId] = useState("");
  const [canonicalName, setCanonicalName] = useState("");
  const [categoryPublicId, setCategoryPublicId] = useState("");
  const [storageLocationPublicId, setStorageLocationPublicId] = useState("");
  const [loadState, setLoadState] = useState<"idle" | "loading" | "ready" | "error">("idle");
  const [errorMessage, setErrorMessage] = useState("");

  const effectiveVendorPublicId = fixedVendorPublicId || vendorPublicId;

  const refreshOptions = useCallback(() => {
    if (!tenantId) {
      setVendors([]);
      setCategories([]);
      setStorageLocations([]);
      return;
    }

    Promise.all([
      getVendors(tenantId, "all"),
      getItemCategories(tenantId, "active"),
      getStorageLocations(tenantId, "active", "all"),
    ])
      .then(([vendorRecords, categoryRecords, storageRecords]) => {
        setVendors(vendorRecords);
        setCategories(categoryRecords);
        setStorageLocations(storageRecords);
      })
      .catch(() => {
        setErrorMessage("Unable to load vendor item choices.");
      });
  }, [tenantId]);

  const refreshItems = useCallback(() => {
    if (!tenantId) {
      setItems([]);
      return;
    }

    setItems([]);
    setErrorMessage("");
    setLoadState("loading");
    getVendorItems(tenantId, {
      status,
      vendor_public_id: effectiveVendorPublicId || undefined,
      canonical_name: canonicalName || undefined,
      category_public_id: categoryPublicId || undefined,
      storage_location_public_id: storageLocationPublicId || undefined,
    })
      .then((records) => {
        setItems(records);
        setLoadState("ready");
      })
      .catch((error) => {
        setItems([]);
        setLoadState("error");
        setErrorMessage(readApiError(error, "Unable to load vendor items."));
      });
  }, [
    canonicalName,
    categoryPublicId,
    effectiveVendorPublicId,
    storageLocationPublicId,
    status,
    tenantId,
  ]);

  useEffect(() => {
    refreshOptions();
  }, [refreshOptions]);

  useEffect(() => {
    refreshItems();
  }, [refreshItems]);

  const createNewItem = (payload: CreateVendorItemPayload) => {
    setErrorMessage("");
    return createVendorItem(tenantId, payload)
      .then((createdItem) => {
        setItems((current) => [createdItem, ...current]);
        return createdItem;
      })
      .catch((error) => {
        setErrorMessage(readApiError(error, "Unable to create vendor item."));
        throw error;
      });
  };

  const saveItem = (vendorItemPublicId: string, payload: UpdateVendorItemPayload) => {
    setErrorMessage("");
    return updateVendorItem(tenantId, vendorItemPublicId, payload)
      .then((updatedItem) => {
        setItems((current) =>
          current
            .map((item) => (item.public_id === updatedItem.public_id ? updatedItem : item))
            .filter((item) => status === "all" || item.is_active === (status === "active")),
        );
        return updatedItem;
      })
      .catch((error) => {
        setErrorMessage(readApiError(error, "Unable to save vendor item."));
        throw error;
      });
  };

  const toggleItemActive = (item: VendorItem) => {
    setErrorMessage("");
    const request = item.is_active
      ? deleteVendorItem(tenantId, item.public_id)
      : reactivateVendorItem(tenantId, item.public_id);

    return request
      .then((updatedItem) => {
        setItems((current) =>
          current
            .map((record) => (record.public_id === updatedItem.public_id ? updatedItem : record))
            .filter((record) => status === "all" || record.is_active === (status === "active")),
        );
        return updatedItem;
      })
      .catch((error) => {
        setErrorMessage(readApiError(error, "Unable to update vendor item status."));
        throw error;
      });
  };

  return {
    canonicalName,
    categories,
    categoryPublicId,
    createNewItem,
    effectiveVendorPublicId,
    errorMessage,
    fixedVendorPublicId,
    items,
    loadState,
    refreshItems,
    saveItem,
    setCanonicalName,
    setCategoryPublicId,
    setStatus,
    setStorageLocationPublicId,
    setVendorPublicId,
    status,
    storageLocationPublicId,
    storageLocations,
    toggleItemActive,
    vendorPublicId,
    vendors,
  };
}

function readApiError(error: unknown, fallback: string) {
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
  return fallback;
}
