import { useEffect, useState } from "react";

import { getOrganizations } from "../../organizations/api";
import type { Organization } from "../../organizations/types";
import { createVendor, deleteVendor, getVendors, updateVendor } from "../api";
import type { CreateVendorPayload, Vendor, VendorStatusFilter } from "../types";

export function useVendors(tenantId: string) {
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [status, setStatus] = useState<VendorStatusFilter>("active");
  const [loadState, setLoadState] = useState<"idle" | "loading" | "ready" | "error">("idle");
  const [errorMessage, setErrorMessage] = useState("");

  const refreshVendors = () => {
    if (!tenantId) {
      setVendors([]);
      return;
    }
    setLoadState("loading");
    getVendors(tenantId, status)
      .then((records) => {
        setVendors(records);
        setLoadState("ready");
      })
      .catch(() => {
        setLoadState("error");
        setErrorMessage("Unable to load vendors.");
      });
  };

  const refreshOrganizations = () => {
    if (!tenantId) {
      setOrganizations([]);
      return;
    }
    getOrganizations(tenantId, "active")
      .then(setOrganizations)
      .catch(() => setErrorMessage("Unable to load organizations for vendor setup."));
  };

  useEffect(() => {
    refreshOrganizations();
  }, [tenantId]);

  useEffect(() => {
    refreshVendors();
  }, [tenantId, status]);

  const createNewVendor = (payload: CreateVendorPayload) => {
    setErrorMessage("");
    return createVendor(tenantId, payload)
      .then((vendor) => {
        setVendors((current) => [vendor, ...current]);
      })
      .catch((error) => {
        setErrorMessage(readApiError(error));
        throw error;
      });
  };

  const toggleVendorActive = (vendor: Vendor) => {
    const request = vendor.is_active
      ? deleteVendor(tenantId, vendor.public_id)
      : updateVendor(tenantId, vendor.public_id, { is_active: true });

    return request
      .then((updatedVendor) => {
        setVendors((current) =>
          current
            .map((record) => (record.public_id === updatedVendor.public_id ? updatedVendor : record))
            .filter((record) => status === "all" || record.is_active === (status === "active")),
        );
      })
      .catch((error) => {
        setErrorMessage(readApiError(error));
        throw error;
      });
  };

  return {
    createNewVendor,
    errorMessage,
    loadState,
    organizations,
    refreshVendors,
    setStatus,
    status,
    toggleVendorActive,
    vendors,
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
  return "The vendor request could not be completed.";
}
