import assert from "node:assert/strict";
import test from "node:test";
import { lint } from "markdownlint/promise";
import rule from "./markdownlint-table-separator.mjs";

async function check(text) {
  const result = await lint({ strings: { sample: text }, customRules: [rule], config: { default: false, "brain-table-separator": true } });
  return result.sample;
}

test("accepts compact separators while preserving padded cells", async () => {
  assert.deepEqual(await check("| Header A | Header B |\n|---|:---:|\n| Value A | Value B |\n"), []);
});

test("reports separator padding with a fix that preserves alignment", async () => {
  const errors = await check("| A | B |\n| --- | :---: |\n| a | b |\n");
  assert.equal(errors.length, 1);
  assert.equal(errors[0].lineNumber, 2);
  assert.equal(errors[0].fixInfo.insertText, "|---|:---:|");
});

test("ignores table-like content inside fences", async () => {
  assert.deepEqual(await check("```markdown\n| A | B |\n| --- | --- |\n```\n"), []);
});

test("preserves blockquote and list indentation", async () => {
  const errors = await check("> | A | B |\n> | --- | --- |\n\n- Item\n\n  | A | B |\n  | --- | --- |\n");
  assert.equal(errors.length, 2);
  assert.deepEqual(errors.map(error => error.fixInfo.insertText), ["|---|---|", "|---|---|"]);
  assert.ok(errors.every(error => error.fixInfo.editColumn === 3));
});
