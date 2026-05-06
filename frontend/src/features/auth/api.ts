import { api } from "../../shared/api/client";
import type { CurrentUser } from "./types";

export async function getCurrentUser(): Promise<CurrentUser> {
  const response = await api.get<CurrentUser>("/identity/me");
  return response.data;
}

