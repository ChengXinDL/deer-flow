import { useEffect, useState } from "react";
import { listAgents, type AgentConfig } from "@/core/api/agents";

export function useAgents() {
  const [agents, setAgents] = useState<AgentConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    async function fetchAgents() {
      try {
        setLoading(true);
        setError(null);
        const data = await listAgents();
        setAgents(data);
      } catch (err) {
        console.error("Failed to fetch agents:", err);
        setError(err instanceof Error ? err : new Error("Failed to fetch agents"));
      } finally {
        setLoading(false);
      }
    }

    fetchAgents();
  }, []);

  return { agents, loading, error };
}
