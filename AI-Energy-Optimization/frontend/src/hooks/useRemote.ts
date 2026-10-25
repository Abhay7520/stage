import { useCallback, useEffect, useState } from "react";
import { request } from "../services/client";
export function useRemote<T>(path: string) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const reload = useCallback(async () => {
    setBusy(true);
    setError("");
    try {
      const r = await request<T>(path);
      setData(r);
      return r;
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }, [path]);
  useEffect(() => {
    let active = true;
    request<T>(path)
      .then((r) => {
        if (active) setData(r);
      })
      .catch((e) => {
        if (active) setError(e instanceof Error ? e.message : String(e));
      });
    return () => {
      active = false;
    };
  }, [path]);
  return { data, setData, error, setError, busy, setBusy, reload };
}
