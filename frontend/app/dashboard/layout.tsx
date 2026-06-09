"use client";

import { ReactNode, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuthStore } from "@/store/auth";
import { Button } from "@/components/ui/button";
import {
  LayoutDashboard,
  Mail,
  Users,
  Send,
  BarChart3,
  Settings,
  Menu,
  ChevronLeft,
  MessageSquare,
  Thermometer,
  Shield,
  Briefcase,
  Bot,
  CreditCard,
} from "lucide-react";
import { useState } from "react";

const sidebarLinks = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { label: "Campaigns", href: "/dashboard/campaigns", icon: Send },
  { label: "Leads", href: "/dashboard/leads", icon: Users },
  { label: "Mailboxes", href: "/dashboard/mailboxes", icon: Mail },
  { label: "Inbox", href: "/dashboard/inbox", icon: MessageSquare },
  { label: "Templates", href: "/dashboard/templates", icon: Mail },
  { label: "Deliverability", href: "/dashboard/deliverability", icon: Shield },
  { label: "Warmup", href: "/dashboard/warmup", icon: Thermometer },
  { label: "CRM", href: "/dashboard/crm", icon: Briefcase },
  { label: "Automation", href: "/dashboard/automation", icon: Bot },
  { label: "Analytics", href: "/dashboard/analytics", icon: BarChart3 },
  { label: "Settings", href: "/dashboard/settings", icon: Settings },
];

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, router]);

  if (!isAuthenticated) return null;

  return (
    <div className="flex h-screen overflow-hidden">
      <aside
        className={`${
          sidebarOpen ? "w-64" : "w-16"
        } border-r bg-background transition-all duration-300 flex flex-col`}
      >
        <div className="p-4 flex items-center justify-between border-b">
          {sidebarOpen && (
            <Link href="/dashboard" className="text-xl font-bold text-primary">
              Openmailer
            </Link>
          )}
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            {sidebarOpen ? <ChevronLeft className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
        </div>
        <nav className="flex-1 overflow-y-auto p-2 space-y-1">
          {sidebarLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="flex items-center gap-3 px-3 py-2 rounded-md text-sm hover:bg-accent transition-colors"
            >
              <link.icon className="h-5 w-5 flex-shrink-0" />
              {sidebarOpen && <span>{link.label}</span>}
            </Link>
          ))}
        </nav>
      </aside>
      <main className="flex-1 overflow-y-auto bg-muted/30">
        <header className="h-16 border-b bg-background flex items-center justify-end px-6 gap-4">
          <Button variant="outline" size="sm" onClick={() => { useAuthStore.getState().logout(); router.push("/login"); }}>
            Logout
          </Button>
        </header>
        <div className="p-6">{children}</div>
      </main>
    </div>
  );
}
