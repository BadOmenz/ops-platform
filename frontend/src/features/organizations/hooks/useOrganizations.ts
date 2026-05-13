import { useCallback, useEffect, useMemo, useState } from "react";

import {
  createOrganization,
  deleteOrganization,
  getOrganizations,
  getOrganizationTypes,
  updateOrganization,
} from "../api";
import type {
  CreateOrganizationPayload,
  Organization,
  OrganizationStatusFilter,
  OrganizationType,
  UpdateOrganizationPayload,
} from "../types";

export type OrganizationSortField = "display_name" | "type" | "contact" | "notes" | "active";
export type OrganizationSortDirection = "asc" | "desc";

export function useOrganizations(tenantId: string) {
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [organizationTypes, setOrganizationTypes] = useState<OrganizationType[]>([]);
  const [status, setStatus] = useState<OrganizationStatusFilter>("active");
  const [selectedOrganizationId, setSelectedOrganizationId] = useState("");
  const [loadState, setLoadState] = useState<"idle" | "loading" | "ready" | "error">("idle");
  const [errorMessage, setErrorMessage] = useState("");
  const [displayNameFilter, setDisplayNameFilter] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const [contactFilter, setContactFilter] = useState("");
  const [notesFilter, setNotesFilter] = useState("");
  const [sortField, setSortField] = useState<OrganizationSortField>("display_name");
  const [sortDirection, setSortDirection] = useState<OrganizationSortDirection>("asc");

  const selectedOrganization =
    organizations.find((organization) => organization.id === selectedOrganizationId) || null;

  const refreshOrganizations = useCallback(() => {
    if (!tenantId) {
      setOrganizations([]);
      setSelectedOrganizationId("");
      return;
    }
    setOrganizations([]);
    setSelectedOrganizationId("");
    setErrorMessage("");
    setLoadState("loading");
    getOrganizations(tenantId, status)
      .then((records) => {
        setOrganizations(records);
        setSelectedOrganizationId((currentId) =>
          records.some((organization) => organization.id === currentId) ? currentId : records[0]?.id || "",
        );
        setLoadState("ready");
      })
      .catch(() => {
        setOrganizations([]);
        setSelectedOrganizationId("");
        setLoadState("error");
        setErrorMessage("Unable to load organizations.");
      });
  }, [tenantId, status]);

  useEffect(() => {
    getOrganizationTypes()
      .then((types) => setOrganizationTypes(types))
      .catch(() => setErrorMessage("Unable to load organization lookup data."));
  }, []);

  useEffect(() => {
    refreshOrganizations();
  }, [refreshOrganizations]);

  const visibleOrganizations = useMemo(() => {
    const matches = (value: string, filter: string) =>
      value.toLowerCase().includes(filter.trim().toLowerCase());

    return organizations
      .filter((organization) => {
        const typeText = organization.organization_types.map((type) => type.name).join(" ");
        const contactText = [
          organization.legal_name || "",
          organization.main_phone || "",
          organization.main_email || "",
          organization.website || "",
        ].join(" ");
        const notesText = organization.notes || "";

        return (
          matches(organization.display_name, displayNameFilter) &&
          matches(typeText, typeFilter) &&
          matches(contactText, contactFilter) &&
          matches(notesText, notesFilter)
        );
      })
      .sort((first, second) => {
        const firstValue = getSortValue(first, sortField);
        const secondValue = getSortValue(second, sortField);
        const comparison = firstValue.localeCompare(secondValue);
        return sortDirection === "asc" ? comparison : comparison * -1;
      });
  }, [
    organizations,
    displayNameFilter,
    typeFilter,
    contactFilter,
    notesFilter,
    sortField,
    sortDirection,
  ]);

  const createNewOrganization = (payload: CreateOrganizationPayload) => {
    setErrorMessage("");
    return createOrganization(tenantId, payload)
      .then((organization) => {
        setOrganizations((current) => [organization, ...current]);
        setSelectedOrganizationId(organization.id);
      })
      .catch((error) => {
        setErrorMessage(readApiError(error));
        throw error;
      });
  };

  const saveOrganization = (organizationId: string, payload: UpdateOrganizationPayload) => {
    setErrorMessage("");
    return updateOrganization(tenantId, organizationId, payload)
      .then((updatedOrganization) => {
        setOrganizations((current) =>
          current.map((organization) =>
            organization.id === updatedOrganization.id ? updatedOrganization : organization,
          ),
        );
        setSelectedOrganizationId(updatedOrganization.id);
      })
      .catch((error) => {
        setErrorMessage(readApiError(error));
        throw error;
      });
  };

  const toggleOrganizationActive = (organization: Organization) => {
    const request = organization.is_active
      ? deleteOrganization(tenantId, organization.id)
      : updateOrganization(tenantId, organization.id, { is_active: true });

    return request.then((updatedOrganization) => {
      setOrganizations((current) =>
        current
          .map((record) => (record.id === updatedOrganization.id ? updatedOrganization : record))
          .filter((record) => status === "all" || record.is_active === (status === "active")),
      );
      setSelectedOrganizationId(updatedOrganization.id);
    });
  };

  const handleSort = (field: OrganizationSortField) => {
    if (field === sortField) {
      setSortDirection((current) => (current === "asc" ? "desc" : "asc"));
      return;
    }
    setSortField(field);
    setSortDirection("asc");
  };

  const clearFilters = () => {
    setDisplayNameFilter("");
    setTypeFilter("");
    setContactFilter("");
    setNotesFilter("");
  };

  return {
    clearFilters,
    contactFilter,
    createNewOrganization,
    displayNameFilter,
    errorMessage,
    handleSort,
    loadState,
    notesFilter,
    organizationTypes,
    refreshOrganizations,
    saveOrganization,
    selectedOrganization,
    selectedOrganizationId,
    setContactFilter,
    setDisplayNameFilter,
    setNotesFilter,
    setSelectedOrganizationId,
    setStatus,
    setTypeFilter,
    sortDirection,
    sortField,
    status,
    toggleOrganizationActive,
    typeFilter,
    visibleOrganizations,
  };
}

function getSortValue(organization: Organization, field: OrganizationSortField) {
  if (field === "type") {
    return organization.organization_types.map((type) => type.name).join(" ");
  }
  if (field === "contact") {
    return [organization.main_phone || "", organization.main_email || "", organization.website || ""].join(" ");
  }
  if (field === "notes") {
    return organization.notes || "";
  }
  if (field === "active") {
    return organization.is_active ? "1" : "0";
  }
  return organization.display_name;
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
  return "The organization request could not be completed.";
}
