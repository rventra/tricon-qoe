# HTML Presentation Visual Schema
## Extracted from: Restorative_Dental_Exit_Strategy.html

---

## 1. CANVAS & SLIDE DIMENSIONS

| Property | Value |
|----------|-------|
| **Slide Size** | 1280px × 720px (16:9 widescreen) |
| **Slide Background** | `#F7F5F0` — Cream / Bone white |
| **Padding** | 30px top/bottom, 50px left/right |
| **Page Break** | `page-break-after: always` (print-ready) |

---

## 2. COLOR PALETTE

### Primary Colors
| Token | Hex | Usage |
|-------|-----|-------|
| **Primary Navy** | `#0B1D3A` | Headings (h1, h2, h3, th), slide titles, framework block headers |
| **Slate Blue** | `#475569` | Body text (p, li, td), subtitles |
| **Cream / Bone** | `#F7F5F0` | Slide background, table header text |

### Accent Colors
| Token | Hex | Usage |
|-------|-----|-------|
| **Accent Gold** | `#C8973E` | Title underline borders, tile borders, icon accents |
| **Soft Gold** | `#E2B45A` | Table borders, tile borders, framework block borders |
| **Bright Gold** | `#EDB624` | Font Awesome icons, highlighted totals, positive accent text |
| **Dark Navy** | `#0F172A` | Legend text, secondary headings |
| **Muted Blue** | `#6B7B8D` | Legend values, secondary text, tile footnotes |

### Semantic Colors
| Token | Hex | Usage |
|-------|-----|-------|
| **Positive Green** | `#059669` | Positive values, upward metrics |
| **Negative Red** | `#DC2626` | Negative values, downward metrics, loss indicators |
| **White** | `#FFFFFF` | Tile backgrounds, chart containers, framework blocks |
| **Light Gray** | `#F5F5F5` | Table total row background, alternate block shading |

---

## 3. TYPOGRAPHY

### Font Families
| Role | Font | Weights | Fallback |
|------|------|---------|----------|
| **Headings** | Manrope | 400, 600, 800 | sans-serif |
| **Body** | Inter | 400, 500, 600 | sans-serif |

### Type Scale
| Element | Size | Weight | Color | Notes |
|---------|------|--------|-------|-------|
| **Slide Title (h2)** | 36px | 800 | `#0B1D3A` | Letter-spacing: -0.5px, bottom border: 2px solid `#C8973E`, padding-bottom: 8px |
| **Section Header (h3)** | 20px | 700 | `#0B1D3A` | — |
| **Framework Block Header (h4)** | 16–18px | 700 | `#0B1D3A` | Flex layout with icon |
| **Body Text (p, li, td, th)** | 15px | 400–600 | `#475569` | Line-height: 1.6 |
| **Large Metric** | 40px | 800 | varies | Manrope, for tile metrics |
| **Table Header (th)** | 13px | 600 | `#F7F5F0` | Uppercase, letter-spacing: 1px, bg: `#0B1D3A` |
| **Chart Summary** | 15px | 400 | `#475569` | Centered, bold for highlights |
| **Tile Body** | 14px | 400 | `#475569` | Line-height: 1.5 |

---

## 4. LAYOUT PATTERNS

### Pattern A: Tiled Content (3-Column Cards)
```
.tiled-content
├── gap: 20px
├── .tile (flex: 1)
│   ├── background: #FFFFFF
│   ├── border: 1px solid #E2B45A
│   ├── border-radius: 12px
│   ├── padding: 24px 20px
│   ├── text-align: center
│   ├── box-shadow: 0 4px 6px rgba(0,0,0,0.02)
│   ├── .icon (32–56px, color: #C8973E)
│   ├── h3 (20px, 700, #0B1D3A)
│   ├── .metric (40px, 800, Manrope)
│   └── p (14px, #475569)
```

### Pattern B: Table Layout
```
.table-layout
├── background: #FFFFFF
├── border-radius: 12px
├── border: 1px solid #E2B45A
├── overflow: hidden
├── table (border-collapse: collapse)
│   ├── th
│   │   ├── bg: #0B1D3A
│   │   ├── color: #F7F5F0
│   │   ├── font-size: 13px
│   │   ├── text-transform: uppercase
│   │   ├── letter-spacing: 1px
│   │   └── padding: 10px 16px
│   ├── td
│   │   ├── border-bottom: 1px solid #E2B45A
│   │   ├── padding: 10px 16px
│   │   ├── text-align: right
│   │   └── first-child: text-align left, font-weight 600, #0B1D3A
│   └── tr:last-child td
│       ├── bg: #F5F5F5
│       ├── font-weight: 800
│       ├── font-size: 17px
│       ├── color: #0B1D3A
│       └── border-top: 2px solid #C8973E
```

### Pattern C: Split Layout (2-Column Grid)
```
.split-layout
├── display: grid
├── grid-template-columns: 1fr 1fr
├── gap: 30px
├── align-items: start
└── .framework-block (nested)
```

### Pattern D: Framework Block (Card with Icon)
```
.framework-block
├── background: #FFFFFF
├── border: 1px solid #E2B45A
├── border-radius: 12px
├── padding: 16–20px
├── margin-bottom: 12px
├── h4 (flex, icon + text, 16–18px, 700, #0B1D3A)
│   └── i.fa-solid (color: #EDB624, margin-right: 12px)
└── p (15–16px, #475569)
```

### Pattern E: Chart Side (Doughnut + Legend)
```
.chart-side
├── display: flex, flex-direction: column, align-items: center
├── background: #FFFFFF
├── border: 1px solid #E2B45A
├── border-radius: 12px
├── padding: 24px
├── .doughnut-chart
│   ├── border-radius: 50%
│   ├── size: 160×160px
│   ├── box-shadow: 0 0 0 6px #FFFFFF inset
│   └── ::after: 90×90px white circle (creates doughnut hole)
└── .legend
    ├── flex, column, gap: 8px
    ├── li: flex, align-items: center
    ├── .color-box: 14×14px, border-radius: 4px
    └── .val: margin-left: auto, #6B7B8D, Manrope, 700
```

---

## 5. SLIDE CONTENT ZONES (16:9)

| Zone | Y-Range | Purpose | Max Objects |
|------|---------|---------|-------------|
| **Navigation/Title** | 0px – ~80px | Slide title with gold underline | 1 |
| **Insight/Content** | ~80px – ~650px | Core content, tiles, tables, charts | 3–5 |
| **Footer** | ~650px – 720px | Sources, disclaimers, page numbers | 1–2 |

---

## 6. VISUAL EFFECTS

| Effect | Value |
|--------|-------|
| **Tile Shadow** | `0 4px 6px rgba(0,0,0,0.02)` |
| **Chart Shadow** | `0 0 0 6px #FFFFFF inset` (doughnut ring) |
| **Border Radius** | 12px (cards, tiles, tables) |
| **Icon Size (tiles)** | 32px standard, 56px for hero scenarios |
| **Gold Underline** | `border-bottom: 2px solid #C8973E` on slide titles |
| **Left Accent Border** | `border-left: 6px solid #EDB624` for emphasis blocks |

---

## 7. COMPONENT INVENTORY

### Slides in Reference Deck
| # | Slide Title | Layout Pattern | Key Elements |
|---|-------------|---------------|--------------|
| 1 | Disentanglement Analysis: Exit Scenarios | **Tiled Content (3 cols)** | 3 tiles with emoji icons, large metrics (+$2.26M, -$136K, -$920K), scenario descriptions |
| 2 | Detailed Scenario Breakdown | **Table Layout** | 7-row table, 4 columns, green/red value formatting, gold-bordered total row |
| 3 | Valuation Framework & Portfolio Concentration | **Split Layout** | Left: 2 framework blocks with icons; Right: doughnut chart + legend + summary |
| 4 | External Debt Allocation | **Split Layout (2 cols)** | Left: 9-row table; Right: 3 stacked framework blocks with left accent borders |
| 5 | Intercompany Dynamics | **Split Layout (2 cols)** | Top: centered subtitle with gold/red highlights; Bottom: 2 framework blocks + 3 scenario cards |

### Iconography
- Font Awesome 6.5.1 solid icons (`fa-solid`)
- Color: `#EDB624` (Bright Gold)
- Used in: framework block headers, tile icons (emojis for scenarios)
- Examples: `fa-chart-line`, `fa-building-shield`, `fa-file-invoice-dollar`, `fa-chart-pie`, `fa-shield-halved`, `fa-building-columns`, `fa-scale-unbalanced`

---

## 8. INTENT DENSITY MAPPING

| Content Type | Visual Structure | When to Use |
|--------------|-----------------|-------------|
| **Scenarios / Options** | 3-Column Tiled Cards | Multiple paths with distinct outcomes |
| **Financial Breakdown** | Bordered Table | Row/column data with totals |
| **Framework + Data** | Split Layout (50/50) | Methodology on left, visual on right |
| **Narrative + Details** | Stacked Framework Blocks | Sequential explanation with icon headers |
| **Concentration / Mix** | Doughnut Chart + Legend | Portfolio distribution, market share |

---

## 9. PPTX TRANSLATION NOTES

### What Works in PPTX
- ✅ Color palette (all hex values map directly)
- ✅ Typography (Manrope + Inter available as Google Fonts)
- ✅ Table styling (header row bg, borders, total row formatting)
- ✅ Framework blocks (rounded rectangles with borders)
- ✅ Split layouts (two-column text boxes)
- ✅ Tile cards (rounded rectangles with centered text)

### What Needs Adaptation
- ⚠️ Doughnut chart: Use PPTX native chart or placeholder image
- ⚠️ Font Awesome icons: Replace with emoji or native PPTX icons
- ⚠️ CSS box-shadow: Use subtle shape fills or skip (PPTX shadow is different)
- ⚠️ `page-break-after`: Not applicable; use slide masters
- ⚠️ Flex/grid layouts: Use absolute positioning or table-based layouts in PPTX

---

## 10. MASTER SLIDE RECOMMENDATIONS

For PPTX translation, create these master layouts:

1. **Title Slide** — Large navy title, gold underline, centered subtitle
2. **Tiled 3-Column** — Three content placeholders with rounded rects
3. **Table Slide** — Full-width content area, pre-styled table
4. **Split 50/50** — Left + right content areas
5. **Framework Blocks** — Stacked rounded rectangles with icon placeholders
6. **Chart + Text** — Left text, right chart/image area
