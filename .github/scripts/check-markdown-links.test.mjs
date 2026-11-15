import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { checkRepository, missingLinks } from "./check-markdown-links.mjs";
import { execFileSync } from "node:child_process";

function fixture(t) {
  const root = mkdtempSync(path.join(os.tmpdir(), "brain-links-"));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  const file = path.join(root, "SKILL.md");
  writeFileSync(path.join(root, "real file.md"), "# Target\n");
  return { root, file };
}

test("checks inline, reference and image links, including encoded paths", t => {
  const { root, file } = fixture(t);
  const errors = missingLinks(file, "[ok](real%20file.md#heading) [bad](missing.md) ![image](missing.png) [ref][r]\n\n[r]: absent.md", root);
  assert.equal(errors.length, 3);
  assert.ok(errors.some(error => error.includes("absent.md")));
});

test("ignores code, metadata, remote URLs, anchors and runtime placeholders", t => {
  const { root, file } = fixture(t);
  const text = "---\ndescription: '[meta](missing.md)'\n---\n```markdown\n[code](missing.md)\n```\n`[inline](missing.md)` [remote](https://example.com) [anchor](#heading) [runtime](/tmp/report.md) [template]({{file}})";
  assert.deepEqual(missingLinks(file, text, root), []);
});

test("an exception allows only its exact destination", t => {
  const { root, file } = fixture(t);
  const errors = missingLinks(file, "[generated](generated.md) [bad](missing.md)", root, { "generated.md": "Created by installer" });
  assert.equal(errors.length, 1);
  assert.match(errors[0], /missing.md/);
});

test("scans tracked dotfiles while excluding archived trees", t => {
  const { root } = fixture(t);
  execFileSync("git", ["init", "--quiet"], { cwd: root });
  for (const folder of [".github", "_backup", "_in-progress", "docs/kbs"]) {
    mkdirSync(path.join(root, folder), { recursive: true });
    writeFileSync(path.join(root, folder, "sample.md"), "[bad](absent.md)");
  }
  execFileSync("git", ["add", "."], { cwd: root });
  const errors = checkRepository(root);
  assert.equal(errors.length, 1);
  assert.match(errors[0], /\.github/);
});
