export default {
  names: ["brain-table-separator"],
  description: "Table separator rows have no padding spaces",
  tags: ["table"],
  parser: "micromark",
  function(params, onError) {
    function visit(tokens) {
      for (const token of tokens) {
        if (token.type === "tableDelimiterRow") {
          const compact = token.text.replace(/[\t ]/g, "");
          if (token.text !== compact) {
            onError({
              lineNumber: token.startLine,
              detail: "Use a separator such as |---|---|; keep cell padding unchanged.",
              fixInfo: {
                editColumn: params.lines[token.startLine - 1].indexOf(token.text) + 1,
                deleteCount: token.text.length,
                insertText: compact
              }
            });
          }
        }
        if (token.children) visit(token.children);
      }
    }
    visit(params.parsers.micromark.tokens);
  }
};
