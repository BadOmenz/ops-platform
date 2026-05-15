import { useCallback, useEffect, useState } from "react";

import { getOrganizations } from "../../organizations/api";
import type { Organization } from "../../organizations/types";
import { createCustomer, deleteCustomer, getCustomers, updateCustomer } from "../api";
import type { CreateCustomerPayload, Customer, CustomerStatusFilter } from "../types";

export function useCustomers(tenantId: string) {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [status, setStatus] = useState<CustomerStatusFilter>("active");
  const [loadState, setLoadState] = useState<"idle" | "loading" | "ready" | "error">("idle");
  const [errorMessage, setErrorMessage] = useState("");

  const refreshCustomers = useCallback(() => {
    if (!tenantId) {
      setCustomers([]);
      return;
    }
    setCustomers([]);
    setErrorMessage("");
    setLoadState("loading");
    getCustomers(tenantId, status)
      .then((records) => {
        setCustomers(records);
        setLoadState("ready");
      })
      .catch(() => {
        setCustomers([]);
        setLoadState("error");
        setErrorMessage("Unable to load customers.");
      });
  }, [tenantId, status]);

  const refreshOrganizations = useCallback(() => {
    if (!tenantId) {
      setOrganizations([]);
      return;
    }
    setOrganizations([]);
    getOrganizations(tenantId, "active")
      .then(setOrganizations)
      .catch(() => {
        setOrganizations([]);
        setErrorMessage("Unable to load organizations for customer setup.");
      });
  }, [tenantId]);

  useEffect(() => {
    refreshOrganizations();
  }, [refreshOrganizations]);

  useEffect(() => {
    refreshCustomers();
  }, [refreshCustomers]);

  const createNewCustomer = (payload: CreateCustomerPayload) => {
    setErrorMessage("");
    return createCustomer(tenantId, payload)
      .then((customer) => {
        setCustomers((current) => [customer, ...current]);
      })
      .catch((error) => {
        setErrorMessage(readApiError(error));
        throw error;
      });
  };

  const toggleCustomerActive = (customer: Customer) => {
    const request = customer.is_active
      ? deleteCustomer(tenantId, customer.public_id)
      : updateCustomer(tenantId, customer.public_id, { is_active: true });

    return request
      .then((updatedCustomer) => {
        setCustomers((current) =>
          current
            .map((record) => (record.public_id === updatedCustomer.public_id ? updatedCustomer : record))
            .filter((record) => status === "all" || record.is_active === (status === "active")),
        );
      })
      .catch((error) => {
        setErrorMessage(readApiError(error));
        throw error;
      });
  };

  return {
    createNewCustomer,
    customers,
    errorMessage,
    loadState,
    organizations,
    refreshCustomers,
    setStatus,
    status,
    toggleCustomerActive,
  };
}

function readApiError(error: unknown) {
  const detail = getApiErrorDetail(error);
  if (typeof detail === "string") {
    return humanizeCustomerErrorDetail(detail);
  }
  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => {
        if (typeof item !== "object" || item === null) {
          return "";
        }
        const issue = item as { loc?: unknown[]; msg?: unknown };
        const field = issue.loc?.[issue.loc.length - 1];
        const message = typeof issue.msg === "string" ? issue.msg : "Invalid value.";
        return humanizeCustomerValidationMessage(field, message);
      })
      .filter(Boolean);
    if (messages.length > 0) {
      return messages.join(" ");
    }
  }

  return "The customer request could not be completed.";
}

function getApiErrorDetail(error: unknown) {
  if (
    typeof error === "object" &&
    error !== null &&
    "response" in error &&
    typeof error.response === "object" &&
    error.response !== null &&
    "data" in error.response
  ) {
    return (error.response.data as { detail?: unknown }).detail;
  }
  return undefined;
}

function humanizeCustomerErrorDetail(detail: string) {
  const lowerDetail = detail.toLowerCase();
  if (lowerDetail.includes("active customer already exists")) {
    return "An active customer role already exists for this organization.";
  }
  if (lowerDetail.includes("organization is invalid")) {
    return "Customer role must be linked to an organization in this tenant.";
  }
  if (lowerDetail.includes("accounts payable") && lowerDetail.includes("phone")) {
    return "Accounts payable phone must be a valid phone number.";
  }
  if (lowerDetail.includes("accounts payable") && lowerDetail.includes("email")) {
    return "Accounts payable email must be a valid email address.";
  }
  if (lowerDetail.includes("billing") && lowerDetail.includes("phone")) {
    return "Billing phone must be a valid phone number.";
  }
  if (lowerDetail.includes("billing") && lowerDetail.includes("email")) {
    return "Billing email must be a valid email address.";
  }
  return detail;
}

function humanizeCustomerValidationMessage(field: unknown, message: string) {
  const lowerMessage = message.toLowerCase();
  if (field === "billing_email" || (lowerMessage.includes("email") && lowerMessage.includes("billing"))) {
    return "Billing email must be a valid email address.";
  }
  if (field === "accounts_payable_email" || lowerMessage.includes("email")) {
    return "Accounts payable email must be a valid email address.";
  }
  if (field === "billing_phone" || (lowerMessage.includes("phone") && lowerMessage.includes("billing"))) {
    return "Billing phone must be a valid phone number.";
  }
  if (field === "accounts_payable_phone" || lowerMessage.includes("phone")) {
    return "Accounts payable phone must be a valid phone number.";
  }
  if (field === "organization_id") {
    return "Customer role must be linked to an organization in this tenant.";
  }
  if (lowerMessage.includes("string_too_long")) {
    return "Value is too long.";
  }
  return message;
}
