import type {
  SimulationState,
  SimulationMetrics,
  ServerCreate,
  VMCreate,
  PlacementRequest,
} from "../types/simulation";

const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function request<T>(
  endpoint: string,
  method: "GET" | "POST" = "GET",
  body?: unknown,
): Promise<T> {
  const response = await fetch(`${BASE_URL}/simulation${endpoint}`, {
    method,
    headers: {
      "Content-Type": "application/json",
    },
    ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
  });

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => ({ detail: "Request failed." }));

    throw new Error(
      typeof error.detail === "string"
        ? error.detail
        : JSON.stringify(error.detail),
    );
  }

  return response.json() as Promise<T>;
}

interface ActionResponse {
  success: boolean;
  state: SimulationState;
}

export const simulationApi = {
  state: () => request<SimulationState>("/state"),

  metrics: () => request<SimulationMetrics>("/metrics"),

  reset: () => request<ActionResponse>("/reset", "POST"),

  createServer: (data: ServerCreate) =>
    request<ActionResponse>("/servers", "POST", data),

  createVM: (data: VMCreate) => request<ActionResponse>("/vms", "POST", data),

  allocate: (data: PlacementRequest) =>
    request<ActionResponse>("/allocate", "POST", data),

  migrate: (data: PlacementRequest) =>
    request<ActionResponse>("/migrate", "POST", data),
};
