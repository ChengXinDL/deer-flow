"use client";

import {
  ChevronsUpDown,
  Settings2Icon,
  LogOutIcon,
  UserIcon,
} from "lucide-react";
import { useEffect, useState } from "react";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar";
import { useI18n } from "@/core/i18n/hooks";
import { useAuth } from "@/core/auth/hooks";
import { useRouter } from "next/navigation";

import { SettingsDialog } from "./settings";

function NavMenuButtonContent({
  isSidebarOpen,
  t,
  user,
  isAuthenticated,
}: {
  isSidebarOpen: boolean;
  t: ReturnType<typeof useI18n>["t"];
  user: any;
  isAuthenticated: boolean;
}) {
  if (!isAuthenticated) {
    return isSidebarOpen ? (
      <div className="text-muted-foreground flex w-full items-center gap-2 text-left text-sm">
        <UserIcon className="size-4" />
        <span>登录</span>
        <ChevronsUpDown className="text-muted-foreground ml-auto size-4" />
      </div>
    ) : (
      <div className="flex size-full items-center justify-center">
        <UserIcon className="text-muted-foreground size-4" />
      </div>
    );
  }

  return isSidebarOpen ? (
    <div className="text-muted-foreground flex w-full items-center gap-2 text-left text-sm">
      <div className="flex size-8 items-center justify-center rounded-full bg-green-100 text-green-600">
        {user?.avatar_url ? (
          <img
            src={user.avatar_url}
            alt={user.name}
            className="size-8 rounded-full object-cover"
          />
        ) : (
          <UserIcon className="size-4" />
        )}
      </div>
      <div className="flex-1 min-w-0">
        <div className="truncate font-medium text-foreground">
          {user?.name || "用户"}
        </div>
        <div className="truncate text-xs text-muted-foreground">
          {user?.email || "未登录"}
        </div>
      </div>
      <ChevronsUpDown className="text-muted-foreground ml-2 size-4" />
    </div>
  ) : (
    <div className="flex size-full items-center justify-center">
      <div className="flex size-6 items-center justify-center rounded-full bg-green-100 text-green-600">
        {user?.avatar_url ? (
          <img
            src={user.avatar_url}
            alt={user.name}
            className="size-6 rounded-full object-cover"
          />
        ) : (
          <UserIcon className="size-3" />
        )}
      </div>
    </div>
  );
}

export function WorkspaceNavMenu() {
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [settingsDefaultSection, setSettingsDefaultSection] = useState<
    "appearance" | "memory" | "skills" | "notification" | "about"
  >("appearance");
  const [mounted, setMounted] = useState(false);
  const { open: isSidebarOpen } = useSidebar();
  const { t } = useI18n();
  const { user, logout, isAuthenticated } = useAuth();
  const router = useRouter();

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleButtonClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!isAuthenticated) {
      router.push("/auth/login");
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error("登出失败:", error);
    }
  };

  return (
    <>
      <SettingsDialog
        open={settingsOpen}
        onOpenChange={setSettingsOpen}
        defaultSection={settingsDefaultSection}
      />
      <SidebarMenu className="w-full">
        <SidebarMenuItem>
          {mounted ? (
            isAuthenticated ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <SidebarMenuButton
                    size="lg"
                    className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
                  >
                    <NavMenuButtonContent isSidebarOpen={isSidebarOpen} t={t} user={user} isAuthenticated={isAuthenticated} />
                  </SidebarMenuButton>
                </DropdownMenuTrigger>
                <DropdownMenuContent
                  className="w-(--radix-dropdown-menu-trigger-width) min-w-56 rounded-lg"
                  align="end"
                  sideOffset={4}
                >
                  <DropdownMenuGroup>
                    <DropdownMenuItem
                      onClick={() => {
                        setSettingsDefaultSection("appearance");
                        setSettingsOpen(true);
                      }}
                    >
                      <Settings2Icon className="mr-2 size-4" />
                      设置
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem
                      onClick={handleLogout}
                    >
                      <LogOutIcon className="mr-2 size-4" />
                      登出
                    </DropdownMenuItem>
                  </DropdownMenuGroup>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <button
                type="button"
                className="peer/menu-button flex w-full items-center gap-2 overflow-hidden rounded-md p-2 text-left text-sm outline-hidden ring-sidebar-ring transition-[width,height,padding] hover:bg-sidebar-accent hover:text-sidebar-accent-foreground focus-visible:ring-2 active:bg-sidebar-accent active:text-sidebar-accent-foreground disabled:pointer-events-none disabled:opacity-50 group-has-data-[sidebar=menu-action]/menu-item:pr-8 aria-disabled:pointer-events-none aria-disabled:opacity-50 data-[active=true]:bg-sidebar-accent data-[active=true]:font-medium data-[active=true]:text-sidebar-accent-foreground data-[state=open]:hover:bg-sidebar-accent data-[state=open]:hover:text-sidebar-accent-foreground group-data-[collapsible=icon]:size-8! hover:bg-sidebar-accent hover:text-sidebar-accent-foreground h-12"
                onClick={handleButtonClick}
              >
                <NavMenuButtonContent isSidebarOpen={isSidebarOpen} t={t} user={user} isAuthenticated={isAuthenticated} />
              </button>
            )
          ) : (
            <SidebarMenuButton size="lg" className="pointer-events-none">
              <NavMenuButtonContent isSidebarOpen={isSidebarOpen} t={t} user={user} isAuthenticated={isAuthenticated} />
            </SidebarMenuButton>
          )}
        </SidebarMenuItem>
      </SidebarMenu>
    </>
  );
}

