import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

// SDLC project root is two levels up from the frontend directory
const PROJECT_ROOT = path.resolve(process.cwd(), "..");

interface AgentInfo {
  id: string;
  name: string;
  description: string;
  phase: string;
  tier: string;
  autonomy: string;
  tags: string[];
}

function parseManifestYaml(content: string): Partial<AgentInfo> {
  const result: Partial<AgentInfo> = {};

  const idMatch = content.match(/^\s*id:\s*(.+)$/m);
  if (idMatch) result.id = idMatch[1].trim();

  const nameMatch = content.match(/^\s*name:\s*(.+)$/m);
  if (nameMatch) result.name = nameMatch[1].trim().replace(/^["']|["']$/g, "");

  const descMatch = content.match(/^\s*description:\s*(.+)$/m);
  if (descMatch) result.description = descMatch[1].trim().replace(/^["']|["']$/g, "");

  const phaseMatch = content.match(/^\s*phase:\s*(.+)$/m);
  if (phaseMatch) result.phase = phaseMatch[1].trim();

  const tierMatch = content.match(/^\s*tier:\s*(.+)$/m);
  if (tierMatch) result.tier = tierMatch[1].trim();

  const autonomyMatch = content.match(/^\s*autonomy_tier:\s*(.+)$/m);
  if (autonomyMatch) result.autonomy = autonomyMatch[1].trim();

  const tagsMatch = content.match(/^\s*tags:\s*\[([^\]]*)\]/m);
  if (tagsMatch) {
    result.tags = tagsMatch[1].split(",").map((t) => t.trim().replace(/^["']|["']$/g, ""));
  }

  return result;
}

function scanAgents(): AgentInfo[] {
  const agentsDir = path.join(PROJECT_ROOT, "agents");
  const agents: AgentInfo[] = [];

  if (!fs.existsSync(agentsDir)) return agents;

  const phases = fs.readdirSync(agentsDir).filter((d) => {
    const full = path.join(agentsDir, d);
    return fs.statSync(full).isDirectory() && !d.startsWith("__");
  });

  for (const phase of phases) {
    const phaseDir = path.join(agentsDir, phase);
    const agentDirs = fs.readdirSync(phaseDir).filter((d) => {
      const full = path.join(phaseDir, d);
      return fs.statSync(full).isDirectory() && !d.startsWith("__");
    });

    for (const agentDir of agentDirs) {
      const manifestPath = path.join(phaseDir, agentDir, "manifest.yaml");
      if (fs.existsSync(manifestPath)) {
        try {
          const content = fs.readFileSync(manifestPath, "utf-8");
          const parsed = parseManifestYaml(content);
          agents.push({
            id: parsed.id || agentDir,
            name: parsed.name || agentDir,
            description: parsed.description || "",
            phase: parsed.phase || phase,
            tier: parsed.tier || "balanced",
            autonomy: parsed.autonomy || "T0",
            tags: parsed.tags || [],
          });
        } catch {
          agents.push({
            id: agentDir,
            name: agentDir,
            description: "",
            phase,
            tier: "balanced",
            autonomy: "T0",
            tags: [],
          });
        }
      }
    }
  }

  return agents;
}

function scanDocuments(): { name: string; number: string }[] {
  const docsDir = path.join(PROJECT_ROOT, "Generated-Docs");
  if (!fs.existsSync(docsDir)) return [];

  return fs
    .readdirSync(docsDir)
    .filter((f) => f.endsWith(".md"))
    .sort()
    .map((f) => {
      const match = f.match(/^(\d+)-(.+)\.md$/);
      return {
        name: match ? match[2] : f.replace(".md", ""),
        number: match ? match[1] : "??",
      };
    });
}

function countFiles(dir: string, ext?: string): number {
  const fullDir = path.join(PROJECT_ROOT, dir);
  if (!fs.existsSync(fullDir)) return 0;
  const files = fs.readdirSync(fullDir);
  if (ext) return files.filter((f) => f.endsWith(ext)).length;
  return files.filter((f) => !f.startsWith("__")).length;
}

export async function GET() {
  try {
    const agents = scanAgents();
    const documents = scanDocuments();

    const phaseCounts: Record<string, number> = {};
    for (const agent of agents) {
      const p = agent.phase.toLowerCase();
      phaseCounts[p] = (phaseCounts[p] || 0) + 1;
    }

    return NextResponse.json({
      agents,
      documents,
      phase_counts: phaseCounts,
      metrics: {
        total_agents: agents.length,
        total_documents: documents.length,
        total_services: countFiles("services", ".py"),
        total_migrations: countFiles("migrations", ".sql"),
      },
    });
  } catch (error) {
    return NextResponse.json(
      { error: "Failed to scan project", detail: String(error) },
      { status: 500 }
    );
  }
}
