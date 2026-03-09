"use client";

import { BrainIcon } from "lucide-react";
import { useLocalSettings } from "@/core/settings";
import { getAgentName } from "@/core/config/agents";
import { useAgentConfigs } from "@/core/config/use-agent-configs";

export function CurrentAgentBadge() {
  const [settings] = useLocalSettings();
  const agentId = settings.agent.assistant_id;
  const { agents } = useAgentConfigs();
  const agentName = getAgentName(agentId);

  return (
    <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 text-primary text-xs font-medium">
      <BrainIcon className="size-3.5" />
      <span>{agentName}</span>
    </div>
  );
}
