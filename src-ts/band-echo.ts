import { Agent, GenericAdapter, loadAgentConfig } from "@band-ai/sdk";
import { diagnosticLogger } from "./logger.js";

const validRoles = new Set(["support_lead", "technical_specialist"]);
const role = process.argv[2];

if (!role || !validRoles.has(role)) {
  throw new Error("Usage: npm run band:lead:echo | npm run band:specialist:echo");
}

const agent = Agent.create({
  // This bypasses Codex completely. It proves Band room delivery and mention
  // routing before a coding-agent process is introduced.
  adapter: new GenericAdapter(async ({ message, tools }) => {
    console.log(`[delivery] received ${message.id} in room ${message.roomId}`);
    // Band agent text messages require a recipient mention. Reply directly to
    // the human/agent who triggered this diagnostic turn.
    await tools.sendMessage(
      `Echo from ${role}: I received your message.`,
      [message.senderId],
    );
  }),
  config: loadAgentConfig(role),
  logger: diagnosticLogger,
  agentConfig: { autoSubscribeExistingRooms: true },
});

console.log(`Starting Band echo diagnostic: ${role}`);
await agent.run();
