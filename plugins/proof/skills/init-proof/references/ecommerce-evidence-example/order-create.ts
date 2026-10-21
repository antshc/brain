// Copy to proof/contracts/order-create.ts; adapt real routes and stable domain fields.
import { matchesFields, containsItem } from "../kit/matchers";
import { JsonlLogAdapter, scopedLogs, logs, type LogScope } from "../kit/logs";
import type { EvidenceContract } from "../kit/evidence-types";

export const orderCreate: EvidenceContract = {
  feature: "order-create", surfaces: ["web", "api"],
  resource: { path: "api/get-order.json", kind: "api" },
  required: ["order/api: status", "order/api: item present", "order/task: succeeded",
    "order/ui: refreshed row", "order/ui: screenshot", "order/browser: request",
    "order/browser: console", "order/logs: created"],
  async verify(kit) {
    const order = await kit.evidence.json<{ id: string; status: string; items: { sku: string; quantity: number }[] }>("api/get-order.json");
    const task = await kit.evidence.json("tasks/create-order.json");
    const ui = await kit.evidence.json<{ reloaded: boolean; rows: unknown[] }>("browser/order-list.json");
    const requests = await kit.evidence.json<unknown[]>("browser/network.json");
    const consoleCapture = await kit.evidence.json<{ complete: boolean; correlationId: string; errors: unknown[] }>("browser/console.json");
    const scope = await kit.evidence.json<LogScope>("logs/scope.json");
    const records = scopedLogs(new JsonlLogAdapter().parse(await kit.evidence.text("logs/application.jsonl"), "logs/application.jsonl"), scope);
    kit.check("order/api: status", matchesFields(order, { status: "Confirmed" }), true, "api/get-order.json");
    kit.check("order/api: item present", containsItem(order.items, { sku: "SKU-COFFEE", quantity: 2 }), true, "api/get-order.json");
    kit.check("order/task: succeeded", matchesFields(task, { orderId: order.id, state: "Succeeded" }), true, "tasks/create-order.json");
    kit.check("order/ui: refreshed row", ui.reloaded && containsItem(ui.rows, { id: order.id, status: "Confirmed" }), true, "browser/order-list.json");
    // Supports visual review only; persisted GET + refreshed row prove the business result.
    const png = await kit.evidence.bytes("browser/order-list.png");
    kit.check("order/ui: screenshot", Array.from(png.slice(0, 8)), [137, 80, 78, 71, 13, 10, 26, 10], "browser/order-list.png");
    kit.check("order/browser: request", containsItem(requests, { method: "POST", path: "/orders", body: { items: [{ sku: "SKU-COFFEE", quantity: 2 }] } }), true, "browser/network.json");
    kit.check("order/browser: console", consoleCapture.complete && consoleCapture.correlationId === "order-create-run" && consoleCapture.errors.length === 0, true, "browser/console.json");
    kit.check("order/logs: created", logs.eventExists(records, "OrderCreated", { orderId: order.id }), true, "logs/application.jsonl");
  },
};
