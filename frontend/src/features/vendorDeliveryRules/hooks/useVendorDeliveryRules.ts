import { useCallback, useEffect, useState } from "react";

import {
  createVendorDeliveryRule,
  deleteVendorDeliveryRule,
  getVendorDeliveryRules,
  reactivateVendorDeliveryRule,
  updateVendorDeliveryRule,
} from "../api";
import type {
  CreateVendorDeliveryRulePayload,
  UpdateVendorDeliveryRulePayload,
  VendorDeliveryRule,
  VendorDeliveryRuleStatusFilter,
} from "../types";

type UseVendorDeliveryRulesOptions = {
  tenantId: string;
  vendorPublicId: string;
};

export function useVendorDeliveryRules({ tenantId, vendorPublicId }: UseVendorDeliveryRulesOptions) {
  const [rules, setRules] = useState<VendorDeliveryRule[]>([]);
  const [status, setStatus] = useState<VendorDeliveryRuleStatusFilter>("active");
  const [loadState, setLoadState] = useState<"idle" | "loading" | "ready" | "error">("idle");
  const [errorMessage, setErrorMessage] = useState("");

  const refreshRules = useCallback(() => {
    if (!tenantId || !vendorPublicId) {
      setRules([]);
      return;
    }

    setRules([]);
    setErrorMessage("");
    setLoadState("loading");
    getVendorDeliveryRules(tenantId, vendorPublicId, status)
      .then((records) => {
        setRules(records);
        setLoadState("ready");
      })
      .catch((error) => {
        setRules([]);
        setLoadState("error");
        setErrorMessage(readApiError(error, "Unable to load delivery rules."));
      });
  }, [status, tenantId, vendorPublicId]);

  useEffect(() => {
    refreshRules();
  }, [refreshRules]);

  const createRule = (payload: CreateVendorDeliveryRulePayload) => {
    setErrorMessage("");
    return createVendorDeliveryRule(tenantId, vendorPublicId, payload)
      .then((createdRule) => {
        setRules((current) =>
          status === "all" || createdRule.is_active === (status === "active")
            ? [createdRule, ...current]
            : current,
        );
        return createdRule;
      })
      .catch((error) => {
        setErrorMessage(readApiError(error, "Unable to create delivery rule."));
        throw error;
      });
  };

  const saveRule = (deliveryRulePublicId: string, payload: UpdateVendorDeliveryRulePayload) => {
    setErrorMessage("");
    return updateVendorDeliveryRule(tenantId, deliveryRulePublicId, payload)
      .then((updatedRule) => {
        setRules((current) =>
          current
            .map((rule) => (rule.public_id === updatedRule.public_id ? updatedRule : rule))
            .filter((rule) => status === "all" || rule.is_active === (status === "active")),
        );
        return updatedRule;
      })
      .catch((error) => {
        setErrorMessage(readApiError(error, "Unable to save delivery rule."));
        throw error;
      });
  };

  const toggleRuleActive = (rule: VendorDeliveryRule) => {
    setErrorMessage("");
    const request = rule.is_active
      ? deleteVendorDeliveryRule(tenantId, rule.public_id)
      : reactivateVendorDeliveryRule(tenantId, rule.public_id);

    return request
      .then((updatedRule) => {
        setRules((current) =>
          current
            .map((record) => (record.public_id === updatedRule.public_id ? updatedRule : record))
            .filter((record) => status === "all" || record.is_active === (status === "active")),
        );
        return updatedRule;
      })
      .catch((error) => {
        setErrorMessage(readApiError(error, "Unable to update delivery rule status."));
        throw error;
      });
  };

  return {
    createRule,
    errorMessage,
    loadState,
    refreshRules,
    rules,
    saveRule,
    setStatus,
    status,
    toggleRuleActive,
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
    const response = error.response as { data?: { detail?: unknown }; status?: number };
    const data = response.data;
    if (typeof data?.detail === "string") {
      return data.detail;
    }
    if (typeof response.status === "number") {
      return `${fallback} (${response.status})`;
    }
  }
  return fallback;
}
