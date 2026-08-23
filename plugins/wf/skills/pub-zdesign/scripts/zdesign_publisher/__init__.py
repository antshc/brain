"""Modules composing the zdesign-to-Confluence publish pipeline.

Split along the seams the original single-file script already delineated with comment
banners, so each seam can be unit tested independently: pure text/ADF transforms
(`patterns`, `inline`, `blocks`, `adf`) are dependency-free; I/O-touching seams
(`env`, `mermaid` rendering, `attachments`, `cli`) are thin enough to test with mocks.
"""
