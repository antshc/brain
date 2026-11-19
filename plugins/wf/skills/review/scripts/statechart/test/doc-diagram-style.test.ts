import assert from "node:assert/strict";
import { test } from "node:test";
import { mermaid } from "../backends/mermaid.ts";
import type { Chart } from "../ir.ts";

const chart: Chart = {
  title: "Lifecycle",
  regions: [
    {
      name: "Main",
      states: [
        {
          path: ["Ready"],
          start: true,
          members: [],
          works: true,
          lead: false,
          repeats: false,
          breaks: [],
          group: undefined,
        },
      ],
      steps: [],
      arrows: [],
    },
  ],
  notes: [],
  inside: 0,
  quiet: 0,
  colors: {},
  paths: [],
  loops: [],
};

test("generated statecharts follow the doc-diagram base style and stable ID", () => {
  const output = mermaid(chart);
  assert.match(output, /^---\ntitle: "Lifecycle"\n---\n/);
  assert.match(
    output,
    /%%\{init: \{'theme': 'base', 'themeVariables': \{.*'stateBkg': '#242424'.*'stateBorder': '#8b949e'.*'labelColor': '#c9d1d9'.*\}\}\}%%\n/,
  );
  assert.match(output, /%% diagram-id: statechart-model\nstateDiagram-v2\n/);
});
