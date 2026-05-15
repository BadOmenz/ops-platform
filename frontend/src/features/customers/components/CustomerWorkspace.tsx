import { useEffect, useState } from "react";

import { getCustomer, updateCustomer } from "../api";
import type { Customer } from "../types";

type CustomerWorkspaceProps = {
  tenantId: string;
  customerPublicId: string;
  onBackToOrganization: (organizationId: string) => void;
};

type CustomerSnapshot = {
  customer_code: string | null;
  billing_email: string | null;
  billing_phone: string | null;
  accounts_payable_email: string | null;
  accounts_payable_phone: string | null;
  primary_contact_name: string | null;
  notes: string | null;
};

type CustomerFieldErrors = Partial<Record<keyof CustomerSnapshot, string>>;

export function CustomerWorkspace({
  tenantId,
  customerPublicId,
  onBackToOrganization,
}: CustomerWorkspaceProps) {
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [customerCode, setCustomerCode] = useState("");
  const [billingEmail, setBillingEmail] = useState("");
  const [billingPhone, setBillingPhone] = useState("");
  const [accountsPayableEmail, setAccountsPayableEmail] = useState("");
  const [accountsPayablePhone, setAccountsPayablePhone] = useState("");
  const [primaryContactName, setPrimaryContactName] = useState("");
  const [notes, setNotes] = useState("");
  const [savedSnapshot, setSavedSnapshot] = useState<CustomerSnapshot | null>(null);
  const [fieldErrors, setFieldErrors] = useState<CustomerFieldErrors>({});
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [loadState, setLoadState] = useState<"loading" | "ready" | "error">("loading");

  const applyCustomer = (record: Customer) => {
    setCustomerCode(record.customer_code || "");
    setBillingEmail(record.billing_email || "");
    setBillingPhone(record.billing_phone || "");
    setAccountsPayableEmail(record.accounts_payable_email || "");
    setAccountsPayablePhone(record.accounts_payable_phone || "");
    setPrimaryContactName(record.primary_contact_name || "");
    setNotes(record.notes || "");
    setSavedSnapshot(buildCustomerSnapshot(record));
  };

  useEffect(() => {
    let isMounted = true;

    setLoadState("loading");
    setCustomer(null);
    setSavedSnapshot(null);
    setErrorMessage("");
    setSuccessMessage("");
    getCustomer(tenantId, customerPublicId)
      .then((record) => {
        if (!isMounted) {
          return;
        }
        setCustomer(record);
        applyCustomer(record);
        setLoadState("ready");
      })
      .catch(() => {
        if (isMounted) {
          setCustomer(null);
          setSavedSnapshot(null);
          setLoadState("error");
          setErrorMessage("Unable to load customer.");
        }
      });

    return () => {
      isMounted = false;
    };
  }, [tenantId, customerPublicId]);

  useEffect(() => {
    if (!successMessage) {
      return;
    }

    const timeoutId = window.setTimeout(() => setSuccessMessage(""), 2500);
    return () => window.clearTimeout(timeoutId);
  }, [successMessage]);

  const handleSave = () => {
    if (!customer) {
      return;
    }

    const clientErrors = validateCustomerFields({
      customer_code: customerCode || null,
      billing_email: billingEmail || null,
      billing_phone: billingPhone || null,
      accounts_payable_email: accountsPayableEmail || null,
      accounts_payable_phone: accountsPayablePhone || null,
      primary_contact_name: primaryContactName || null,
      notes: notes || null,
    });
    setFieldErrors(clientErrors);
    if (Object.keys(clientErrors).length > 0) {
      setErrorMessage("");
      return;
    }

    setErrorMessage("");
    setSuccessMessage("");
    updateCustomer(tenantId, customer.public_id, {
      customer_code: customerCode || null,
      billing_email: billingEmail || null,
      billing_phone: billingPhone || null,
      accounts_payable_email: accountsPayableEmail || null,
      accounts_payable_phone: accountsPayablePhone || null,
      primary_contact_name: primaryContactName || null,
      notes: notes || null,
    })
      .then((updatedCustomer) => {
        setCustomer(updatedCustomer);
        applyCustomer(updatedCustomer);
        setFieldErrors({});
        setSuccessMessage("Customer saved.");
      })
      .catch((error) => {
        const parsedError = parseCustomerApiError(error);
        setFieldErrors(parsedError.fieldErrors);
        setErrorMessage(parsedError.message);
      });
  };

  const handleCancel = () => {
    if (customer) {
      applyCustomer(customer);
      setFieldErrors({});
      setErrorMessage("");
      setSuccessMessage("");
    }
  };

  const currentSnapshot = normalizeCustomerSnapshot({
    customer_code: customerCode || null,
    billing_email: billingEmail || null,
    billing_phone: billingPhone || null,
    accounts_payable_email: accountsPayableEmail || null,
    accounts_payable_phone: accountsPayablePhone || null,
    primary_contact_name: primaryContactName || null,
    notes: notes || null,
  });
  const hasChanges =
    savedSnapshot !== null && JSON.stringify(currentSnapshot) !== JSON.stringify(savedSnapshot);

  if (loadState === "loading") {
    return <p className="muted">Loading customer...</p>;
  }

  if (!customer) {
    return <div className="error-banner">{errorMessage || "Customer unavailable."}</div>;
  }

  return (
    <section className="vendor-workspace" aria-label="Customer workspace">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Customer</p>
          <h2>{customer.organization_display_name}</h2>
        </div>
        <button
          className="secondary-button"
          type="button"
          onClick={() => onBackToOrganization(customer.organization_id)}
        >
          Back to Organization
        </button>
      </div>

      {errorMessage && <div className="error-banner">{errorMessage}</div>}
      {successMessage && <div className="success-banner">{successMessage}</div>}

      <section className="vendor-profile">
        <div>
          <p className="eyebrow">Profile</p>
          <h3>Customer details</h3>
        </div>
        <p className="muted">
          Linked organization: {customer.organization_display_name}
        </p>

        <div className="editor-grid">
          <label className="field">
            <span>Customer Code</span>
            <input
              aria-invalid={Boolean(fieldErrors.customer_code)}
              className={fieldErrors.customer_code ? "input-error" : undefined}
              value={customerCode}
              onChange={(event) =>
                updateField("customer_code", event.target.value, setCustomerCode, fieldErrors, setFieldErrors)
              }
            />
            {fieldErrors.customer_code && <small className="field-error">{fieldErrors.customer_code}</small>}
          </label>
          <label className="field">
            <span>Billing Email</span>
            <input
              aria-invalid={Boolean(fieldErrors.billing_email)}
              className={fieldErrors.billing_email ? "input-error" : undefined}
              value={billingEmail}
              type="email"
              onChange={(event) =>
                updateField("billing_email", event.target.value, setBillingEmail, fieldErrors, setFieldErrors)
              }
            />
            {fieldErrors.billing_email && <small className="field-error">{fieldErrors.billing_email}</small>}
          </label>
          <label className="field">
            <span>Billing Phone</span>
            <input
              aria-invalid={Boolean(fieldErrors.billing_phone)}
              className={fieldErrors.billing_phone ? "input-error" : undefined}
              value={billingPhone}
              type="tel"
              onChange={(event) =>
                updateField("billing_phone", event.target.value, setBillingPhone, fieldErrors, setFieldErrors)
              }
            />
            {fieldErrors.billing_phone && <small className="field-error">{fieldErrors.billing_phone}</small>}
          </label>
          <label className="field">
            <span>Accounts Payable Email</span>
            <input
              aria-invalid={Boolean(fieldErrors.accounts_payable_email)}
              className={fieldErrors.accounts_payable_email ? "input-error" : undefined}
              value={accountsPayableEmail}
              type="email"
              onChange={(event) =>
                updateField(
                  "accounts_payable_email",
                  event.target.value,
                  setAccountsPayableEmail,
                  fieldErrors,
                  setFieldErrors,
                )
              }
            />
            {fieldErrors.accounts_payable_email && (
              <small className="field-error">{fieldErrors.accounts_payable_email}</small>
            )}
          </label>
          <label className="field">
            <span>Accounts Payable Phone</span>
            <input
              aria-invalid={Boolean(fieldErrors.accounts_payable_phone)}
              className={fieldErrors.accounts_payable_phone ? "input-error" : undefined}
              value={accountsPayablePhone}
              type="tel"
              onChange={(event) =>
                updateField(
                  "accounts_payable_phone",
                  event.target.value,
                  setAccountsPayablePhone,
                  fieldErrors,
                  setFieldErrors,
                )
              }
            />
            {fieldErrors.accounts_payable_phone && (
              <small className="field-error">{fieldErrors.accounts_payable_phone}</small>
            )}
          </label>
          <label className="field">
            <span>Primary Contact Name</span>
            <input
              aria-invalid={Boolean(fieldErrors.primary_contact_name)}
              className={fieldErrors.primary_contact_name ? "input-error" : undefined}
              value={primaryContactName}
              onChange={(event) =>
                updateField(
                  "primary_contact_name",
                  event.target.value,
                  setPrimaryContactName,
                  fieldErrors,
                  setFieldErrors,
                )
              }
            />
            {fieldErrors.primary_contact_name && (
              <small className="field-error">{fieldErrors.primary_contact_name}</small>
            )}
          </label>
          <label className="field">
            <span>Notes</span>
            <input
              aria-invalid={Boolean(fieldErrors.notes)}
              className={fieldErrors.notes ? "input-error" : undefined}
              value={notes}
              onChange={(event) =>
                updateField("notes", event.target.value, setNotes, fieldErrors, setFieldErrors)
              }
            />
            {fieldErrors.notes && <small className="field-error">{fieldErrors.notes}</small>}
          </label>
        </div>

        <div className="editor-actions">
          <button type="button" onClick={handleSave} disabled={!hasChanges}>
            Save Customer
          </button>
          <button
            className="secondary-button"
            type="button"
            onClick={handleCancel}
            disabled={!hasChanges}
          >
            Cancel
          </button>
        </div>
      </section>
    </section>
  );
}

function buildCustomerSnapshot(customer: Customer): CustomerSnapshot {
  return normalizeCustomerSnapshot({
    customer_code: customer.customer_code,
    billing_email: customer.billing_email,
    billing_phone: customer.billing_phone,
    accounts_payable_email: customer.accounts_payable_email,
    accounts_payable_phone: customer.accounts_payable_phone,
    primary_contact_name: customer.primary_contact_name,
    notes: customer.notes,
  });
}

function normalizeCustomerSnapshot(snapshot: CustomerSnapshot): CustomerSnapshot {
  return {
    customer_code: normalizeNullableText(snapshot.customer_code),
    billing_email: normalizeNullableText(snapshot.billing_email),
    billing_phone: normalizeNullableText(snapshot.billing_phone),
    accounts_payable_email: normalizeNullableText(snapshot.accounts_payable_email),
    accounts_payable_phone: normalizeNullableText(snapshot.accounts_payable_phone),
    primary_contact_name: normalizeNullableText(snapshot.primary_contact_name),
    notes: normalizeNullableText(snapshot.notes),
  };
}

function normalizeNullableText(value: string | null) {
  return value?.trim() || null;
}

function validateCustomerFields(snapshot: CustomerSnapshot): CustomerFieldErrors {
  const errors: CustomerFieldErrors = {};
  const billingEmail = snapshot.billing_email?.trim() || "";
  const accountsPayableEmail = snapshot.accounts_payable_email?.trim() || "";
  const billingPhone = snapshot.billing_phone?.trim() || "";
  const accountsPayablePhone = snapshot.accounts_payable_phone?.trim() || "";

  if (billingEmail && !isValidEmail(billingEmail)) {
    errors.billing_email = "Billing email must be a valid email address.";
  }
  if (accountsPayableEmail && !isValidEmail(accountsPayableEmail)) {
    errors.accounts_payable_email = "Accounts payable email must be a valid email address.";
  }
  if (billingPhone && !isValidPhone(billingPhone)) {
    errors.billing_phone = "Billing phone must be a valid phone number.";
  }
  if (accountsPayablePhone && !isValidPhone(accountsPayablePhone)) {
    errors.accounts_payable_phone = "Accounts payable phone must be a valid phone number.";
  }

  return errors;
}

function isValidEmail(value: string) {
  return /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(value);
}

function isValidPhone(value: string) {
  const digitCount = Array.from(value).filter((character) => /\d/.test(character)).length;
  return digitCount >= 7 && digitCount <= 20 && /^[0-9\s()+.-]+$/.test(value);
}

function updateField(
  field: keyof CustomerSnapshot,
  value: string,
  setter: (value: string) => void,
  currentErrors: CustomerFieldErrors,
  setFieldErrors: (errors: CustomerFieldErrors) => void,
) {
  setter(value);
  if (!currentErrors[field]) {
    return;
  }

  const nextSnapshot = {
    customer_code: null,
    billing_email: null,
    billing_phone: null,
    accounts_payable_email: null,
    accounts_payable_phone: null,
    primary_contact_name: null,
    notes: null,
    [field]: value || null,
  };
  if (!validateCustomerFields(nextSnapshot)[field]) {
    const remainingErrors = { ...currentErrors };
    delete remainingErrors[field];
    setFieldErrors(remainingErrors);
  }
}

function parseCustomerApiError(error: unknown): { fieldErrors: CustomerFieldErrors; message: string } {
  const detail = getApiErrorDetail(error);
  const fieldErrors: CustomerFieldErrors = {};
  let message = "";

  if (Array.isArray(detail)) {
    for (const item of detail) {
      if (typeof item !== "object" || item === null) {
        continue;
      }
      const issue = item as { loc?: unknown[]; msg?: unknown };
      const field = issue.loc?.[issue.loc.length - 1];
      const issueMessage = typeof issue.msg === "string" ? issue.msg : "Invalid value.";
      assignFieldError(fieldErrors, field, humanizeValidationMessage(field, issueMessage));
    }
  }

  if (typeof detail === "string") {
    message = assignStringDetail(fieldErrors, detail);
  }

  return {
    fieldErrors,
    message: Object.keys(fieldErrors).length > 0 ? "" : message || "Unable to save customer.",
  };
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

function assignStringDetail(fieldErrors: CustomerFieldErrors, detail: string) {
  const lowerDetail = detail.toLowerCase();
  if (lowerDetail.includes("active customer already exists")) {
    return "An active customer role already exists for this organization.";
  }
  if (lowerDetail.includes("organization is invalid")) {
    return "Customer role must be linked to an organization in this tenant.";
  }
  if (lowerDetail.includes("accounts payable") && lowerDetail.includes("phone")) {
    fieldErrors.accounts_payable_phone = "Accounts payable phone must be a valid phone number.";
    return "";
  }
  if (lowerDetail.includes("accounts payable") && lowerDetail.includes("email")) {
    fieldErrors.accounts_payable_email = "Accounts payable email must be a valid email address.";
    return "";
  }
  if (lowerDetail.includes("billing") && lowerDetail.includes("phone")) {
    fieldErrors.billing_phone = "Billing phone must be a valid phone number.";
    return "";
  }
  if (lowerDetail.includes("billing") && lowerDetail.includes("email")) {
    fieldErrors.billing_email = "Billing email must be a valid email address.";
    return "";
  }
  if (lowerDetail.includes("phone")) {
    fieldErrors.billing_phone = "Billing phone must be a valid phone number.";
    return "";
  }
  if (lowerDetail.includes("email")) {
    fieldErrors.billing_email = "Billing email must be a valid email address.";
    return "";
  }
  return detail;
}

function assignFieldError(
  fieldErrors: CustomerFieldErrors,
  field: unknown,
  message: string,
) {
  if (field === "billing_phone") {
    fieldErrors.billing_phone = message;
  }
  if (field === "billing_email") {
    fieldErrors.billing_email = message;
  }
  if (field === "accounts_payable_phone") {
    fieldErrors.accounts_payable_phone = message;
  }
  if (field === "accounts_payable_email") {
    fieldErrors.accounts_payable_email = message;
  }
  if (field === "customer_code") {
    fieldErrors.customer_code = message;
  }
  if (field === "primary_contact_name") {
    fieldErrors.primary_contact_name = message;
  }
  if (field === "notes") {
    fieldErrors.notes = message;
  }
}

function humanizeValidationMessage(field: unknown, message: string) {
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
  if (lowerMessage.includes("string_too_long")) {
    return "Value is too long.";
  }
  return message;
}
