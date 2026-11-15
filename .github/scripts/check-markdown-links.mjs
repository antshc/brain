import { execFileSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import MarkdownIt from "markdown-it";

const parser = new MarkdownIt();
const exceptions = JSON.parse(readFileSync(new URL("./markdown-link-exceptions.json", import.meta.url), "utf8"));
const excluded = /(?:^|\/)(?:_backup|_in-progress)(?:\/|$)|(?:^|\/)docs\/kbs(?:\/|$)/;

export function missingLinks(file, text, root, allowed = {}) {
  // Front matter is metadata; fenced code and inline code are handled by the parser.
  const body = text.replace(/^---\r?\n[\s\S]*?\r?\n---(?:\r?\n|$)/, "");
  const missing = new Set();
  function visit(tokens) {
    for (const token of tokens) {
      if (token.type === "link_open" || token.type === "image") {
        const target = token.attrGet(token.type === "image" ? "src" : "href");
        // Runtime paths, URLs, anchors, and template destinations aren't repo files.
        if (target && !allowed[target] && !/^(?:[a-z][a-z\d+.-]*:|\/|#)/i.test(target) &&
            !/[<>{}$]/.test(decodeURIComponent(target))) {
          const destination = decodeURIComponent(target.split(/[?#]/, 1)[0]);
          if (destination && !existsSync(path.resolve(path.dirname(file), destination))) {
            missing.add(`${path.relative(root, file)}: missing local link ${target}`);
          }
        }
      }
      if (token.children) visit(token.children);
    }
  }
  visit(parser.parse(body, {}));
  return [...missing];
}

export function checkRepository(root) {
  const files = execFileSync("git", ["ls-files", "-z"], { cwd: root, encoding: "utf8" })
    .split("\0").filter(file => /\.(?:md|markdown)$/i.test(file) && !excluded.test(file));
  return files.flatMap(file => missingLinks(path.join(root, file), readFileSync(path.join(root, file), "utf8"), root, exceptions[file]));
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const errors = checkRepository(process.cwd());
  for (const error of errors) console.error(error);
  console.log(`Local Markdown links: ${errors.length} error(s)`);
  process.exitCode = errors.length ? 1 : 0;
}
