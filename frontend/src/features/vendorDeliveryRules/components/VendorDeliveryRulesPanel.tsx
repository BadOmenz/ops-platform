import { useEffect, useMemo, useState, type Dispatch, type SetStateAction } from "react";

import { useVendorDeliveryRules } from "../hooks/useVendorDeliveryRules";
import type {
  CreateVendorDeliveryRulePayload,
  UpdateVendorDeliveryRulePayload,
  VendorDeliveryRule,
  VendorDeliveryRuleStatusFilter,
  Weekday,
} from "../types";

const weekdays: Weekday[] = [
  "monday",
  "tuesday",
  "wednesday",
  "thursday",
  "friday",
  "saturday",
  "sunday",
];

type VendorDeliveryRulesPanelProps = {
  tenantId: string;
  vendorPublicId: string;
};

type DeliveryRuleFormState = {
  delivery_weekday: Weekday;
  order_cutoff_weekday: Weekday;
  order_cutoff_time: string;
  lead_time_days: string;
  minimum_order_value: string;
  delivery_window_start: string;
  delivery_window_end: string;
  notes: string;
};

const emptyFormState: DeliveryRuleFormState = {
  delivery_weekday: "monday",
  order_cutoff_weekday: "friday",
  order_cutoff_time: "",
  lead_time_days: "",
  minimum_order_value: "",
  delivery_window_start: "",
  delivery_window_end: "",
  notes: "",
};

export function VendorDeliveryRulesPanel({ tenantId, vendorPublicId }: VendorDeliveryRulesPanelProps) {
  const deliveryRules = useVendorDeliveryRules({ tenantId, vendorPublicId });
  const [selectedPublicId, setSelectedPublicId] = useState("");
  const selectedRule =
    deliveryRules.rules.find((rule) => rule.public_id === selectedPublicId) || null;
  const visibleRules = useMemo(() => sortDeliveryRules(deliveryRules.rules), [deliveryRules.rules]);

  useEffect(() => {
    if (
      selectedPublicId &&
      !deliveryRules.rules.some((rule) => rule.public_id === selectedPublicId)
    ) {
      setSelectedPublicId("");
    }
  }, [deliveryRules.rules, selectedPublicId]);

  return (
    <section className="vendor-delivery-rules-panel" aria-label="Vendor delivery rules">
      {deliveryRules.errorMessage && <div className="error-banner">{deliveryRules.errorMessage}</div>}

      <div className="vendor-delivery-rules-toolbar">
        <h3>Delivery Rules</h3>
        <span className="muted">{deliveryRules.rules.length} rules</span>
        <button type="button" onClick={deliveryRules.refreshRules}>
          Refresh
        </button>
        <select
          value={deliveryRules.status}
          onChange={(event) => deliveryRules.setStatus(event.target.value as VendorDeliveryRuleStatusFilter)}
        >
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
          <option value="all">All</option>
        </select>
      </div>

      <DeliveryRuleForm
        onCancel={() => setSelectedPublicId("")}
        onCreate={deliveryRules.createRule}
        onSave={deliveryRules.saveRule}
        onSaved={(rule) => setSelectedPublicId(rule.public_id)}
        rule={selectedRule}
      />

      <DeliveryRulesTable
        loadState={deliveryRules.loadState}
        onSelect={setSelectedPublicId}
        onToggleActive={deliveryRules.toggleRuleActive}
        rules={visibleRules}
        selectedPublicId={selectedPublicId}
      />
    </section>
  );
}

type DeliveryRuleFormProps = {
  onCancel: () => void;
  onCreate: (payload: CreateVendorDeliveryRulePayload) => Promise<VendorDeliveryRule>;
  onSave: (deliveryRulePublicId: string, payload: UpdateVendorDeliveryRulePayload) => Promise<VendorDeliveryRule>;
  onSaved: (rule: VendorDeliveryRule) => void;
  rule: VendorDeliveryRule | null;
};

function DeliveryRuleForm({ onCancel, onCreate, onSave, onSaved, rule }: DeliveryRuleFormProps) {
  const [formState, setFormState] = useState<DeliveryRuleFormState>(emptyFormState);
  const [savedFormState, setSavedFormState] = useState<DeliveryRuleFormState>(emptyFormState);
  const [validationMessage, setValidationMessage] = useState("");
  const [saveState, setSaveState] = useState<"idle" | "saving">("idle");

  useEffect(() => {
    const nextFormState = rule ? buildFormState(rule) : emptyFormState;
    setFormState(nextFormState);
    setSavedFormState(nextFormState);
    setValidationMessage("");
  }, [rule]);

  const hasChanges = JSON.stringify(formState) !== JSON.stringify(savedFormState);
  const canSave = saveState !== "saving" && hasChanges && formState.order_cutoff_time.trim().length > 0;

  const handleSave = () => {
    const clientError = validateFormState(formState);
    if (clientError) {
      setValidationMessage(clientError);
      return;
    }

    setValidationMessage("");
    setSaveState("saving");
    const payload = rule ? buildChangedPayload(formState, savedFormState) : buildPayload(formState);
    const request = rule ? onSave(rule.public_id, payload) : onCreate(payload as CreateVendorDeliveryRulePayload);
    request
      .then((savedRule) => {
        const nextSavedFormState = buildFormState(savedRule);
        setFormState(nextSavedFormState);
        setSavedFormState(nextSavedFormState);
        onSaved(savedRule);
      })
      .finally(() => setSaveState("idle"));
  };

  const handleNew = () => {
    setFormState(emptyFormState);
    setSavedFormState(emptyFormState);
    setValidationMessage("");
    onCancel();
  };

  return (
    <div className="delivery-rule-form" aria-label={rule ? "Edit delivery rule" : "Create delivery rule"}>
      {validationMessage && <div className="error-banner">{validationMessage}</div>}

      <SelectField label="Delivery day" name="delivery_weekday" state={formState} setState={setFormState} />
      <SelectField label="Order by" name="order_cutoff_weekday" state={formState} setState={setFormState} />
      <TimeField label="Cutoff" name="order_cutoff_time" state={formState} setState={setFormState} />
      <NumberField label="Lead days" name="lead_time_days" state={formState} setState={setFormState} />
      <NumberField label="Min order" name="minimum_order_value" state={formState} setState={setFormState} />
      <TimeField label="Window start" name="delivery_window_start" state={formState} setState={setFormState} />
      <TimeField label="Window end" name="delivery_window_end" state={formState} setState={setFormState} />
      <label className="field delivery-rule-notes">
        <span>Notes</span>
        <input value={formState.notes} onChange={(event) => updateField("notes", event.target.value, setFormState)} />
      </label>
      <div className="editor-actions delivery-rule-actions">
        <button type="button" onClick={handleSave} disabled={!canSave}>
          {saveState === "saving" ? "Saving..." : "Save"}
        </button>
        <button className="secondary-button" type="button" onClick={handleNew} disabled={!rule && !hasChanges}>
          New
        </button>
      </div>
    </div>
  );
}

function DeliveryRulesTable({
  loadState,
  onSelect,
  onToggleActive,
  rules,
  selectedPublicId,
}: {
  loadState: "idle" | "loading" | "ready" | "error";
  onSelect: (publicId: string) => void;
  onToggleActive: (rule: VendorDeliveryRule) => Promise<VendorDeliveryRule>;
  rules: VendorDeliveryRule[];
  selectedPublicId: string;
}) {
  return (
    <div className="table-shell setup-table delivery-rules-table">
      <table>
        <thead>
          <tr>
            <th>Delivery</th>
            <th>Order Cutoff</th>
            <th>Minimum</th>
            <th>Window</th>
            <th>Notes</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {rules.map((rule) => (
            <tr
              key={rule.public_id}
              className={selectedPublicId === rule.public_id ? "selected-row" : undefined}
              onClick={() => onSelect(rule.public_id)}
            >
              <td>
                <strong>{formatWeekday(rule.delivery_weekday)} delivery</strong>
                {rule.lead_time_days !== null && (
                  <span className="muted"> {rule.lead_time_days} lead days</span>
                )}
              </td>
              <td>
                Order by {formatWeekday(rule.order_cutoff_weekday)} {formatTime(rule.order_cutoff_time)}
              </td>
              <td>{formatMinimum(rule.minimum_order_value)}</td>
              <td>{formatWindow(rule)}</td>
              <td>{rule.notes || ""}</td>
              <td>
                <span className={`status-label ${rule.is_active ? "is-success" : "is-danger"}`}>
                  {rule.is_active ? "Active" : "Inactive"}
                </span>
              </td>
              <td>
                <button
                  type="button"
                  onClick={(event) => {
                    event.stopPropagation();
                    onToggleActive(rule);
                  }}
                >
                  {rule.is_active ? "Deactivate" : "Reactivate"}
                </button>
              </td>
            </tr>
          ))}
          {rules.length === 0 && (
            <tr>
              <td colSpan={7}>
                {loadState === "loading" ? "Loading delivery rules..." : "No delivery rules yet."}
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

function SelectField({
  label,
  name,
  state,
  setState,
}: {
  label: string;
  name: "delivery_weekday" | "order_cutoff_weekday";
  state: DeliveryRuleFormState;
  setState: Dispatch<SetStateAction<DeliveryRuleFormState>>;
}) {
  return (
    <label className="field">
      <span>{label}</span>
      <select value={state[name]} onChange={(event) => updateField(name, event.target.value, setState)}>
        {weekdays.map((weekday) => (
          <option key={weekday} value={weekday}>
            {formatWeekday(weekday)}
          </option>
        ))}
      </select>
    </label>
  );
}

function TimeField({
  label,
  name,
  state,
  setState,
}: {
  label: string;
  name: keyof DeliveryRuleFormState;
  state: DeliveryRuleFormState;
  setState: Dispatch<SetStateAction<DeliveryRuleFormState>>;
}) {
  return (
    <label className="field">
      <span>{label}</span>
      <input type="time" value={state[name]} onChange={(event) => updateField(name, event.target.value, setState)} />
    </label>
  );
}

function NumberField({
  label,
  name,
  state,
  setState,
}: {
  label: string;
  name: keyof DeliveryRuleFormState;
  state: DeliveryRuleFormState;
  setState: Dispatch<SetStateAction<DeliveryRuleFormState>>;
}) {
  return (
    <label className="field">
      <span>{label}</span>
      <input
        min="0"
        step="0.0001"
        type="number"
        value={state[name]}
        onChange={(event) => updateField(name, event.target.value, setState)}
      />
    </label>
  );
}

function updateField(
  field: keyof DeliveryRuleFormState,
  value: string,
  setState: Dispatch<SetStateAction<DeliveryRuleFormState>>,
) {
  setState((current) => ({ ...current, [field]: value }));
}

function buildFormState(rule: VendorDeliveryRule): DeliveryRuleFormState {
  return {
    delivery_weekday: rule.delivery_weekday,
    order_cutoff_weekday: rule.order_cutoff_weekday,
    order_cutoff_time: toTimeInputValue(rule.order_cutoff_time),
    lead_time_days: rule.lead_time_days === null ? "" : String(rule.lead_time_days),
    minimum_order_value: rule.minimum_order_value || "",
    delivery_window_start: toTimeInputValue(rule.delivery_window_start),
    delivery_window_end: toTimeInputValue(rule.delivery_window_end),
    notes: rule.notes || "",
  };
}

function buildPayload(formState: DeliveryRuleFormState): CreateVendorDeliveryRulePayload | UpdateVendorDeliveryRulePayload {
  return {
    delivery_weekday: formState.delivery_weekday,
    order_cutoff_weekday: formState.order_cutoff_weekday,
    order_cutoff_time: formState.order_cutoff_time,
    lead_time_days: normalizeOptionalInteger(formState.lead_time_days),
    minimum_order_value: normalizeOptionalNumber(formState.minimum_order_value),
    delivery_window_start: normalizeOptionalText(formState.delivery_window_start),
    delivery_window_end: normalizeOptionalText(formState.delivery_window_end),
    notes: normalizeOptionalText(formState.notes),
  };
}

function buildChangedPayload(
  formState: DeliveryRuleFormState,
  baseline: DeliveryRuleFormState,
): UpdateVendorDeliveryRulePayload {
  const fullPayload = buildPayload(formState) as UpdateVendorDeliveryRulePayload;
  const changedPayload: UpdateVendorDeliveryRulePayload = {};

  for (const field of Object.keys(formState) as Array<keyof DeliveryRuleFormState>) {
    if (formState[field] === baseline[field]) {
      continue;
    }
    const payloadField = field as keyof UpdateVendorDeliveryRulePayload;
    changedPayload[payloadField] = fullPayload[payloadField] as never;
  }

  return changedPayload;
}

function validateFormState(formState: DeliveryRuleFormState) {
  if (!formState.order_cutoff_time.trim()) {
    return "Order cutoff time is required.";
  }
  if (Number(formState.lead_time_days) < 0) {
    return "Lead days must be non-negative.";
  }
  if (Number(formState.minimum_order_value) < 0) {
    return "Minimum order must be non-negative.";
  }
  return "";
}

function normalizeOptionalText(value: string) {
  return value.trim() || null;
}

function normalizeOptionalNumber(value: string) {
  return value.trim() || null;
}

function normalizeOptionalInteger(value: string) {
  return value.trim() ? Number(value) : null;
}

function toTimeInputValue(value: string | null) {
  return value ? value.slice(0, 5) : "";
}

function sortDeliveryRules(rules: VendorDeliveryRule[]) {
  return [...rules].sort((first, second) => {
    const deliveryCompare = weekdays.indexOf(first.delivery_weekday) - weekdays.indexOf(second.delivery_weekday);
    if (deliveryCompare !== 0) {
      return deliveryCompare;
    }
    const cutoffCompare =
      weekdays.indexOf(first.order_cutoff_weekday) - weekdays.indexOf(second.order_cutoff_weekday);
    if (cutoffCompare !== 0) {
      return cutoffCompare;
    }
    return first.order_cutoff_time.localeCompare(second.order_cutoff_time);
  });
}

function formatWeekday(weekday: Weekday | string) {
  return weekday.charAt(0).toUpperCase() + weekday.slice(1);
}

function formatTime(value: string | null) {
  if (!value) {
    return "";
  }
  const [hourText, minuteText] = value.split(":");
  const hour = Number(hourText);
  const minute = Number(minuteText);
  if (Number.isNaN(hour) || Number.isNaN(minute)) {
    return value;
  }
  const suffix = hour >= 12 ? "PM" : "AM";
  const displayHour = hour % 12 || 12;
  return `${displayHour}:${String(minute).padStart(2, "0")} ${suffix}`;
}

function formatMinimum(value: string | null) {
  if (!value) {
    return "";
  }
  return `$${Number(value).toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
}

function formatWindow(rule: VendorDeliveryRule) {
  if (!rule.delivery_window_start && !rule.delivery_window_end) {
    return "";
  }
  return `${formatTime(rule.delivery_window_start)}-${formatTime(rule.delivery_window_end)}`;
}
