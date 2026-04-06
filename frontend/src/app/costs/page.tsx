"use client";

import { motion } from "framer-motion";
import {
  DollarSign,
  TrendingDown,
  Zap,
  Server,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const costBreakdown = [
  { phase: "DESIGN", agents: 22, avgCost: "$0.08", totalCost: "$1.80", color: "bg-purple-500", pct: 60 },
  { phase: "BUILD", agents: 9, avgCost: "$0.07", totalCost: "$0.60", color: "bg-emerald-500", pct: 20 },
  { phase: "TEST", agents: 5, avgCost: "$0.06", totalCost: "$0.30", color: "bg-yellow-500", pct: 10 },
  { phase: "DEPLOY", agents: 5, avgCost: "$0.03", totalCost: "$0.15", color: "bg-red-500", pct: 5 },
  { phase: "OPERATE", agents: 5, avgCost: "$0.02", totalCost: "$0.10", color: "bg-teal-500", pct: 3 },
  { phase: "GOVERN", agents: 5, avgCost: "$0.01", totalCost: "$0.05", color: "bg-blue-500", pct: 1.5 },
  { phase: "OVERSIGHT", agents: 10, avgCost: "$0.01", totalCost: "$0.10", color: "bg-orange-500", pct: 3 },
];

const providerPricing = [
  { provider: "Anthropic (Claude)", model: "Haiku/Sonnet", costPerRun: "~$3.00", speed: "35 min", recommended: true },
  { provider: "OpenAI (GPT)", model: "GPT-4o-mini/4o", costPerRun: "~$3.50", speed: "40 min", recommended: false },
  { provider: "Ollama (Local)", model: "Llama 3 / Mistral", costPerRun: "$0.00", speed: "60+ min", recommended: false },
];

export default function CostsPage() {
  return (
    <div className="p-6 max-w-5xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">
          <span className="gradient-text">Cost Breakdown</span>
        </h1>
        <p className="text-muted-foreground mt-1">
          Per-pipeline cost estimates by phase and provider
        </p>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: "Total Per Run", value: "~$3", icon: DollarSign, color: "from-blue-500 to-cyan-400" },
          { label: "Avg Per Agent", value: "$0.05", icon: TrendingDown, color: "from-emerald-500 to-teal-400" },
          { label: "61 Agents", value: "7 phases", icon: Zap, color: "from-purple-500 to-pink-400" },
          { label: "LLM Agnostic", value: "3 providers", icon: Server, color: "from-amber-500 to-orange-400" },
        ].map((stat) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
          >
            <div className="glass-card p-6 text-center">
              <div className={`inline-flex p-3 rounded-xl bg-gradient-to-br ${stat.color} mb-3`}>
                <stat.icon className="w-5 h-5 text-white" />
              </div>
              <div className="text-2xl font-bold text-white">{stat.value}</div>
              <div className="text-xs text-muted-foreground mt-1">{stat.label}</div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Phase breakdown */}
      <Card className="bg-card/50 backdrop-blur-sm border-blue-500/20">
        <CardHeader>
          <CardTitle className="text-base">Cost by Phase</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {costBreakdown.map((item, i) => (
            <motion.div
              key={item.phase}
              initial={{ opacity: 0, x: -12 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05, duration: 0.3 }}
              className="space-y-1.5"
            >
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <div className={`w-2.5 h-2.5 rounded-full ${item.color}`} />
                  <span className="font-medium">{item.phase}</span>
                  <span className="text-xs text-muted-foreground">
                    {item.agents} agents
                  </span>
                </div>
                <div className="flex items-center gap-3 text-xs">
                  <span className="text-muted-foreground">avg {item.avgCost}/agent</span>
                  <span className="font-semibold text-foreground">{item.totalCost}</span>
                </div>
              </div>
              <div className="progress-track">
                <motion.div
                  className="progress-fill"
                  initial={{ width: 0 }}
                  animate={{ width: `${item.pct}%` }}
                  transition={{ delay: 0.3 + i * 0.05, duration: 0.6 }}
                />
              </div>
            </motion.div>
          ))}
        </CardContent>
      </Card>

      {/* Provider comparison */}
      <Card className="bg-card/50 backdrop-blur-sm border-purple-500/20">
        <CardHeader>
          <CardTitle className="text-base">Provider Comparison</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {providerPricing.map((p) => (
              <div
                key={p.provider}
                className={`flex items-center justify-between p-3 rounded-lg border ${
                  p.recommended
                    ? "border-blue-500/30 bg-blue-500/5"
                    : "border-border/50 bg-muted/20"
                }`}
              >
                <div className="space-y-0.5">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium">{p.provider}</span>
                    {p.recommended && (
                      <Badge className="text-[10px] bg-blue-500/20 text-blue-400 border-0">
                        Recommended
                      </Badge>
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground">{p.model}</p>
                </div>
                <div className="text-right space-y-0.5">
                  <div className="text-sm font-semibold">{p.costPerRun}</div>
                  <div className="text-xs text-muted-foreground">{p.speed}</div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Cost note */}
      <div className="text-center text-xs text-muted-foreground pb-6">
        Estimates based on Claude Haiku for fast-tier and Sonnet for balanced/powerful-tier agents.
        Actual costs depend on input/output token counts and provider pricing.
      </div>
    </div>
  );
}
