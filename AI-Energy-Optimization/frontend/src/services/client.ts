export const baseURL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
export async function request<T>(path: string, body?: unknown): Promise<T> {
  const r = await fetch(baseURL + path, {
    method: body === undefined ? "GET" : "POST",
    headers: { "Content-Type": "application/json" },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  });
  if (!r.ok) {
    const e = await r.json().catch(() => ({ detail: r.statusText }));
    throw new Error(
      typeof e.detail === "string"
        ? e.detail
        : Array.isArray(e.detail)
          ? e.detail
              .map(
                (issue: { loc?: Array<string | number>; msg?: string }) =>
                  `${issue.loc?.slice(1).join(".") || "Input"}: ${issue.msg || "Invalid value"}`,
              )
              .join("; ")
          : "Request failed. Check the input values and try again.",
    );
  }
  return r.json();
}
export async function downloadReport(path: string, name: string) {
  const r = await fetch(baseURL + path);
  if (!r.ok) {
    const e = await r.json();
    throw new Error(
      typeof e.detail === "string" ? e.detail : "Report unavailable",
    );
  }
  const url = URL.createObjectURL(await r.blob());
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  URL.revokeObjectURL(url);
}
