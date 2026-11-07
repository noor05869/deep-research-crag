---
name: DeepResearch-CRAG
description: Autonomous Corrective-RAG & Self-RAG Research Engine
colors:
  bg-base: "#09090b"
  bg-surface: "#111216"
  bg-surface-hover: "#18191f"
  border-subtle: "#22242c"
  border-focus: "#3b82f6"
  text-primary: "#f4f4f5"
  text-secondary: "#a1a1aa"
  text-muted: "#71717a"
  accent: "#2563eb"
  accent-subtle: "rgba(37, 99, 235, 0.12)"
  status-grounded: "#10b981"
  status-grounded-bg: "rgba(16, 185, 129, 0.1)"
  status-warning: "#f59e0b"
  status-error: "#ef4444"
typography:
  family: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
  prose-measure: "68ch"
rounded:
  sm: "6px"
  md: "10px"
  lg: "14px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "32px"
components:
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.md}"
    padding: "8px 18px"
  search-input:
    backgroundColor: "{colors.bg-surface}"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.lg}"
    padding: "14px 18px"
  citation-badge:
    backgroundColor: "{colors.accent-subtle}"
    textColor: "{colors.accent}"
    rounded: "{rounded.sm}"
    padding: "2px 6px"
---

## Overview
DeepResearch-CRAG is a high-assurance research workstation. It serves users who require strictly verified, hallucination-free factual synthesis with inspectable evidence.
Mode: **Operate / Read**. The interface prioritizes restraint, high typographic contrast, transparent source evidence, and zero decorative noise.

## Colors
- **Restrained dark palette:** Solid obsidian `#09090b` for the canvas, `#111216` for panels and cards.
- **Hairline borders:** Subtle structural boundaries `#22242c` replacing heavy glowing shadows.
- **Solid text colors:** `#f4f4f5` for headings and primary content, `#a1a1aa` for secondary descriptions. No gradient text.
- **Purposeful semantic accents:** Solid cobalt `#2563eb` for user interactions and citations; emerald `#10b981` strictly indicating verified groundedness.

## Typography
- Single unified sans-serif system font stack for low cognitive load and native rendering.
- Body copy is strictly constrained to `68ch` line-length for optimal editorial readability.
- Clear, disciplined scale steps with solid font weights (medium 500, semibold 600) rather than loud display fonts.

## Layout
- Clean asymmetric split:
  - **Left / Main Column (60-65%):** The synthesized research brief with inline numerical citation tokens (`[1]`, `[2]`).
  - **Right Evidence Rail (35-40%):** Synchronized citation cards revealing document source, URL, and exact verbatim quotes.
- No nested cards: information is divided by clean structural hairlines and balanced whitespace.

## Elevation & Depth
- Flat, tonal layering. Depth is expressed by color shifts between surfaces (`#09090b` canvas $\rightarrow$ `#111216` panels), not glowing drop shadows or faux glassmorphism.

## Shapes
- Modest, functional corner radii (6px for badges, 10px for cards/buttons, 14px for inputs). No bulbous pill shapes for entire content sections.

## Components
- **Citation Badges:** High-contrast interactive anchors (`[1]`) that draw attention only when hovered or selected.
- **Audit Strip:** A single-line status bar displaying verified audit results, document count, and execution latency without clownish marketing cards.
- **Empty & Loading States:** Clean skeletons and informative prompt chips that teach the system rather than generic placeholders.

## Do's and Don'ts
- **DO** use solid colors for all headings and metrics.
- **DO** keep citations inspectable and directly linked to their source quotes.
- **DON'T** use gradient text (`bg-clip-text`).
- **DON'T** use purple/cyan gradients or neon drop shadows (`shadow-indigo-500/20`).
- **DON'T** nest cards within cards with stacked borders.
- **DON'T** place decorative floating icon tiles above every heading.
