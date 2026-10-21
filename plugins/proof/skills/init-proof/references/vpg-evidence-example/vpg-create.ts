// Copy to proof/contracts/vpg-create.ts; adapt real routes and stable domain fields.
import { matchesFields, containsItem } from "../kit/matchers";
import { JsonlLogAdapter, scopedLogs, logs, type LogScope } from "../kit/logs";
import type { EvidenceContract } from "../kit/evidence-types";

export const vpgCreate: EvidenceContract = {
  feature: "vpg-create", surfaces: ["web", "api"],
  resource: { path: "api/get-vpg.json", kind: "api" },
  required: ["vpg/api: name", "vpg/api: VM present", "vpg/task: succeeded",
    "vpg/ui: refreshed row", "vpg/ui: screenshot", "vpg/browser: request",
    "vpg/browser: console", "vpg/logs: created"],
  async verify(kit) {
    const vpg = await kit.evidence.json<{ id: string; name: string; vms: { name: string }[] }>("api/get-vpg.json");
    const task = await kit.evidence.json("tasks/create-vpg.json");
    const ui = await kit.evidence.json<{ reloaded: boolean; rows: unknown[] }>("browser/vpg-list.json");
    const requests = await kit.evidence.json<unknown[]>("browser/network.json");
    const consoleCapture = await kit.evidence.json<{ complete: boolean; correlationId: string; errors: unknown[] }>("browser/console.json");
    const scope = await kit.evidence.json<LogScope>("logs/scope.json");
    const records = scopedLogs(new JsonlLogAdapter().parse(await kit.evidence.text("logs/application.jsonl"), "logs/application.jsonl"), scope);
    kit.check("vpg/api: name", matchesFields(vpg, { name: "TestVpg" }), true, "api/get-vpg.json");
    kit.check("vpg/api: VM present", containsItem(vpg.vms, { name: "TestVm" }), true, "api/get-vpg.json");
    kit.check("vpg/task: succeeded", matchesFields(task, { vpgId: vpg.id, state: "Succeeded" }), true, "tasks/create-vpg.json");
    kit.check("vpg/ui: refreshed row", ui.reloaded && containsItem(ui.rows, { id: vpg.id, name: "TestVpg" }), true, "browser/vpg-list.json");
    // Supports visual review only; persisted GET + refreshed row prove the business result.
    const png = await kit.evidence.bytes("browser/vpg-list.png");
    kit.check("vpg/ui: screenshot", Array.from(png.slice(0, 8)), [137, 80, 78, 71, 13, 10, 26, 10], "browser/vpg-list.png");
    kit.check("vpg/browser: request", containsItem(requests, { method: "POST", path: "/vpgs", body: { name: "TestVpg" } }), true, "browser/network.json");
    kit.check("vpg/browser: console", consoleCapture.complete && consoleCapture.correlationId === "vpg-create-run" && consoleCapture.errors.length === 0, true, "browser/console.json");
    kit.check("vpg/logs: created", logs.eventExists(records, "VpgCreated", { vpgId: vpg.id }), true, "logs/application.jsonl");
  },
};
