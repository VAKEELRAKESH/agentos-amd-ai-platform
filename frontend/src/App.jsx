import { useEffect, useMemo, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  Activity,
  CheckCircle2,
  Copy,
  Database,
  Layers3,
  Play,
  RefreshCw,
  Rocket,
  ShieldCheck,
  Sparkles,
  Zap
} from "lucide-react";
import "./App.css";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8002/api/v1";
const DEMO_MODE = String(import.meta.env.VITE_DEMO_MODE).toLowerCase() === "true";

const tabs = [
  { key: "result", label: "Answer", icon: Rocket },
  { key: "plan", label: "Plan", icon: Layers3 },
  { key: "research", label: "Research", icon: Sparkles },
  { key: "validation", label: "Validation", icon: ShieldCheck },
  { key: "memory", label: "Memory", icon: Database }
];

const modelOptions = [
  { value: "amd-vllm", label: "AMD vLLM", mode: "active" },
  { value: "mistral-7b", label: "Mistral 7B", mode: "active" },
  { value: "llama", label: "Llama", mode: "planned" },
  { value: "qwen", label: "Qwen", mode: "planned" },
  { value: "demo", label: "Demo", mode: "demo" }
];

const workflowOptions = [
  { value: "general", label: "General Agent Workflow" },
  { value: "research", label: "Research Agent" },
  { value: "code", label: "Code / Execution Agent" },
  { value: "validation", label: "Validation Agent" },
  { value: "product-demo", label: "Product Demo Agent" },
  { value: "submission", label: "Hackathon Submission Agent" }
];


const workflowModes = [
  {
    key: "general",
    label: "General Agent",
    prefix: ""
  },
  {
    key: "research",
    label: "Research Agent",
    prefix: "Act as the Senior Research Analyst. Focus on evidence, comparison, risks, and clear findings."
  },
  {
    key: "code",
    label: "Code Agent",
    prefix: "Act as the Code and Execution Agent. Focus on implementation steps, code actions, debugging, and practical completion."
  },
  {
    key: "validation",
    label: "Validation Agent",
    prefix: "Act as the Quality Assurance Validator. Review correctness, gaps, risks, and readiness."
  },
  {
    key: "product-demo",
    label: "Product Demo",
    prefix: "Act as the Product Demo Agent. Create concise demo messaging, product flow, and value explanation."
  },
  {
    key: "submission",
    label: "Submission Agent",
    prefix: "Act as the Hackathon Submission Agent. Create submission-ready content, judging alignment, demo flow, and impact summary."
  }
];


const demoResult = {
  workflow_id: "demo-ops-01",
  task: "Demo workflow task",
  plan: "1. Confirm runtime status.\n2. Run one focused workflow.\n3. Inspect plan, execution, validation, and memory.\n4. Decide whether the output is ready or needs revision.",
  research: "Research is skipped for this interface validation run. For current-information tasks, the research agent can use available tools.",
  result: "AgentOS is ready as a focused AI agent operations workspace. It can launch multi-agent workflows, inspect execution quality, validate outputs, and preserve useful context through semantic memory.",
  validation: "The workflow output is clear, structured, and suitable for demo review.\n\nPASS_WITH_NOTES",
  quality_verdict: "PASS_WITH_NOTES",
  status: "completed",
  duration_seconds: 4.2,
  recalled_context: [
    {
      memory_id: "demo-memory-01",
      similarity: 0.74,
      metadata: { task: "Previous AMD AI platform validation workflow" },
      snippet: "Prior validation confirmed backend health, runtime routing, and workflow persistence."
    }
  ]
};

const particles = Array.from({ length: 70 }, (_, i) => ({
  id: i,
  left: `${(i * 37) % 100}%`,
  top: `${(i * 61) % 100}%`,
  size: `${1.5 + (i % 3)}px`,
  delay: `${(i % 20) * 0.18}s`,
  duration: `${10 + (i % 7)}s`,
  hue: `${220 + (i % 80)}`
}));

function cleanText(value) {
  if (!value) return "No output available.";
  let text = typeof value === "string" ? value : JSON.stringify(value, null, 2);

  const exported = text.match(/exported_output=(['"])([\s\S]*?)\1/);
  const raw = text.match(/raw_output=(['"])([\s\S]*?)\1/);
  text = exported?.[2] || raw?.[2] || text;

  return text
    .replaceAll("\\n", "\n")
    .replaceAll("\\'", "'")
    .replaceAll('\\"', '"')
    .trim();
}

function Status({ children, tone = "neutral", icon: Icon }) {
  return (
    <span className={`status ${tone}`}>
      {Icon && <Icon size={12} />}
      {children}
    </span>
  );
}

function ParticleField() {
  return (
    <div className="particleField" aria-hidden="true">
      {particles.map((p) => (
        <span
          key={p.id}
          style={{
            "--left": p.left,
            "--top": p.top,
            "--size": p.size,
            "--delay": p.delay,
            "--duration": p.duration,
            "--hue": p.hue
          }}
        />
      ))}
    </div>
  );
}


function AmbientMotion() {
  return (
    <div className="ambientMotion" aria-hidden="true">
      <span className="motionOrb orbOne" />
      <span className="motionOrb orbTwo" />
      <span className="motionOrb orbThree" />
      <span className="motionRing ringOne" />
      <span className="motionRing ringTwo" />
      <span className="motionBeam beamOne" />
    </div>
  );
}

function LoadingResponse() {
  return (
    <motion.div
      className="assistantCard loadingCard"
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <div className="loaderMark">
        <span />
        <span />
        <span />
      </div>
      <div>
        <strong>Running agent workflow</strong>
        <p>Planning, executing, validating, and checking memory context.</p>
      </div>
    </motion.div>
  );
}




function HoverSelect({
  label,
  value,
  options,
  onChange,
  width = 176,
  menuKey,
  openMenu,
  setOpenMenu,
}) {
  const selected =
    options.find((item) => (item.value ?? item.key) === value) || options[0];

  const isOpen = openMenu === menuKey;
  const isWorkflow = menuKey === "workflow";

  return (
    <div
      className={`proPicker ${isWorkflow ? "workflowPicker" : "modelPicker"}`}
      style={{ width }}
      onMouseEnter={() => setOpenMenu(menuKey)}
      onMouseLeave={() => setOpenMenu(null)}
    >
      <button
        type="button"
        className={`proPickerTrigger ${isOpen ? "open" : ""}`}
        onClick={() => setOpenMenu(isOpen ? null : menuKey)}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
      >
        <span className="proPickerMeta">{label}</span>
        <span className="proPickerValue">{selected?.label}</span>
        <span className="proPickerArrow">⌃</span>
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="proPickerMenu"
            role="listbox"
            initial={{ opacity: 0, y: 12, scale: 0.96, filter: "blur(8px)" }}
            animate={{ opacity: 1, y: 0, scale: 1, filter: "blur(0px)" }}
            exit={{ opacity: 0, y: 8, scale: 0.98, filter: "blur(5px)" }}
            transition={{ duration: 0.2, ease: [0.22, 1, 0.36, 1] }}
          >
            <div className="proPickerGlow" />
            {options.map((option, index) => {
              const optionValue = option.value ?? option.key;
              const active = optionValue === value;

              return (
                <motion.button
                  key={optionValue}
                  type="button"
                  role="option"
                  aria-selected={active}
                  className={`proPickerItem ${active ? "active" : ""}`}
                  onClick={() => {
                    onChange(optionValue);
                    setOpenMenu(null);
                  }}
                  initial={{ opacity: 0, y: 7 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{
                    duration: 0.16,
                    delay: index * 0.018,
                    ease: [0.22, 1, 0.36, 1],
                  }}
                >
                  <span>{option.label}</span>
                  {active && <span className="proPickerCheck">✓</span>}
                </motion.button>
              );
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default function App() {
  const [health, setHealth] = useState(null);
  const [agentInfo, setAgentInfo] = useState(null);
  const [task, setTask] = useState("");
  const [openMenu, setOpenMenu] = useState(null);
  const [selectedModel, setSelectedModel] = useState("mistral-7b");
  const [workflowMode, setWorkflowMode] = useState("general");
  const [result, setResult] = useState(null);
  const [activeTab, setActiveTab] = useState("result");
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);
  const [composerFocused, setComposerFocused] = useState(false);
  const composerRef = useRef(null);
  const chatStreamRef = useRef(null);

  const production = agentInfo?.mode?.toLowerCase().includes("production");
  const selectedWorkflow = workflowModes.find((mode) => mode.key === workflowMode) || workflowModes[0];

  const verdictTone = useMemo(() => {
    if (result?.quality_verdict === "PASS") return "success";
    if (result?.quality_verdict === "PASS_WITH_NOTES") return "warning";
    if (result?.quality_verdict === "NEEDS_REVISION") return "danger";
    return "neutral";
  }, [result]);

  function resizeComposer(element) {
    if (!element) return;
    element.style.height = "auto";
    const nextHeight = Math.min(element.scrollHeight, 180);
    element.style.height = `${Math.max(nextHeight, 42)}px`;
    element.style.overflowY = element.scrollHeight > 180 ? "auto" : "hidden";
  }

  function handleTaskChange(event) {
    setTask(event.target.value);
    resizeComposer(event.target);
  }

  async function refreshStatus() {
    setRefreshing(true);
    setError("");

    if (DEMO_MODE) {
      setHealth({ status: "ok" });
      setAgentInfo({
        mode: "demo mode",
        available_agents: [
          "Strategic Planner",
          "Senior Research Analyst",
          "Task Executor",
          "Quality Assurance Validator"
        ]
      });
      setRefreshing(false);
      return;
    }

    try {
      const [healthRes, infoRes] = await Promise.all([
        fetch(`${API_BASE}/health/`),
        fetch(`${API_BASE}/agents/info`)
      ]);

      if (!healthRes.ok) throw new Error("Backend health check failed.");
      if (!infoRes.ok) throw new Error("Agent metadata check failed.");

      setHealth(await healthRes.json());
      setAgentInfo(await infoRes.json());
    } catch (err) {
      setError(err.message || String(err));
    } finally {
      setRefreshing(false);
    }
  }

  async function runWorkflow() {
    const cleanTask = task.trim();
    const routedTask = selectedWorkflow.prefix
      ? `${selectedWorkflow.prefix}\n\nUser task: ${cleanTask}`
      : cleanTask;
    if (!cleanTask || loading) return;

    setLoading(true);
    setError("");
    setActiveTab("result");

    if (DEMO_MODE) {
      window.setTimeout(() => {
        setResult({ ...demoResult, task: cleanTask, workflow_mode: selectedWorkflow.label });
        setLoading(false);
      }, 900);
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/agents/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task: routedTask })
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Workflow failed.");

      setResult(data);
    } catch (err) {
      setError(err.message || String(err));
    } finally {
      setLoading(false);
    }
  }

  function outputText() {
    if (!result) return "";

    if (activeTab === "memory") {
      if (!result.recalled_context?.length) return "No relevant memory was recalled for this workflow.";

      return result.recalled_context
        .map((mem, i) => {
          return `Memory ${i + 1}\nSimilarity: ${mem.similarity}\nTask: ${mem.metadata?.task || "Unknown"}\n\n${mem.snippet}`;
        })
        .join("\n\n---\n\n");
    }

    return cleanText(result[activeTab]);
  }

  async function copyOutput() {
    const text = outputText();
    if (!text) return;

    await navigator.clipboard.writeText(text);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1200);
  }

  useEffect(() => {
    refreshStatus();
  }, []);

  return (
    <div className="app">
      <AmbientMotion />
      <ParticleField />

      <header className="topbar">
        <div className="brand">
          <img className="brandImage" src="/lotus-favicon.png" alt="AgentOS" />
          <div>
            <strong>AgentOS</strong>
            <span>AI Agent Operations</span>
          </div>
        </div>

        <div className="headerStatus">
          <Status tone={health?.status === "ok" ? "success" : "warning"} icon={Activity}>
            {health?.status === "ok" ? "Ready" : "Checking"}
          </Status>
          <Status tone={production || DEMO_MODE ? "success" : "warning"} icon={Zap}>
            {DEMO_MODE ? "Demo" : production ? "Production" : "Connecting"}
          </Status>
          <button className="refreshButton" onClick={refreshStatus}>
            <RefreshCw size={13} className={refreshing ? "spin" : ""} />
            Refresh
          </button>
        </div>
      </header>

      <main className="chatWorkspace">
        <section className="chatStream">
          <AnimatePresence mode="wait">
            {!result && !loading && !error && (
              <motion.div
                key="empty-state"
                className="emptyState"
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8, transition: { duration: 0.3 } }}
              >
                <p className="eyebrow">AI agent operations</p>
                <h1>What should the agents solve?</h1>
                <p>
                  Launch an AMD-powered workflow, then inspect the answer, plan, validation, and memory in one focused workspace.
                </p>
              </motion.div>
            )}
          </AnimatePresence>

          {error && (
            <motion.div className="errorCard" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
              {error}
            </motion.div>
          )}

          {result && (
            <motion.div
              className="userMessage"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
            >
              {result.task || task}
            </motion.div>
          )}

          <AnimatePresence mode="wait">
            {loading && <LoadingResponse key="loading" />}

            {!loading && result && (
              <motion.article
                className="assistantCard"
                key={result.workflow_id || "result"}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -6 }}
              >
                <div className="responseHeader">
                  <motion.div
                    initial={{ opacity: 0, x: -8 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 }}
                  >
                    <p className="eyebrow">Agent response</p>
                    <h2>Workflow result</h2>
                  </motion.div>

                  <motion.div
                    className="responseActions"
                    initial={{ opacity: 0, x: 8 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.15 }}
                  >
                    <Status tone={result.status === "completed" ? "success" : "warning"} icon={CheckCircle2}>
                      {result.status || "completed"}
                    </Status>
                    <Status tone={verdictTone}>{result.quality_verdict || "PENDING"}</Status>
                    <button className="iconButton" onClick={copyOutput} title="Copy response">
                      <Copy size={14} />
                      {copied ? "Copied" : "Copy"}
                    </button>
                  </motion.div>
                </div>

                <div className="responseTabs">
                  {tabs.map(({ key, label, icon: Icon }, index) => (
                    <motion.button
                      key={key}
                      className={activeTab === key ? "active" : ""}
                      onClick={() => setActiveTab(key)}
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.05, duration: 0.3 }}
                    >
                      <Icon size={14} />
                      {label}
                    </motion.button>
                  ))}
                </div>

                <pre className="responseText">{outputText()}</pre>

                {result.duration_seconds && (
                  <motion.div
                    className="responseMeta"
                    initial={{ opacity: 0, y: 4 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 }}
                  >
                    Completed in {result.duration_seconds}s
                  </motion.div>
                )}
              </motion.article>
            )}
          </AnimatePresence>
        </section>

        <section className="composerDock">
          <div className="composer">
            <textarea
              ref={composerRef}
              rows={1}
              value={task}
              onChange={handleTaskChange}
              onFocus={() => setComposerFocused(true)}
              onBlur={() => setComposerFocused(false)}
              onKeyDown={(event) => {
                if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
                  runWorkflow();
                }
              }}
              placeholder="Write a message..."
              autoComplete="off"
              autoCorrect="off"
              autoCapitalize="off"
              spellCheck="false"
            />

            <div className="composerFooter">
              <div className="premiumControls">
                <HoverSelect
                  label="Model"
                  value={selectedModel}
                  options={modelOptions}
                  onChange={setSelectedModel}
                  width={176}
                  menuKey="model"
                  openMenu={openMenu}
                  setOpenMenu={setOpenMenu}
                  align="left"
                />

                <HoverSelect
                  label="Workflow"
                  value={workflowMode}
                  options={workflowModes}
                  onChange={setWorkflowMode}
                  width={218}
                  menuKey="workflow"
                  openMenu={openMenu}
                  setOpenMenu={setOpenMenu}
                  align="right"
                />
              </div>

              <button
                id="run-workflow-btn"
                className={`runButton ${loading ? "loading" : ""}`}
                onClick={runWorkflow}
                disabled={loading || !task.trim()}
              >
                {loading ? <RefreshCw size={16} className="spin" /> : <Play size={16} />}
                {loading ? "Running" : "Enter"}
              </button>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

