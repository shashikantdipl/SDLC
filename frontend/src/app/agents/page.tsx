"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Bot, Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";

interface Agent {
  id: string;
  name: string;
  description: string;
  phase: string;
  tier: string;
  autonomy: string;
  tags: string[];
}

const phaseColors: Record<string, { badge: string; border: string; icon: string }> = {
  govern:    { badge: "bg-blue-500/20 text-blue-400",    border: "border-blue-500/30",   icon: "text-blue-400" },
  design:    { badge: "bg-purple-500/20 text-purple-400", border: "border-purple-500/30", icon: "text-purple-400" },
  build:     { badge: "bg-emerald-500/20 text-emerald-400", border: "border-emerald-500/30", icon: "text-emerald-400" },
  test:      { badge: "bg-yellow-500/20 text-yellow-400", border: "border-yellow-500/30", icon: "text-yellow-400" },
  deploy:    { badge: "bg-red-500/20 text-red-400",      border: "border-red-500/30",     icon: "text-red-400" },
  operate:   { badge: "bg-teal-500/20 text-teal-400",    border: "border-teal-500/30",    icon: "text-teal-400" },
  oversight: { badge: "bg-orange-500/20 text-orange-400", border: "border-orange-500/30", icon: "text-orange-400" },
};

const tierColors: Record<string, string> = {
  fast: "bg-green-500/20 text-green-400",
  balanced: "bg-blue-500/20 text-blue-400",
  powerful: "bg-purple-500/20 text-purple-400",
};

const PHASE_TABS = ["all", "govern", "design", "build", "test", "deploy", "operate", "oversight"];

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("all");

  useEffect(() => {
    fetch("/api/project")
      .then((r) => r.json())
      .then((data) => {
        setAgents(data.agents || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const filtered =
    activeTab === "all"
      ? agents
      : agents.filter((a) => a.phase.toLowerCase() === activeTab);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">
          <span className="gradient-text">AI Agents</span>
        </h1>
        <p className="text-muted-foreground mt-1">
          {agents.length} agents across 7 SDLC phases
        </p>
      </div>

      <Tabs defaultValue="all" onValueChange={(v) => setActiveTab(v)}>
        <TabsList variant="line" className="flex-wrap">
          {PHASE_TABS.map((tab) => (
            <TabsTrigger key={tab} value={tab} className="capitalize">
              {tab}
              {tab !== "all" && (
                <span className="ml-1.5 text-xs text-muted-foreground">
                  {agents.filter((a) => a.phase.toLowerCase() === tab).length}
                </span>
              )}
            </TabsTrigger>
          ))}
        </TabsList>

        {PHASE_TABS.map((tab) => (
          <TabsContent key={tab} value={tab}>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.3 }}
              className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 mt-4"
            >
              {(tab === "all"
                ? agents
                : agents.filter((a) => a.phase.toLowerCase() === tab)
              ).map((agent, i) => {
                const colors = phaseColors[agent.phase.toLowerCase()] || phaseColors.govern;
                return (
                  <motion.div
                    key={agent.id}
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.03, duration: 0.3 }}
                  >
                    <Card className={`border ${colors.border} bg-card/50 backdrop-blur-sm hover:bg-card/80 transition-colors`}>
                      <CardHeader className="pb-2">
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex items-center gap-2 min-w-0">
                            <Bot className={`w-4 h-4 shrink-0 ${colors.icon}`} />
                            <CardTitle className="text-sm truncate">{agent.name}</CardTitle>
                          </div>
                          <Badge className={`shrink-0 text-[10px] ${colors.badge} border-0`}>
                            {agent.phase.toUpperCase()}
                          </Badge>
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <p className="text-xs text-muted-foreground line-clamp-2 min-h-[2rem]">
                          {agent.description || "No description available"}
                        </p>
                        <div className="flex items-center gap-2 flex-wrap">
                          <Badge className={`text-[10px] border-0 ${tierColors[agent.tier] || tierColors.balanced}`}>
                            {agent.tier}
                          </Badge>
                          <Badge className="text-[10px] bg-slate-500/20 text-slate-400 border-0">
                            {agent.autonomy}
                          </Badge>
                        </div>
                        {agent.tags.length > 0 && (
                          <div className="flex flex-wrap gap-1">
                            {agent.tags.slice(0, 4).map((tag) => (
                              <span
                                key={tag}
                                className="text-[10px] px-1.5 py-0.5 rounded-md bg-muted text-muted-foreground"
                              >
                                {tag}
                              </span>
                            ))}
                            {agent.tags.length > 4 && (
                              <span className="text-[10px] text-muted-foreground">
                                +{agent.tags.length - 4}
                              </span>
                            )}
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  </motion.div>
                );
              })}
            </motion.div>
            {filtered.length === 0 && tab !== "all" && (
              <p className="text-center text-muted-foreground py-12">
                No agents found in this phase.
              </p>
            )}
          </TabsContent>
        ))}
      </Tabs>
    </div>
  );
}
