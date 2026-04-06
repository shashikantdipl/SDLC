"use client";

import { motion } from "framer-motion";
import {
  Bot, FileText, Layers, DollarSign, Shield, Zap, Eye,
  Rocket, ArrowRight, Sparkles, Terminal, GitBranch
} from "lucide-react";

const stats = [
  { label: "AI Agents", value: "61", icon: Bot, color: "from-blue-500 to-cyan-400" },
  { label: "Documents", value: "24", icon: FileText, color: "from-purple-500 to-pink-400" },
  { label: "SDLC Phases", value: "7", icon: Layers, color: "from-emerald-500 to-teal-400" },
  { label: "Per Pipeline", value: "$3", icon: DollarSign, color: "from-amber-500 to-orange-400" },
];

const phases = [
  { name: "GOVERN", agents: 5, icon: Shield, color: "border-blue-500/20", iconColor: "text-blue-400", bg: "bg-blue-500/10", desc: "Cost, audit, lifecycle" },
  { name: "DESIGN", agents: 22, icon: FileText, color: "border-purple-500/20", iconColor: "text-purple-400", bg: "bg-purple-500/10", desc: "24-doc pipeline" },
  { name: "BUILD", agents: 9, icon: Terminal, color: "border-emerald-500/20", iconColor: "text-emerald-400", bg: "bg-emerald-500/10", desc: "Code, test, security" },
  { name: "TEST", agents: 5, icon: Zap, color: "border-yellow-500/20", iconColor: "text-yellow-400", bg: "bg-yellow-500/10", desc: "Coverage, integration" },
  { name: "DEPLOY", agents: 5, icon: Rocket, color: "border-red-500/20", iconColor: "text-red-400", bg: "bg-red-500/10", desc: "Checklist, rollback" },
  { name: "OPERATE", agents: 5, icon: Eye, color: "border-teal-500/20", iconColor: "text-teal-400", bg: "bg-teal-500/10", desc: "Incidents, SLA" },
  { name: "OVERSIGHT", agents: 10, icon: GitBranch, color: "border-orange-500/20", iconColor: "text-orange-400", bg: "bg-orange-500/10", desc: "Audits, compliance" },
];

const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.1 } },
};
const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.5, ease: "easeOut" as const } },
};

export default function Home() {
  return (
    <div className="min-h-screen relative">
      {/* Ambient glow */}
      <div className="fixed top-0 left-1/2 -translate-x-1/2 w-[800px] h-[600px] bg-blue-500/5 rounded-full blur-[120px] pointer-events-none" />
      <div className="fixed bottom-0 right-0 w-[600px] h-[400px] bg-purple-500/5 rounded-full blur-[100px] pointer-events-none" />

      <div className="relative z-10 max-w-7xl mx-auto px-6 py-16">
        {/* Hero */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="text-center mb-20"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm font-medium mb-8">
            <Sparkles className="w-4 h-4" />
            AI-Native App Development Platform
          </div>

          <h1 className="text-6xl md:text-8xl font-extrabold tracking-tight mb-6">
            <span className="gradient-text">Agentic SDLC</span>
          </h1>

          <p className="text-xl md:text-2xl text-slate-400 max-w-3xl mx-auto mb-10 leading-relaxed">
            One brief. 61 AI agents. 24 documents.
            <br />
            Complete app specification in <span className="text-white font-semibold">35 minutes</span> for <span className="text-emerald-400 font-semibold">$3</span>.
          </p>

          <div className="flex items-center justify-center gap-4 flex-wrap">
            <a
              href="/pipeline"
              className="inline-flex items-center gap-2 px-8 py-4 rounded-2xl bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-bold text-lg transition-all hover:shadow-xl hover:shadow-blue-500/25 hover:-translate-y-1"
            >
              <Rocket className="w-5 h-5" />
              Launch Pipeline
              <ArrowRight className="w-5 h-5" />
            </a>
            <a
              href="/agents"
              className="inline-flex items-center gap-2 px-8 py-4 rounded-2xl bg-slate-800/50 hover:bg-slate-700/50 text-slate-300 font-bold text-lg border border-slate-700/50 transition-all hover:-translate-y-1 backdrop-blur-sm"
            >
              <Bot className="w-5 h-5" />
              View All 61 Agents
            </a>
          </div>
        </motion.div>

        {/* Stats */}
        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
          className="grid grid-cols-2 md:grid-cols-4 gap-5 mb-20"
        >
          {stats.map((stat) => (
            <motion.div key={stat.label} variants={fadeUp}>
              <div className="glass-card p-8 text-center group cursor-default">
                <div className={`inline-flex p-4 rounded-2xl bg-gradient-to-br ${stat.color} mb-5 shadow-lg`}>
                  <stat.icon className="w-7 h-7 text-white" />
                </div>
                <div className="text-4xl font-extrabold text-white mb-2">{stat.value}</div>
                <div className="text-sm text-slate-400 font-medium">{stat.label}</div>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* How it works */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mb-20"
        >
          <h2 className="text-3xl font-bold text-center mb-12">
            <span className="gradient-text">How It Works</span>
          </h2>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              { step: "01", title: "Write a Brief", desc: "Describe your app in plain text. What it does, who uses it, what problem it solves.", icon: FileText, iconColor: "text-blue-400", bg: "bg-blue-500/10", border: "border-blue-500/20" },
              { step: "02", title: "Pipeline Runs", desc: "22 AI agents generate 24 specification documents. Architecture, API, security, tests — everything.", icon: Zap, iconColor: "text-purple-400", bg: "bg-purple-500/10", border: "border-purple-500/20" },
              { step: "03", title: "Build & Deploy", desc: "Claude Code writes the entire app from specs. You review at 9 HITL checkpoints and deploy.", icon: Rocket, iconColor: "text-emerald-400", bg: "bg-emerald-500/10", border: "border-emerald-500/20" },
            ].map((s) => (
              <div key={s.step} className="glass-card p-10 relative overflow-hidden group">
                <div className="absolute -top-4 -right-2 text-[8rem] font-black text-white/[0.02] group-hover:text-white/[0.04] transition-colors">{s.step}</div>
                <div className={`inline-flex p-4 rounded-2xl ${s.bg} border ${s.border} mb-6`}>
                  <s.icon className={`w-7 h-7 ${s.iconColor}`} />
                </div>
                <h3 className="text-xl font-bold text-white mb-3">{s.title}</h3>
                <p className="text-slate-400 leading-relaxed">{s.desc}</p>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Phases */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.7 }}
          className="mb-20"
        >
          <h2 className="text-3xl font-bold text-center mb-12">
            <span className="gradient-text">7 SDLC Phases</span>
          </h2>

          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
            {phases.map((phase, i) => (
              <motion.div
                key={phase.name}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.8 + i * 0.06 }}
              >
                <div className={`glass-card p-6 text-center border ${phase.color} group cursor-default`}>
                  <div className={`inline-flex p-3 rounded-xl ${phase.bg} mb-3`}>
                    <phase.icon className={`w-6 h-6 ${phase.iconColor}`} />
                  </div>
                  <div className={`text-xs font-bold tracking-widest mb-2 ${phase.iconColor}`}>{phase.name}</div>
                  <div className="text-3xl font-extrabold text-white mb-1">{phase.agents}</div>
                  <div className="text-xs text-slate-500">{phase.desc}</div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Cost banner */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1 }}
        >
          <div className="gradient-border p-12 text-center">
            <h3 className="text-xl font-semibold text-slate-300 mb-4">Complete App Specification</h3>
            <div className="text-6xl md:text-7xl font-black gradient-text mb-4">~$3</div>
            <p className="text-slate-500 text-lg max-w-lg mx-auto">
              24 documents · 35 minutes · LLM-agnostic
            </p>
            <div className="flex items-center justify-center gap-6 mt-6 text-sm text-slate-500">
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-blue-500"></span>Anthropic</span>
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-emerald-500"></span>OpenAI</span>
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-orange-500"></span>Ollama</span>
            </div>
          </div>
        </motion.div>

        {/* Footer */}
        <div className="mt-20 text-center text-slate-600 text-sm">
          <p>Agentic SDLC Platform v1.0 · 61 agents · 7 phases · Full-Stack-First</p>
        </div>
      </div>
    </div>
  );
}
