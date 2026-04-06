"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  Rocket,
  FileText,
  CheckCircle2,
  Circle,
  Loader2,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

interface PipelineStep {
  step: number;
  agentId: string;
  document: string;
  phase: string;
  parallel?: string;
}

const pipelineSteps: PipelineStep[] = [
  { step: 0,  agentId: "D0-brd-generator",            document: "00-BRD",                phase: "discovery" },
  { step: 1,  agentId: "D1-roadmap-generator",         document: "01-ROADMAP",            phase: "foundations" },
  { step: 2,  agentId: "D2-prd-generator",             document: "02-PRD",                phase: "foundations" },
  { step: 3,  agentId: "D3-architecture-drafter",      document: "03-ARCH",               phase: "foundations" },
  { step: 4,  agentId: "D4-feature-extractor",         document: "04-FEATURE-CATALOG",    phase: "decomposition" },
  { step: 5,  agentId: "D5-quality-spec-generator",    document: "05-QUALITY",            phase: "decomposition" },
  { step: 6,  agentId: "D6-security-architect",        document: "06-SECURITY-ARCH",      phase: "decomposition" },
  { step: 7,  agentId: "D7-interaction-map-generator",  document: "07-INTERACTION-MAP",    phase: "interface" },
  { step: 8,  agentId: "D8-mcp-tool-spec-writer",      document: "08-MCP-TOOL-SPEC",      phase: "interface", parallel: "8-9" },
  { step: 9,  agentId: "D9-design-spec-writer",        document: "09-DESIGN-SPEC",        phase: "interface", parallel: "8-9" },
  { step: 10, agentId: "D10-data-model-designer",      document: "10-DATA-MODEL",         phase: "data" },
  { step: 11, agentId: "D11-api-contract-generator",   document: "11-API-CONTRACTS",      phase: "data" },
  { step: 12, agentId: "D12-user-story-writer",        document: "12-USER-STORIES",       phase: "data" },
  { step: 13, agentId: "D13-backlog-builder",          document: "13-BACKLOG",            phase: "data" },
  { step: 14, agentId: "D14-claude-md-generator",      document: "14-CLAUDE.md",          phase: "data" },
  { step: 15, agentId: "D15-enforcement-scaffolder",   document: "15-ENFORCEMENT",        phase: "data" },
  { step: 16, agentId: "D16-infra-designer",           document: "16-INFRA-DESIGN",       phase: "operations" },
  { step: 17, agentId: "D17-migration-planner",        document: "17-MIGRATION-PLAN",     phase: "operations", parallel: "17-18" },
  { step: 18, agentId: "D18-test-strategy-generator",  document: "18-TESTING",            phase: "operations", parallel: "17-18" },
  { step: 19, agentId: "D19-fault-tolerance-planner",  document: "19-FAULT-TOLERANCE",    phase: "operations" },
  { step: 20, agentId: "D20-guardrails-spec-writer",   document: "20-GUARDRAILS-SPEC",    phase: "operations" },
  { step: 21, agentId: "D21-compliance-matrix-writer", document: "21-COMPLIANCE-MATRIX",  phase: "operations" },
];

const phaseColors: Record<string, string> = {
  discovery:     "bg-pink-500/20 text-pink-400",
  foundations:   "bg-blue-500/20 text-blue-400",
  decomposition: "bg-purple-500/20 text-purple-400",
  interface:     "bg-cyan-500/20 text-cyan-400",
  data:          "bg-emerald-500/20 text-emerald-400",
  operations:    "bg-orange-500/20 text-orange-400",
};

const phaseLineColors: Record<string, string> = {
  discovery:     "bg-pink-500",
  foundations:   "bg-blue-500",
  decomposition: "bg-purple-500",
  interface:     "bg-cyan-500",
  data:          "bg-emerald-500",
  operations:    "bg-orange-500",
};

export default function PipelinePage() {
  const [projectName, setProjectName] = useState("");
  const [brief, setBrief] = useState("");
  const [provider, setProvider] = useState("anthropic");
  const [running, setRunning] = useState(false);

  function handleRun() {
    if (!projectName.trim() || !brief.trim()) return;
    setRunning(true);
    // Simulated -- in production this would call the real pipeline API
    setTimeout(() => setRunning(false), 3000);
  }

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">
          <span className="gradient-text">Pipeline</span>
        </h1>
        <p className="text-muted-foreground mt-1">
          22-step document generation pipeline
        </p>
      </div>

      {/* Launch form */}
      <Card className="bg-card/50 backdrop-blur-sm border-blue-500/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Rocket className="w-4 h-4 text-blue-400" />
            Launch Pipeline
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid sm:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-xs font-medium text-muted-foreground">
                Project Name
              </label>
              <Input
                placeholder="My SaaS App"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                className="bg-background/50"
              />
            </div>
            <div className="space-y-2">
              <label className="text-xs font-medium text-muted-foreground">
                LLM Provider
              </label>
              <select
                value={provider}
                onChange={(e) => setProvider(e.target.value)}
                className="flex h-8 w-full rounded-lg border border-input bg-background/50 px-3 py-1 text-sm text-foreground shadow-xs outline-none focus:border-ring focus:ring-3 focus:ring-ring/50"
              >
                <option value="anthropic">Anthropic (Claude)</option>
                <option value="openai">OpenAI (GPT)</option>
                <option value="ollama">Ollama (Local)</option>
              </select>
            </div>
          </div>
          <div className="space-y-2">
            <label className="text-xs font-medium text-muted-foreground">
              Project Brief
            </label>
            <Textarea
              placeholder="Describe your application in plain text. What does it do, who uses it, what problem does it solve..."
              value={brief}
              onChange={(e) => setBrief(e.target.value)}
              rows={4}
              className="bg-background/50 resize-none"
            />
          </div>
          <Button
            onClick={handleRun}
            disabled={running || !projectName.trim() || !brief.trim()}
            className="bg-gradient-to-r from-blue-600 to-purple-600 text-white border-0 hover:from-blue-500 hover:to-purple-500"
            size="lg"
          >
            {running ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Running Pipeline...
              </>
            ) : (
              <>
                <Rocket className="w-4 h-4" />
                Run Pipeline
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Timeline */}
      <div className="space-y-1">
        <h2 className="text-lg font-semibold mb-4">Pipeline Steps</h2>
        <div className="relative">
          {pipelineSteps.map((step, i) => {
            const colors = phaseColors[step.phase] || phaseColors.foundations;
            const lineColor = phaseLineColors[step.phase] || "bg-blue-500";
            const isLast = i === pipelineSteps.length - 1;

            return (
              <motion.div
                key={step.step}
                initial={{ opacity: 0, x: -12 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.04, duration: 0.3 }}
                className="flex gap-4 relative"
              >
                {/* Timeline line and dot */}
                <div className="flex flex-col items-center shrink-0 w-8">
                  <div className={`w-3 h-3 rounded-full ${lineColor} ring-4 ring-background z-10 mt-4`} />
                  {!isLast && (
                    <div className="w-px flex-1 bg-border" />
                  )}
                </div>

                {/* Content */}
                <div className="pb-4 flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-xs font-mono text-muted-foreground w-6">
                      {String(step.step).padStart(2, "0")}
                    </span>
                    <FileText className="w-3.5 h-3.5 text-muted-foreground" />
                    <span className="text-sm font-medium truncate">
                      {step.document}
                    </span>
                    <Badge className={`text-[10px] border-0 ${colors}`}>
                      {step.phase}
                    </Badge>
                    {step.parallel && (
                      <Badge className="text-[10px] bg-amber-500/20 text-amber-400 border-0">
                        parallel
                      </Badge>
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground mt-0.5 ml-6 truncate">
                    {step.agentId}
                  </p>
                </div>

                {/* Status */}
                <div className="shrink-0 mt-3.5">
                  <Circle className="w-4 h-4 text-muted-foreground/40" />
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
