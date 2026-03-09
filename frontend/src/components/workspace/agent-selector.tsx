"use client";

import { BrainIcon } from "lucide-react";

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useI18n } from "@/core/i18n/hooks";
import { useAgentConfigs } from "@/core/config/use-agent-configs";

export type AgentOption = {
  id: string;
  name: string;
  description: string;
};

export function AgentSelector({
  value,
  onValueChange,
}: {
  value: string;
  onValueChange: (value: string) => void;
}) {
  const { t } = useI18n();
  const { agents: AGENT_CONFIGS } = useAgentConfigs();

  return (
    <Select value={value} onValueChange={onValueChange}>
      <SelectTrigger className="w-[300px]">
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        {AGENT_CONFIGS.map((agent) => (
          <SelectItem key={agent.id} value={agent.id}>
            <div className="flex flex-col gap-1">
              <div className="flex items-center gap-2">
                <BrainIcon className="size-4" />
                <span className="font-semibold">{agent.name}</span>
              </div>
              <span className="text-muted-foreground text-xs">
                {agent.description}
              </span>
            </div>
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
