import { useEffect, useState } from "react";
import { listAgents } from "@/core/api/agents";
import { BrainIcon } from "lucide-react";
import { setCachedAgents, getCachedAgents, DEFAULT_AGENT_CONFIGS, type AgentConfig } from "@/core/config/agents";

export function useAgentConfigs() {
  const [agents, setAgents] = useState<AgentConfig[]>(getCachedAgents());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    async function fetchAgents() {
      try {
        setLoading(true);
        setError(null);
        const data = await listAgents();
        const agentsWithIcon = data.map((agent) => ({
          ...agent,
          icon: BrainIcon,
        }));
        setCachedAgents(agentsWithIcon);
        setAgents(agentsWithIcon);
      } catch (err) {
        console.error("Failed to fetch agent configs:", err);
        setError(err instanceof Error ? err : new Error("Failed to fetch agent configs"));
        // 使用默认配置
        setAgents(DEFAULT_AGENT_CONFIGS);
      } finally {
        setLoading(false);
      }
    }

    fetchAgents();
  }, []);

  return { agents, loading, error };
}
