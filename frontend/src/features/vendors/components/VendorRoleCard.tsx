import { useEffect, useMemo, useState } from "react";

import { createCustomer, deleteCustomer, getCustomers, updateCustomer } from "../../customers/api";
import type { Customer } from "../../customers/types";
import { createVendor, deleteVendor, getVendors, updateVendor } from "../api";
import type { Vendor } from "../types";

type VendorRoleCardProps = {
  tenantId: string;
  organizationId: string;
  organizationWebsite: string | null;
  onOpenCustomer: (customerPublicId: string) => void;
  onOpenVendor: (vendorPublicId: string) => void;
};

type RoleStatusFilter = "active" | "inactive" | "all";

export function VendorRoleCard({
  tenantId,
  organizationId,
  organizationWebsite,
  onOpenCustomer,
  onOpenVendor,
}: VendorRoleCardProps) {
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
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
  const activeCustomer = useMemo(
    () =>
      customers.find((record) => record.organization_id === organizationId && record.is_active) ||
      null,
    [customers, organizationId],
  );
  const inactiveCustomer = useMemo(
    () =>
      customers.find((record) => record.organization_id === organizationId && !record.is_active) ||
      null,
    [customers, organizationId],
  );
  const visibleRoles = useMemo(() => {
    if (roleStatusFilter === "active") {
      return [
        activeVendor ? buildVendorRole(activeVendor) : null,
        activeCustomer ? buildCustomerRole(activeCustomer) : null,
      ].filter((record): record is VisibleRole => record !== null);
    }
    if (roleStatusFilter === "inactive") {
      return [
        inactiveVendor ? buildVendorRole(inactiveVendor) : null,
        inactiveCustomer ? buildCustomerRole(inactiveCustomer) : null,
      ].filter((record): record is VisibleRole => record !== null);
    }
    return [
      activeVendor ? buildVendorRole(activeVendor) : null,
      inactiveVendor ? buildVendorRole(inactiveVendor) : null,
      activeCustomer ? buildCustomerRole(activeCustomer) : null,
      inactiveCustomer ? buildCustomerRole(inactiveCustomer) : null,
    ].filter((record): record is VisibleRole => record !== null);
  }, [activeCustomer, activeVendor, inactiveCustomer, inactiveVendor, roleStatusFilter]);
  const canAssignRole =
    roleStatusFilter === "active" && (activeVendor === null || activeCustomer === null);
  const addRoleButtonText = getAddRoleButtonText(selectedRole, inactiveVendor, inactiveCustomer);

  useEffect(() => {
    let isMounted = true;

    setLoadState("loading");
    Promise.all([getVendors(tenantId, "all"), getCustomers(tenantId, "all")])
      .then(([vendorRecords, customerRecords]) => {
        if (!isMounted) {
          return;
        }
        setVendors(vendorRecords);
        setCustomers(customerRecords);
        setLoadState("ready");
      })
      .catch(() => {
        if (isMounted) {
          setLoadState("error");
          setErrorMessage("Unable to load organization roles.");
        }
      });

    return () => {
      isMounted = false;
    };
  }, [tenantId, organizationId]);

  const handleAddRole = () => {
    if (selectedRole === "") {
      return;
    }

    setErrorMessage("");

    if (selectedRole === "vendor" && inactiveVendor) {
      updateVendor(tenantId, inactiveVendor.public_id, { is_active: true })
        .then((updatedVendor) => {
          setVendors((current) =>
            current.map((record) =>
              record.public_id === updatedVendor.public_id ? updatedVendor : record,
            ),
          );
          setSelectedRole("");
          setRoleStatusFilter("active");
          onOpenVendor(updatedVendor.public_id);
        })
        .catch((error) => setErrorMessage(readApiError(error)));
      return;
    }

    if (selectedRole === "customer" && inactiveCustomer) {
      updateCustomer(tenantId, inactiveCustomer.public_id, { is_active: true })
        .then((updatedCustomer) => {
          setCustomers((current) =>
            current.map((record) =>
              record.public_id === updatedCustomer.public_id ? updatedCustomer : record,
            ),
          );
          setSelectedRole("");
          setRoleStatusFilter("active");
          onOpenCustomer(updatedCustomer.public_id);
        })
        .catch((error) => setErrorMessage(readApiError(error)));
      return;
    }

    const request =
      selectedRole === "vendor"
        ? createVendor(tenantId, {
            organization_id: organizationId,
            website: organizationWebsite || null,
          })
        : createCustomer(tenantId, {
            organization_id: organizationId,
          });

    request
      .then((createdRole) => {
        if (selectedRole === "vendor") {
          const createdVendor = createdRole as Vendor;
          setVendors((current) => [createdVendor, ...current]);
          onOpenVendor(createdVendor.public_id);
        } else {
          const createdCustomer = createdRole as Customer;
          setCustomers((current) => [createdCustomer, ...current]);
          onOpenCustomer(createdCustomer.public_id);
        }
        setSelectedRole("");
        setRoleStatusFilter("active");
      })
      .catch((error) => setErrorMessage(readApiError(error)));
  };

  const handleToggleActive = (role: VisibleRole) => {
    setErrorMessage("");
    const request =
      role.kind === "vendor"
        ? role.record.is_active
          ? deleteVendor(tenantId, role.record.public_id)
          : updateVendor(tenantId, role.record.public_id, { is_active: true })
        : role.record.is_active
          ? deleteCustomer(tenantId, role.record.public_id)
          : updateCustomer(tenantId, role.record.public_id, { is_active: true });

    request
      .then((updatedRole) => {
        if (role.kind === "vendor") {
          const updatedVendor = updatedRole as Vendor;
          setVendors((current) =>
            current.map((record) =>
              record.public_id === updatedVendor.public_id ? updatedVendor : record,
            ),
          );
        } else {
          const updatedCustomer = updatedRole as Customer;
          setCustomers((current) =>
            current.map((record) =>
              record.public_id === updatedCustomer.public_id ? updatedCustomer : record,
            ),
          );
        }
        if (updatedRole.is_active) {
          setRoleStatusFilter("active");
        }
      })
      .catch((error) => setErrorMessage(readApiError(error)));
  };

  return (
    <section className="vendor-role-card" aria-label="Organization role">
      <div className="role-section-header">
        <div>
          <p className="eyebrow">Roles</p>
          <h3>Organization roles</h3>
        </div>
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
      </div>

      {errorMessage && <div className="error-banner">{errorMessage}</div>}

      {canAssignRole && (
        <div className="role-selector">
          <label className="field role-add-field">
            <span>Select role to add or open</span>
            <select
              value={selectedRole}
              onChange={(event) => setSelectedRole(event.target.value as "" | "vendor" | "customer")}
            >
              <option value="">Choose role</option>
              <option value="vendor" disabled={activeVendor !== null}>
                Vendor
              </option>
              <option value="customer" disabled={activeCustomer !== null}>
                Customer
              </option>
            </select>
          </label>
          <button
            type="button"
            onClick={handleAddRole}
            disabled={loadState === "loading" || selectedRole === ""}
          >
            {addRoleButtonText}
          </button>
        </div>
      )}

      {visibleRoles.length > 0 ? (
        <div className="role-card-grid">
          {visibleRoles.map((role) => (
            <RoleCard
              key={`${role.kind}-${role.record.public_id}`}
              role={role}
              onOpen={() =>
                role.kind === "vendor"
                  ? onOpenVendor(role.record.public_id)
                  : onOpenCustomer(role.record.public_id)
              }
              onToggleActive={() => handleToggleActive(role)}
            />
          ))}
        </div>
      ) : (
        <div className="role-empty-state">{getEmptyRoleMessage(roleStatusFilter)}</div>
      )}
    </section>
  );
}

type VisibleRole =
  | {
      kind: "vendor";
      label: "Vendor";
      description: "Purchasing, ordering, and supplier-side workflows.";
      record: Vendor;
    }
  | {
      kind: "customer";
      label: "Customer";
      description: "Billing, accounts payable, and customer-side workflows.";
      record: Customer;
    };

function buildVendorRole(record: Vendor): VisibleRole {
  return {
    kind: "vendor",
    label: "Vendor",
    description: "Purchasing, ordering, and supplier-side workflows.",
    record,
  };
}

function buildCustomerRole(record: Customer): VisibleRole {
  return {
    kind: "customer",
    label: "Customer",
    description: "Billing, accounts payable, and customer-side workflows.",
    record,
  };
}

function getEmptyRoleMessage(roleStatusFilter: RoleStatusFilter) {
  if (roleStatusFilter === "inactive") {
    return "No inactive roles";
  }
  if (roleStatusFilter === "all") {
    return "No roles yet";
  }
  return "No active roles";
}

function getAddRoleButtonText(
  selectedRole: "" | "vendor" | "customer",
  inactiveVendor: Vendor | null,
  inactiveCustomer: Customer | null,
) {
  if (selectedRole === "vendor" && inactiveVendor) {
    return "Reactivate Vendor role";
  }
  if (selectedRole === "customer" && inactiveCustomer) {
    return "Reactivate Customer role";
  }
  return "Add role";
}

function RoleCard({
  role,
  onOpen,
  onToggleActive,
}: {
  role: VisibleRole;
  onOpen: () => void;
  onToggleActive: () => void;
}) {
  const isActive = role.record.is_active;
  const toggleLabel = isActive
    ? `Deactivate ${role.label} role`
    : `Reactivate ${role.label} role`;

  return (
    <article className="organization-role-card">
      <div className="role-card-heading">
        <div>
          <p className="eyebrow">Role</p>
          <h4>{role.label}</h4>
        </div>
        <span className={`status-label ${isActive ? "is-success" : ""}`}>
          {isActive ? "Active" : "Inactive"}
        </span>
      </div>
      <p className="muted">{role.description}</p>
      <div className="role-card-actions">
        {isActive ? (
          <>
            <button type="button" onClick={onOpen}>
              Open {role.label}
            </button>
            <button className="secondary-button" type="button" onClick={onToggleActive}>
              {toggleLabel}
            </button>
          </>
        ) : (
          <>
            <button type="button" onClick={onToggleActive}>
              {toggleLabel}
            </button>
            <button className="secondary-button" type="button" onClick={onOpen}>
              Open {role.label}
            </button>
          </>
        )}
      </div>
    </article>
  );
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
  return "The role request could not be completed.";
}
