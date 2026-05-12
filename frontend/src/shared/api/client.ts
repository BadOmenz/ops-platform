import axios, { AxiosHeaders } from "axios";

import { getStoredDemoSession } from "../../features/demo/session";
import { getApiBaseUrl } from "./config";

export const api = axios.create({
  baseURL: getApiBaseUrl(),
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  const session = getStoredDemoSession();
  if (!session) {
    return config;
  }

  const headers = AxiosHeaders.from(config.headers);
  headers.set("X-Demo-Session-Token", session.session_token);
  headers.set("X-Demo-Tenant-Id", session.tenant_id);
  config.headers = headers;
  return config;
});
