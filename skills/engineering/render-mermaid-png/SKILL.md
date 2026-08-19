---
name: render-mermaid-png
description: "Render Mermaid diagrams as high-resolution PNG images with transparent backgrounds. Use when asked to generate, export, convert, or render a Mermaid diagram into a PNG, especially for documentation."
---

# Render Mermaid PNG

Render a Mermaid diagram to a high-resolution PNG with a transparent background using Mermaid CLI (`mmdc`).

## Workflow

1. Save the Mermaid content, without the Markdown fence, to a `.mmd` file next to the intended image.
2. Verify Mermaid CLI is available before its first use in the session:

   ```bash
   mmdc --version
   ```

3. Render with a transparent background and 2x scale:

   ```bash
   mmdc -i <input>.mmd -o <output>.png -w 1040 -s 2 -b transparent
   ```

   The 1040-pixel Mermaid viewport produces a 2048-pixel-wide PNG at 2x scale because Mermaid CLI crops an 8-pixel margin from each side. The default output is a sharp `2048`-pixel-wide PNG.

4. Verify the image dimensions:

   ```bash
   file <output>.png
   ```

5. Inspect the resulting image to confirm that text is readable, labels are not clipped, and the background is transparent.

## Notes

- Preserve the original Mermaid source `.mmd` alongside the generated PNG so the diagram can be reproduced or updated.
- If the user specifies a different output width, adjust the Mermaid viewport by adding 16 pixels before multiplying by the scale factor. For example, a 1024-pixel output at 1x uses `-w 1040`; at 2x it produces a 2048-pixel output.
- Do not use the `-b` option with a color when the requested output needs transparency.