import { getLangGraphBaseURL } from "../config";

export interface AgentConfig {
  id: string;
  name: string;
  description: string;
}

// LangGraph Assistant 接口
interface LangGraphAssistant {
  assistant_id: string;
  graph_id: string;
  config: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  name?: string;
  metadata: {
    name?: string;
    description?: string;
  };
}

// 缓存 graph_id 到 assistant_id 的映射
let graphIdToAssistantIdCache: Map<string, string> = new Map();

export async function resolveGraphIdToAssistantId(graphId: string): Promise<string | null> {
  const baseUrl = getLangGraphBaseURL();
  console.log("resolveGraphIdToAssistantId:", graphId, "baseUrl:", baseUrl);
  
  // 先清除缓存，确保获取最新的
  graphIdToAssistantIdCache.clear();
  
  try {
    const response = await fetch(`${baseUrl}/assistants/search`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({}),
    });
    
    if (!response.ok) {
      console.error("Failed to search assistants:", response.statusText);
      return null;
    }
    
    const assistants: LangGraphAssistant[] = await response.json();
    console.log("Available assistants:", assistants.map(a => a.graph_id));
    
    const agent = assistants.find(a => a.graph_id === graphId);
    
    if (agent) {
      console.log("Found assistant_id for", graphId, ":", agent.assistant_id);
      graphIdToAssistantIdCache.set(graphId, agent.assistant_id);
      return agent.assistant_id;
    }
    
    console.error("No assistant found for graph_id:", graphId);
    return null;
  } catch (error) {
    console.error("Error resolving graph_id to assistant_id:", error);
    return null;
  }
}

export async function listAgents(): Promise<AgentConfig[]> {
  const baseUrl = getLangGraphBaseURL();
  const response = await fetch(`${baseUrl}/assistants/search`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({}),
  });
  if (!response.ok) {
    throw new Error(`Failed to fetch agents: ${response.statusText}`);
  }
  const assistants: LangGraphAssistant[] = await response.json();
  // 过滤并去重：每个 graph_id 只保留一个
  // 只保留有效的 agents (sql-agent, research)
  const seen = new Set<string>();
  const uniqueAssistants = assistants.filter(assistant => {
    if (!seen.has(assistant.graph_id)) {
      seen.add(assistant.graph_id);
      return true;
    }
    return false;
  });
  
  return uniqueAssistants.map((assistant) => ({
    id: assistant.graph_id,
    name: assistant.name || assistant.metadata?.name || assistant.graph_id,
    description: assistant.metadata?.description || "",
  }));
}

export async function getAgent(id: string): Promise<AgentConfig | null> {
  try {
    // 先尝试通过 ID 直接获取
    const baseUrl = getLangGraphBaseURL();
    let response = await fetch(`${baseUrl}/assistants/${id}`);
    
    // 如果 404，尝试通过 graph_id 查找
    if (response.status === 404) {
      const searchResponse = await fetch(`${baseUrl}/assistants/search`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({}),
      });
      if (searchResponse.ok) {
        const assistants: LangGraphAssistant[] = await searchResponse.json();
        const agent = assistants.find(a => a.graph_id === id);
        if (agent) {
          response = await fetch(`${baseUrl}/assistants/${agent.assistant_id}`);
        }
      }
    }
    
    if (!response.ok) {
      if (response.status === 404) {
        return null;
      }
      throw new Error(`Failed to fetch agent: ${response.statusText}`);
    }
    
    const assistant: LangGraphAssistant = await response.json();
    return {
      id: assistant.graph_id,
      name: assistant.name || assistant.metadata?.name || assistant.graph_id,
      description: assistant.metadata?.description || "",
    };
  } catch (error) {
    console.error(`Failed to fetch agent ${id}:`, error);
    return null;
  }
}
