import { useCallback, useEffect, useState } from "react";

import {
  createStorageLocation,
  deleteStorageLocation,
  getStorageLocations,
  updateStorageLocation,
} from "../api";
import type {
  CreateStorageLocationPayload,
  StorageLocation,
  StorageLocationStatusFilter,
  StorageLocationTypeFilter,
  UpdateStorageLocationPayload,
} from "../types";

export function useStorageLocations(tenantId: string) {
  const [locations, setLocations] = useState<StorageLocation[]>([]);
  const [status, setStatus] = useState<StorageLocationStatusFilter>("active");
  const [storageType, setStorageType] = useState<StorageLocationTypeFilter>("all");
  const [loadState, setLoadState] = useState<"idle" | "loading" | "ready" | "error">("idle");
  const [errorMessage, setErrorMessage] = useState("");

  const refreshLocations = useCallback(() => {
    if (!tenantId) {
      setLocations([]);
      return;
    }

    setErrorMessage("");
    setLoadState("loading");
    getStorageLocations(tenantId, status, storageType)
      .then((records) => {
        setLocations(records);
        setLoadState("ready");
      })
      .catch(() => {
        setLocations([]);
        setLoadState("error");
        setErrorMessage("Unable to load storage locations.");
      });
  }, [tenantId, status, storageType]);

  useEffect(() => {
    refreshLocations();
  }, [refreshLocations]);

  const createNewLocation = (payload: CreateStorageLocationPayload) => {
    setErrorMessage("");
    return createStorageLocation(tenantId, payload)
      .then(() => refreshLocations())
      .catch((error) => {
        setErrorMessage(readApiError(error));
        throw error;
      });
  };

  const saveLocation = (locationPublicId: string, payload: UpdateStorageLocationPayload) => {
    setErrorMessage("");
    return updateStorageLocation(tenantId, locationPublicId, payload)
      .then(() => refreshLocations())
      .catch((error) => {
        setErrorMessage(readApiError(error));
        throw error;
      });
  };

  const toggleLocationActive = (location: StorageLocation) => {
    const request = location.is_active
      ? deleteStorageLocation(tenantId, location.public_id)
      : updateStorageLocation(tenantId, location.public_id, { is_active: true });

    return request
      .then(() => refreshLocations())
      .catch((error) => {
        setErrorMessage(readApiError(error));
        throw error;
      });
  };

  return {
    createNewLocation,
    errorMessage,
    loadState,
    locations,
    refreshLocations,
    saveLocation,
    setStatus,
    setStorageType,
    status,
    storageType,
    toggleLocationActive,
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
  return "The storage location request could not be completed.";
}
