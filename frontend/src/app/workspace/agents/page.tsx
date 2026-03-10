"use client";

import { BrainIcon } from "lucide-react";
import { useMemo, useState } from "react";

import { AgentSelector } from "@/components/workspace/agent-selector";
import {
  WorkspaceBody,
  WorkspaceContainer,
  WorkspaceHeader,
} from "@/components/workspace/workspace-container";
import { useLocalSettings } from "@/core/settings";
import { useI18n } from "@/core/i18n/hooks";
import { useAgentConfigs } from "@/core/config/use-agent-configs";

export default function AgentsPage() {
  const { t } = useI18n();
  const [settings, setSettings] = useLocalSettings();
  const { agents: AGENT_CONFIGS } = useAgentConfigs();

  const handleAgentChange = (agentId: string) => {
    setSettings("agent", { assistant_id: agentId });
  };

  return (
    <WorkspaceContainer>
      <WorkspaceHeader>
        <h1 className="text-2xl font-semibold">{t.settings.sections.agent || "Agent"}</h1>
        <p className="text-muted-foreground">选择要使用的 AI Agent 类型</p>
      </WorkspaceHeader>
      <WorkspaceBody>
        <div className="mx-auto w-full max-w-(--container-width-md) space-y-4">
          <div>
            <label className="text-sm font-medium">当前 Agent</label>
            <p className="text-muted-foreground text-xs mb-4">
              选择不同的 Agent 会改变 AI 的行为和能力
            </p>
            <AgentSelector
              value={settings.agent.assistant_id}
              onValueChange={handleAgentChange}
            />
          </div>

          <div className="space-y-2 rounded-lg border p-4">
            <h3 className="text-sm font-semibold">Agent 说明</h3>
            <div className="space-y-2 text-sm text-muted-foreground">
              {AGENT_CONFIGS.map((agent) => (
                <div key={agent.id}>
                  <strong className="text-foreground">{agent.name}</strong>
                  <p>{agent.description}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-lg border border-blue-200 bg-blue-50 p-4 dark:border-blue-900 dark:bg-blue-950">
            <div className="flex items-start gap-2">
              <BrainIcon className="size-4 mt-0.5 text-blue-600 dark:text-blue-400" />
              <div className="space-y-1">
                <p className="text-sm">
                  <strong className="text-blue-900 dark:text-blue-100">提示</strong>
                </p>
                <p className="text-xs text-muted-foreground">
                  切换 Agent 后，新对话将使用选中的 Agent。现有对话不受影响。
                </p>
              </div>
            </div>
          </div>
        </div>
      </WorkspaceBody>
    </WorkspaceContainer>
  );
}
