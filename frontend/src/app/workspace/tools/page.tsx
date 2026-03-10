"use client";

import {
  Item,
  ItemActions,
  ItemContent,
  ItemDescription,
  ItemTitle,
} from "@/components/ui/item";
import { Switch } from "@/components/ui/switch";
import {
  WorkspaceBody,
  WorkspaceContainer,
  WorkspaceHeader,
} from "@/components/workspace/workspace-container";
import { useI18n } from "@/core/i18n/hooks";
import { useMCPConfig, useEnableMCPServer } from "@/core/mcp/hooks";
import type { MCPServerConfig } from "@/core/mcp/types";
import { env } from "@/env";

export default function ToolsPage() {
  const { t } = useI18n();
  const { config, isLoading, error } = useMCPConfig();

  return (
    <WorkspaceContainer>
      <WorkspaceHeader>
        <h1 className="text-2xl font-semibold">{t.settings.tools.title}</h1>
        <p className="text-muted-foreground">{t.settings.tools.description}</p>
      </WorkspaceHeader>
      <WorkspaceBody>
        <div className="mx-auto w-full max-w-(--container-width-md)">
          {isLoading ? (
            <div className="text-muted-foreground text-sm">{t.common.loading}</div>
          ) : error ? (
            <div>Error: {error.message}</div>
          ) : (
            config && <MCPServerList servers={config.mcp_servers} />
          )}
        </div>
      </WorkspaceBody>
    </WorkspaceContainer>
  );
}

function MCPServerList({
  servers,
}: {
  servers: Record<string, MCPServerConfig>;
}) {
  const { mutate: enableMCPServer } = useEnableMCPServer();
  return (
    <div className="flex w-full flex-col gap-4">
      {Object.entries(servers).map(([name, config]) => (
        <Item className="w-full" variant="outline" key={name}>
          <ItemContent>
            <ItemTitle>
              <div className="flex items-center gap-2">
                <div>{name}</div>
              </div>
            </ItemTitle>
            <ItemDescription className="line-clamp-4">
              {config.description}
            </ItemDescription>
          </ItemContent>
          <ItemActions>
            <Switch
              checked={config.enabled}
              disabled={env.NEXT_PUBLIC_STATIC_WEBSITE_ONLY === "true"}
              onCheckedChange={(checked) =>
                enableMCPServer({ serverName: name, enabled: checked })
              }
            />
          </ItemActions>
        </Item>
      ))}
    </div>
  );
}
