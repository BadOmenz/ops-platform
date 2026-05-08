import { useEffect, useMemo, useState } from "react";

import { createVendor, deleteVendor, getVendors, updateVendor } from "../api";
import type { Vendor } from "../types";

type VendorRoleCardProps = {
  tenantId: string;
  organizationId: string;
  organizationWebsite: string | null;
  onOpenVendor: (vendorPublicId: string) => void;
};

type RoleStatusFilter = "active" | "inactive" | "all";

export function VendorRoleCard({
  tenantId,
  organizationId,
  organizationWebsite,
  onOpenVendor,
}: VendorRoleCardProps) {
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [loadState, setLoadState] = useState<"idle" | "loading" | "ready" | "error">("idle");
  const [errorMessage, setErrorMessage] = useState("");
  const [selectedRole, setSelectedRole] = useState<"" | "vendor" | "customer">("");
  const [roleStatusFilter, setRoleStatusFilter] = useState<RoleStatusFilter>("active");

  const activeVendor = useMemo(
    () =>
      vendors.find((record) => record.organization_id === organizationId && record.is_active) ||
      null,
    [organizationId, vendors],
  );
  const inactiveVendor = useMemo(
    () =>
      vendors.find((record) => record.organization_id === organizationId && !record.is_active) ||
      null,
    [organizationId, vendors],
  );
  const visibleVendors = useMemo(() => {
    if (roleStatusFilter === "active") {
      return activeVendor ? [activeVendor] : [];
    }
    if (roleStatusFilter === "inactive") {
      return inactiveVendor ? [inactiveVendor] : [];
    }
    return [activeVendor, inactiveVendor].filter((record): record is Vendor => record !== null);
  }, [activeVendor, inactiveVendor, roleStatusFilter]);
  const vendor = visibleVendors[0] || null;
  const canAssignRole = roleStatusFilter === "active" && activeVendor === null;
  const roleSummary = vendor
    ? `${vendor.is_active ? "Active" : "Inactive"} roles: Vendor`
    : getEmptyRoleMessage(roleStatusFilter);

  useEffect(() => {
    let isMounted = true;

    setLoadState("loading");
    getVendors(tenantId, "all")
      .then((records) => {
        if (!isMounted) {
          return;
        }
        setVendors(records);
        setLoadState("ready");
      })
      .catch(() => {
        if (isMounted) {
          setLoadState("error");
          setErrorMessage("Unable to load vendor role.");
        }
      });

    return () => {
      isMounted = false;
    };
  }, [tenantId, organizationId]);

  const handleCreateAndOpenVendor = () => {
    if (selectedRole !== "vendor") {
      return;
    }

    setErrorMessage("");
    createVendor(tenantId, {
      organization_id: organizationId,
      website: organizationWebsite || null,
    })
      .then((createdVendor) => {
        setVendors((current) => [createdVendor, ...current]);
        setSelectedRole("");
        setRoleStatusFilter("active");
        onOpenVendor(createdVendor.public_id);
      })
      .catch((error) => setErrorMessage(readApiError(error)));
  };

  const handleToggleActive = () => {
    if (!vendor) {
      return;
    }

    setErrorMessage("");
    const request = vendor.is_active
      ? deleteVendor(tenantId, vendor.public_id)
      : updateVendor(tenantId, vendor.public_id, { is_active: true });

    request
      .then((updatedVendor) => {
        setVendors((current) =>
          current.map((record) =>
            record.public_id === updatedVendor.public_id ? updatedVendor : record,
          ),
        );
        if (updatedVendor.is_active) {
          setRoleStatusFilter("active");
        }
      })
      .catch((error) => setErrorMessage(readApiError(error)));
  };

  return (
    <section className="vendor-role-card" aria-label="Organization role">
      <div className="role-section-header">
        <p className="eyebrow">Roles</p>
        <label className="field role-view-field">
          <span>Role view</span>
          <select
            className="role-status-filter"
            value={roleStatusFilter}
            onChange={(event) => setRoleStatusFilter(event.target.value as RoleStatusFilter)}
          >
            <option value="active">Show active roles</option>
            <option value="inactive">Show inactive roles</option>
            <option value="all">Show all roles</option>
          </select>
        </label>
        <div className="role-summary-row">
          <h3>{roleSummary}</h3>
        </div>
      </div>

      {errorMessage && <div className="error-banner">{errorMessage}</div>}

      {canAssignRole && (
        <div className="role-selector">
          <select
            value={selectedRole}
            onChange={(event) => setSelectedRole(event.target.value as "" | "vendor" | "customer")}
          >
            <option value="">Select role</option>
            <option value="vendor">Vendor</option>
            <option value="customer" disabled>
              Customer - coming soon
            </option>
          </select>
          <button
            type="button"
            onClick={handleCreateAndOpenVendor}
            disabled={loadState === "loading" || selectedRole !== "vendor"}
          >
            Create/Open
          </button>
        </div>
      )}

      {vendor && (
        <div className="role-actions">
          {vendor.is_active && (
            <button type="button" onClick={() => onOpenVendor(vendor.public_id)}>
              Open Vendor
            </button>
          )}
          <button
            className={vendor.is_active ? "secondary-button" : undefined}
            type="button"
            onClick={handleToggleActive}
          >
            {vendor.is_active ? "Deactivate this role" : "Reactivate this role"}
          </button>
        </div>
      )}
    </section>
  );
}

function getEmptyRoleMessage(roleStatusFilter: RoleStatusFilter) {
  if (roleStatusFilter === "inactive") {
    return "No inactive role assigned";
  }
  if (roleStatusFilter === "all") {
    return "No role assigned";
  }
  return "No active role assigned";
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
