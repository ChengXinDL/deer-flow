import { BrainIcon } from "lucide-react";

export interface AgentConfig {
  id: string;
  name: string;
  description: string;
  icon?: React.ComponentType<{ className?: string }>;
}

// 默认配置，用于服务器端渲染或加载失败时
export const DEFAULT_AGENT_CONFIGS: AgentConfig[] = [
  {
    id: "lead_agent",
    name: "Lead Agent",
    description: "通用型 AI 助手，支持多种任务模式",
    icon: BrainIcon,
  },
  {
    id: "sql-agent",
    name: "SQL Agent",
    description: "专注于数据库查询和操作，适合数据相关任务",
    icon: BrainIcon,
  },
];

// 客户端缓存
let cachedAgents: AgentConfig[] | null = null;

export function getCachedAgents(): AgentConfig[] {
  return cachedAgents || DEFAULT_AGENT_CONFIGS;
}

export function setCachedAgents(agents: AgentConfig[]): void {
  cachedAgents = agents;
}

export function getAgentById(id: string): AgentConfig | undefined {
  const agents = getCachedAgents();
  return agents.find((agent) => agent.id === id);
}

export function getAgentName(id: string): string {
  const agent = getAgentById(id);
  return agent?.name || id;
}

export function getAgentDescription(id: string): string {
  const agent = getAgentById(id);
  return agent?.description || "";
}
