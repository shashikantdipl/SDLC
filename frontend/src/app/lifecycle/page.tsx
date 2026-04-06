"use client";

import { motion } from "framer-motion";
import {
  FileText,
  Code2,
  TestTube2,
  Rocket,
  MonitorCheck,
  Bot,
  User,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface LifecycleStep {
  label: string;
  type: "auto" | "hitl";
  detail?: string;
}

interface LifecyclePhase {
  name: string;
  icon: React.ElementType;
  color: string;
  borderColor: string;
  iconColor: string;
  costEstimate: string;
  steps: LifecycleStep[];
}

const lifecyclePhases: LifecyclePhase[] = [
  {
    name: "Docs",
    icon: FileText,
    color: "bg-purple-500/10",
    borderColor: "border-purple-500/30",
    iconColor: "text-purple-400",
    costEstimate: "$1.80",
    steps: [
      { label: "Generate BRD from brief", type: "auto" },
      { label: "Review BRD & approve scope", type: "hitl", detail: "Stakeholder sign-off on business requirements" },
      { label: "Generate Roadmap + PRD + Architecture", type: "auto" },
      { label: "Review Architecture decisions", type: "hitl", detail: "Confirm tech stack, patterns, hosting" },
      { label: "Generate Feature Catalog + Quality + Security", type: "auto" },
      { label: "Generate Interaction Map + MCP + Design", type: "auto" },
      { label: "Generate Data Model + API Contracts", type: "auto" },
      { label: "Review API Contracts", type: "hitl", detail: "Confirm endpoints, auth, pagination" },
      { label: "Generate User Stories + Backlog + CLAUDE.md", type: "auto" },
      { label: "Generate Enforcement + Infra + Testing specs", type: "auto" },
      { label: "Generate Guardrails + Compliance Matrix", type: "auto" },
    ],
  },
  {
    name: "Code",
    icon: Code2,
    color: "bg-emerald-500/10",
    borderColor: "border-emerald-500/30",
    iconColor: "text-emerald-400",
    costEstimate: "$0.60",
    steps: [
      { label: "Scaffold project from specs", type: "auto" },
      { label: "Generate core business logic", type: "auto" },
      { label: "Code review by B1-code-reviewer", type: "auto" },
      { label: "Review code quality & patterns", type: "hitl", detail: "Spot-check generated code, fix edge cases" },
      { label: "Security audit by B3-security-auditor", type: "auto" },
      { label: "Performance analysis by B4", type: "auto" },
      { label: "Dependency audit by B7", type: "auto" },
      { label: "Review security findings", type: "hitl", detail: "Approve or reject flagged vulnerabilities" },
      { label: "Generate SQL migrations", type: "auto" },
    ],
  },
  {
    name: "Test",
    icon: TestTube2,
    color: "bg-yellow-500/10",
    borderColor: "border-yellow-500/30",
    iconColor: "text-yellow-400",
    costEstimate: "$0.30",
    steps: [
      { label: "Static analysis by T1", type: "auto" },
      { label: "Acceptance validation by T2", type: "auto" },
      { label: "Coverage gate check by T3", type: "auto" },
      { label: "Integration test run by T4", type: "auto" },
      { label: "Performance test by T5", type: "auto" },
      { label: "Review test results & coverage", type: "hitl", detail: "Approve coverage thresholds, review failures" },
    ],
  },
  {
    name: "Deploy",
    icon: Rocket,
    color: "bg-red-500/10",
    borderColor: "border-red-500/30",
    iconColor: "text-red-400",
    costEstimate: "$0.15",
    steps: [
      { label: "Deploy checklist by P1", type: "auto" },
      { label: "IaC review by P2-cdk-iac-reviewer", type: "auto" },
      { label: "Generate release notes by P3", type: "auto" },
      { label: "Approve deployment to production", type: "hitl", detail: "Final go/no-go before pushing to prod" },
      { label: "Configure rollback plan by P4", type: "auto" },
      { label: "Set feature flags by P5", type: "auto" },
    ],
  },
  {
    name: "Operate",
    icon: MonitorCheck,
    color: "bg-teal-500/10",
    borderColor: "border-teal-500/30",
    iconColor: "text-teal-400",
    costEstimate: "$0.10",
    steps: [
      { label: "Incident triage by O1", type: "auto" },
      { label: "Runbook execution by O2", type: "auto" },
      { label: "On-call summary by O3", type: "auto" },
      { label: "SLA monitoring by O4", type: "auto" },
      { label: "Alert management by O5", type: "auto" },
      { label: "Review incident reports & SLA status", type: "hitl", detail: "Weekly ops review, approve escalations" },
    ],
  },
];

export default function LifecyclePage() {
  const totalHitl = lifecyclePhases.reduce(
    (sum, phase) => sum + phase.steps.filter((s) => s.type === "hitl").length,
    0
  );
  const totalAuto = lifecyclePhases.reduce(
    (sum, phase) => sum + phase.steps.filter((s) => s.type === "auto").length,
    0
  );
  const totalSteps = totalHitl + totalAuto;

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">
          <span className="gradient-text">Lifecycle</span>
        </h1>
        <p className="text-muted-foreground mt-1">
          5 phases with human-in-the-loop checkpoints
        </p>
      </div>

      {/* Summary bar */}
      <div className="flex flex-wrap gap-4">
        <div className="glass-card px-4 py-3 flex items-center gap-2">
          <Bot className="w-4 h-4 text-blue-400" />
          <span className="text-sm font-medium">{totalAuto} automated steps</span>
        </div>
        <div className="glass-card px-4 py-3 flex items-center gap-2">
          <User className="w-4 h-4 text-amber-400" />
          <span className="text-sm font-medium">{totalHitl} HITL checkpoints</span>
        </div>
        <div className="glass-card px-4 py-3 flex items-center gap-2">
          <span className="text-sm text-muted-foreground">
            {Math.round((totalAuto / totalSteps) * 100)}% automated
          </span>
        </div>
      </div>

      {/* Phases */}
      <div className="space-y-6">
        {lifecyclePhases.map((phase, phaseIdx) => {
          const autoCount = phase.steps.filter((s) => s.type === "auto").length;
          const hitlCount = phase.steps.filter((s) => s.type === "hitl").length;

          return (
            <motion.div
              key={phase.name}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: phaseIdx * 0.1, duration: 0.4 }}
            >
              <Card className={`border ${phase.borderColor} bg-card/50 backdrop-blur-sm`}>
                <CardHeader>
                  <div className="flex items-center justify-between flex-wrap gap-2">
                    <CardTitle className="flex items-center gap-2 text-base">
                      <div className={`p-2 rounded-lg ${phase.color}`}>
                        <phase.icon className={`w-4 h-4 ${phase.iconColor}`} />
                      </div>
                      {phase.name}
                    </CardTitle>
                    <div className="flex items-center gap-3 text-xs">
                      <span className="text-muted-foreground">
                        {autoCount} auto / {hitlCount} HITL
                      </span>
                      <Badge className="bg-emerald-500/20 text-emerald-400 border-0 text-[10px]">
                        ~{phase.costEstimate}
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {phase.steps.map((step, stepIdx) => (
                      <div
                        key={stepIdx}
                        className={`flex items-start gap-3 p-2.5 rounded-lg transition-colors ${
                          step.type === "hitl"
                            ? "bg-amber-500/5 border border-amber-500/20"
                            : "hover:bg-muted/30"
                        }`}
                      >
                        <div className="shrink-0 mt-0.5">
                          {step.type === "auto" ? (
                            <Bot className="w-4 h-4 text-blue-400" />
                          ) : (
                            <User className="w-4 h-4 text-amber-400" />
                          )}
                        </div>
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-2">
                            <span className="text-sm">{step.label}</span>
                            {step.type === "hitl" && (
                              <Badge className="text-[10px] bg-amber-500/20 text-amber-400 border-0">
                                HITL
                              </Badge>
                            )}
                          </div>
                          {step.detail && (
                            <p className="text-xs text-muted-foreground mt-0.5">
                              {step.detail}
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          );
        })}
      </div>

      {/* Total HITL summary */}
      <div className="gradient-border p-6">
        <h3 className="text-lg font-semibold mb-4">HITL Checkpoint Summary</h3>
        <div className="grid sm:grid-cols-2 gap-3">
          {lifecyclePhases.flatMap((phase) =>
            phase.steps
              .filter((s) => s.type === "hitl")
              .map((s, i) => (
                <div
                  key={`${phase.name}-${i}`}
                  className="flex items-center gap-2 p-2 rounded-lg bg-amber-500/5 border border-amber-500/10"
                >
                  <User className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                  <span className="text-xs">{s.label}</span>
                  <Badge className={`ml-auto text-[9px] border-0 ${
                    phaseColors(phase.name)
                  }`}>
                    {phase.name}
                  </Badge>
                </div>
              ))
          )}
        </div>
        <div className="mt-4 pt-4 border-t border-border/50 flex items-center justify-between text-sm">
          <span className="text-muted-foreground">
            Total estimated cost per pipeline run
          </span>
          <span className="text-2xl font-bold gradient-text">~$2.95</span>
        </div>
      </div>
    </div>
  );
}

function phaseColors(name: string): string {
  const map: Record<string, string> = {
    Docs: "bg-purple-500/20 text-purple-400",
    Code: "bg-emerald-500/20 text-emerald-400",
    Test: "bg-yellow-500/20 text-yellow-400",
    Deploy: "bg-red-500/20 text-red-400",
    Operate: "bg-teal-500/20 text-teal-400",
  };
  return map[name] || "bg-muted text-muted-foreground";
}
