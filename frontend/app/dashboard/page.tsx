"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Plus, TrendingUp, Mail, Users, Send, BarChart3, Target, Activity } from "lucide-react";
import Link from "next/link";

const stats = [
  { label: "Total Leads", value: "0", icon: Users, color: "text-blue-600" },
  { label: "Active Campaigns", value: "0", icon: Send, color: "text-green-600" },
  { label: "Mailboxes", value: "0", icon: Mail, color: "text-purple-600" },
  { label: "Open Rate", value: "0%", icon: Activity, color: "text-orange-600" },
  { label: "Reply Rate", value: "0%", icon: MessageSquare, color: "text-pink-600" },
  { label: "Deliverability", value: "100", icon: Target, color: "text-cyan-600" },
];

import { MessageSquare } from "lucide-react";

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">Welcome to Openmailer</p>
        </div>
        <Link href="/dashboard/campaigns/new">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            New Campaign
          </Button>
        </Link>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        {stats.map((stat) => (
          <Card key={stat.label}>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <stat.icon className={`h-5 w-5 ${stat.color}`} />
              </div>
              <div className="mt-3">
                <p className="text-2xl font-bold">{stat.value}</p>
                <p className="text-xs text-muted-foreground">{stat.label}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-2">
            <Link href="/dashboard/campaigns/new">
              <Button variant="outline" className="w-full justify-start">
                <Send className="mr-2 h-4 w-4" /> Create Campaign
              </Button>
            </Link>
            <Link href="/dashboard/leads/import">
              <Button variant="outline" className="w-full justify-start">
                <Users className="mr-2 h-4 w-4" /> Import Leads
              </Button>
            </Link>
            <Link href="/dashboard/mailboxes/connect">
              <Button variant="outline" className="w-full justify-start">
                <Mail className="mr-2 h-4 w-4" /> Connect Mailbox
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-center h-32 text-muted-foreground">
              <p className="text-sm">No recent activity</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
