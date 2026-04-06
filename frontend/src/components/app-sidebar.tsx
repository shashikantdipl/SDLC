"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Bot,
  GitBranch,
  Recycle,
  DollarSign,
} from "lucide-react";
import {
  SidebarProvider,
  Sidebar,
  SidebarHeader,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarInset,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { Separator } from "@/components/ui/separator";
import {
  TooltipProvider,
} from "@/components/ui/tooltip";

const navItems = [
  { title: "Dashboard", href: "/", icon: LayoutDashboard },
  { title: "Agents", href: "/agents", icon: Bot },
  { title: "Pipeline", href: "/pipeline", icon: GitBranch },
  { title: "Lifecycle", href: "/lifecycle", icon: Recycle },
  { title: "Costs", href: "/costs", icon: DollarSign },
];

export function AppSidebar({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <TooltipProvider delay={0}>
      <SidebarProvider>
        <Sidebar collapsible="icon" className="border-r border-sidebar-border">
          <SidebarHeader className="p-4">
            <Link href="/" className="flex items-center gap-2 group-data-[collapsible=icon]:justify-center">
              <span className="text-xl">🤖</span>
              <span className="text-sm font-bold tracking-tight text-sidebar-foreground group-data-[collapsible=icon]:hidden">
                Agentic SDLC
              </span>
            </Link>
          </SidebarHeader>
          <Separator className="mx-2 w-auto bg-sidebar-border" />
          <SidebarContent>
            <SidebarGroup>
              <SidebarGroupContent>
                <SidebarMenu>
                  {navItems.map((item) => (
                    <SidebarMenuItem key={item.href}>
                      <SidebarMenuButton
                        render={<Link href={item.href} />}
                        isActive={
                          item.href === "/"
                            ? pathname === "/"
                            : pathname.startsWith(item.href)
                        }
                        tooltip={item.title}
                      >
                        <item.icon className="size-4" />
                        <span>{item.title}</span>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          </SidebarContent>
          <SidebarFooter className="p-4">
            <div className="text-xs text-muted-foreground group-data-[collapsible=icon]:hidden">
              v1.0 &middot; 61 agents
            </div>
          </SidebarFooter>
        </Sidebar>
        <SidebarInset>
          <header className="flex h-12 shrink-0 items-center gap-2 border-b border-sidebar-border px-4">
            <SidebarTrigger className="-ml-1" />
            <Separator orientation="vertical" className="mr-2 h-4" />
            <span className="text-sm font-medium text-muted-foreground">
              Agentic SDLC Platform
            </span>
          </header>
          <div className="flex-1 overflow-auto">{children}</div>
        </SidebarInset>
      </SidebarProvider>
    </TooltipProvider>
  );
}
