import { api } from "../../shared/api/client";
import type { DemoSession } from "./types";

export async function createDemoSession(): Promise<DemoSession> {
  const response = await api.post<DemoSession>("/demo/sessions");
  return response.data;
}
