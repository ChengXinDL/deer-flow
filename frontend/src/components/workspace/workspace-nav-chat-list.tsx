"use client";

import { MessagesSquare, Wrench, Brain, HardDrive, Sparkles } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import {
  SidebarGroup,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";
import { useI18n } from "@/core/i18n/hooks";

export function WorkspaceNavChatList() {
  const { t } = useI18n();
  const pathname = usePathname();
  return (
    <SidebarGroup className="pt-1">
      <SidebarMenu>
        <SidebarMenuItem>
          <SidebarMenuButton asChild>
            <Link
              className="text-muted-foreground"
              href="/workspace/chats"
              data-active={pathname === "/workspace/chats"}
            >
              <MessagesSquare />
              <span>{t.sidebar.chats}</span>
            </Link>
          </SidebarMenuButton>
        </SidebarMenuItem>
        <SidebarMenuItem>
          <SidebarMenuButton asChild>
            <Link
              className="text-muted-foreground"
              href="/workspace/tools"
              data-active={pathname === "/workspace/tools"}
            >
              <Wrench />
              <span>{t.settings.tools.title}</span>
            </Link>
          </SidebarMenuButton>
        </SidebarMenuItem>
        <SidebarMenuItem>
          <SidebarMenuButton asChild>
            <Link
              className="text-muted-foreground"
              href="/workspace/agents"
              data-active={pathname === "/workspace/agents"}
            >
              <Brain />
              <span>{t.settings.sections.agent || "Agent"}</span>
            </Link>
          </SidebarMenuButton>
        </SidebarMenuItem>
        <SidebarMenuItem>
          <SidebarMenuButton asChild>
            <Link
              className="text-muted-foreground"
              href="/workspace/memory"
              data-active={pathname === "/workspace/memory"}
            >
              <HardDrive />
              <span>{t.settings.sections.memory}</span>
            </Link>
          </SidebarMenuButton>
        </SidebarMenuItem>
        <SidebarMenuItem>
          <SidebarMenuButton asChild>
            <Link
              className="text-muted-foreground"
              href="/workspace/skills"
              data-active={pathname === "/workspace/skills"}
            >
              <Sparkles />
              <span>{t.settings.sections.skills}</span>
            </Link>
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarMenu>
    </SidebarGroup>
  );
}
