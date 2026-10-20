import { Agent, CodexAdapter, loadAgentConfig } from "@band-ai/sdk";
import { readdir, readFile } from "node:fs/promises";
import { join, resolve } from "node:path";
import { promisify } from "node:util";
import { execFile } from "node:child_process";
import { z } from "zod";
import { diagnosticLogger } from "./logger.js";

const validRoles = new Set(["support_lead", "technical_specialist"]);
const role = process.argv[2];

if (!role || !validRoles.has(role)) {
  throw new Error("Usage: npm run band:lead | npm run band:specialist");
}

const prompt = await readFile(resolve("prompts", `${role}.md`), "utf8");

async function resolveCodexCommand(): Promise<string> {
  if (process.env.CODEX_COMMAND) return process.env.CODEX_COMMAND;

  // Codex Desktop installs versioned CLI folders outside the inherited PATH of
  // some child processes. Resolve that documented desktop installation here.
  const binRoot = join(process.env.LOCALAPPDATA ?? "", "OpenAI", "Codex", "bin");
  const entries = await readdir(binRoot, { withFileTypes: true });
  const versionFolder = entries.find((entry) => entry.isDirectory());
  if (!versionFolder) {
    throw new Error("Codex CLI not found. Set CODEX_COMMAND to the path of codex.exe.");
  }
  return join(binRoot, versionFolder.name, "codex.exe");
}

const codexCommand = await resolveCodexCommand();
const execFileAsync = promisify(execFile);

async function runCognee(
  operation: "remember" | "recall",
  customerId: string,
  text: string,
): Promise<string> {
  const python = resolve(
    ".venv",
    process.platform === "win32" ? "Scripts/python.exe" : "bin/python",
  );
  const { stdout } = await execFileAsync(
    python,
    [
      "scripts/cognee_memory.py",
      operation,
      "--customer-id",
      customerId,
      "--text",
      text,
    ],
    { cwd: process.cwd(), timeout: 600_000 },
  );
  return stdout.trim();
}

const agent = Agent.create({
  adapter: new CodexAdapter({
    config: {
      // Band otherwise creates an empty .band-workspaces/<room-id> directory.
      // These agents need read access to the ticket fixtures and prompts in
      // this project, so bind their (single demo) room to the project root.
      workspaceForRoom: () => process.cwd(),
      approvalPolicy: "on-request",
      sandboxMode: "workspace-write",
      reasoningSummary: "concise",
      // `codexCommand` replaces Band's full default command, so preserve the
      // app-server arguments as well as supplying the absolute executable path.
      codexCommand: [codexCommand, "app-server", "--listen", "stdio://"],
      customSection: prompt,
    },
    customTools: [
      {
        name: "recall_customer_memory",
        description:
          "Retrieve durable Cognee history for one customer before drafting support guidance.",
        schema: z.object({
          customerId: z.string().describe(
            "Stable customer ID from the ticket. For this demo it must be exactly acme-labs, never the requester name.",
          ),
          question: z.string().describe("What support history or preference to retrieve"),
        }),
        handler: async ({ customerId, question }) =>
          runCognee("recall", String(customerId), String(question)),
      },
      {
        name: "remember_customer_memory",
        description:
          "Persist an approved customer preference, resolution, or credit decision in Cognee.",
        schema: z.object({
          customerId: z.string().describe(
            "Stable customer ID from the ticket. For this demo it must be exactly acme-labs, never the requester name.",
          ),
          fact: z.string().describe("Concise durable fact, including whether it was human-approved"),
        }),
        handler: async ({ customerId, fact }) =>
          runCognee("remember", String(customerId), String(fact)),
      },
    ],
  }),
  config: loadAgentConfig(role),
  logger: diagnosticLogger,
  // The agents are usually added to the demo room before their local process
  // starts. Without this, the SDK only observes rooms added after startup.
  agentConfig: { autoSubscribeExistingRooms: true },
});

console.log(`Starting Support Relay Band role: ${role}`);
console.log(`Codex executable: ${codexCommand}`);
await agent.run();
