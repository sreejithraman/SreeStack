# Capabilities Reference

Complete reference of everything koubou can do. The skill primarily uses HTML template mode, but this documents all capabilities for context.

## Two Generation Modes

### 1. HTML Template Mode (recommended for skill)

Free-form design with HTML/CSS. Templates receive `{{variables}}` for text and
`{{assets}}` for image paths. With a selected device and framing enabled,
PNG/JPEG assets are composited inside its frame; other formats pass through.
See [HTML asset preparation](https://github.com/bitomule/Koubou/blob/v0.20.0/src/koubou/generator.py#L466)
and the [framing configuration](yaml-reference.md#disabling-device-frame).

```yaml
screenshots:
  slide_1:
    template: "templates/hero.html"
    variables:
      headline: "Your Text"
      subtitle: "A concrete supporting benefit"
      bg_start: "#1a1a2e"
      bg_end: "#0f3460"
    assets:
      app_screenshot: "screenshots/home.png"
```

When HTML contains `data-kou-id` annotations, generation emits a compact sidecar
JSON containing normalized element geometry and mathematical overlaps. See the
[HTML result writer](https://github.com/bitomule/Koubou/blob/v0.20.0/src/koubou/generator.py)
and the [localized JSON inventory limitation](yaml-reference.md#html-template-mode-recommended)
before relying on returned `layout_path` entries.

### 2. Content YAML Mode (programmatic)

Items positioned by coordinates. Useful for simple layouts without HTML.
This mode emits PNGs without HTML annotation sidecars; verify configured
positions and frame geometry visually, and do not claim sidecar measurements.

```yaml
screenshots:
  slide_1:
    background:
      type: linear
      colors: ["#1a1a2e", "#0f3460"]
      direction: 180
    content:
      - type: text
        content: "Your Headline"
        position: ["50%", "15%"]
        size: 120
        color: "#FFFFFF"
        weight: bold
      - type: image
        asset: "screenshots/home.png"
        position: ["50%", "65%"]
        scale: 0.6
        frame: true
```

## Content Item Types (YAML mode)

### text

```yaml
- type: text
  content: "Hello World"
  position: ["50%", "50%"]       # X, Y as % or px
  size: 48                       # Font size in pixels
  color: "#FFFFFF"               # Solid color (hex)
  weight: "bold"                 # normal or bold
  font_family: "Arial"           # Font family
  alignment: "center"            # left, center, right
  max_width: 1000                # Max width for wrapping (px)
  max_lines: 2                   # Max number of lines
  max_height: 300                # Max height budget (px)
  min_size: 24                   # Min font size for auto-sizing
  stroke_width: 3                # Text outline width
  stroke_color: "#000000"        # Solid stroke color
```

For a gradient fill, replace `color` with `gradient`. That fill path supports
either `stroke_color` or `stroke_gradient` (choose one). For example:

```yaml
- type: text
  content: "Hello World"
  position: ["50%", "50%"]
  size: 48
  weight: "bold"
  gradient:
    type: linear
    colors: ["#FF6B6B", "#4ECDC4"]
    direction: 45
  stroke_width: 3
  stroke_gradient:
    type: linear
    colors: ["#FF0000", "#0000FF"]
    direction: 0
```

In 0.20.0, a solid `color` fill renders only `stroke_color`; it ignores
`stroke_gradient`. Use the supported combinations above or HTML/CSS for a
different treatment. See the [solid and gradient text paths](https://github.com/bitomule/Koubou/blob/v0.20.0/src/koubou/renderers/text.py).

**Auto-sizing**: Set `min_size` + `max_width` + `max_height`. Koubou starts at `size` and shrinks to `min_size` until the text fits within the height budget.

For content-mode text in Koubou 0.20.0, numeric weights do not select numeric
font variants (an unquoted number fails schema validation), and `line_height`
and text `rotation` are not forwarded to the rendered text overlay. Use
HTML/CSS when those controls are needed. See the [content schema](https://github.com/bitomule/Koubou/blob/v0.20.0/src/koubou/config.py),
[overlay conversion](https://github.com/bitomule/Koubou/blob/v0.20.0/src/koubou/generator.py),
and [font selection](https://github.com/bitomule/Koubou/blob/v0.20.0/src/koubou/renderers/text.py).

### image

Image rotation below is a separate supported content-mode control.

```yaml
- type: image
  asset: "screenshots/home.png"  # Image path
  position: ["50%", "60%"]       # Center position
  scale: 0.6                     # Scale factor
  frame: true                    # Apply device frame
  rotation: -5                   # Clockwise rotation in degrees
```

Asset path supports localization:
- **String**: Convention-based (`screenshots/home.png` resolves to `screenshots/{lang}/home.png`)
- **Dict**: Explicit per-language paths

```yaml
  asset:
    en: "screenshots/en/home.png"
    es: "screenshots/es/home.png"
    default: "screenshots/home.png"
```

### highlight

Annotation overlays drawn on top of images.

```yaml
- type: highlight
  shape: "rounded_rect"          # circle, rounded_rect, rect
  position: ["50%", "40%"]       # Center position
  dimensions: ["30%", "10%"]     # Width, height (% or px)
  border_color: "#FF0000"        # Border color
  border_width: 4                # Border width in px
  fill_color: "#FF000020"        # Fill with alpha
  corner_radius: 16              # For rounded_rect

  # Shadow
  shadow: true
  shadow_color: "#00000040"
  shadow_blur: 15
  shadow_offset: ["0", "6"]

  # Spotlight mode (dims everything outside)
  spotlight: true
  spotlight_color: "#000000"
  spotlight_opacity: 0.5

  # Blur background (blur non-highlighted area)
  blur_background: true
  blur_radius: 20
```

### zoom

Magnified callout that crops a region and shows it enlarged.

```yaml
- type: zoom
  source_position: ["30%", "40%"]   # Center of area to magnify
  source_size: ["15%", "10%"]       # Size of source crop
  display_position: ["70%", "30%"]  # Where magnified view appears
  display_size: ["40%", "30%"]      # Size of magnified bubble
  # OR
  zoom_level: 2.5                   # Auto-calc display_size from source_size * zoom_level

  shape: "circle"                   # circle, rounded_rect, rect
  border_color: "#FFFFFF"
  border_width: 3
  corner_radius: 16

  # Source indicator
  source_indicator: true
  source_indicator_style: "border"  # border, dashed, fill

  # Connector line
  connector: true
  connector_color: "#FFFFFF"
  connector_width: 2
  connector_style: "curved"         # straight, curved, facing
  connector_fill: "#FFFFFF20"       # Fill between facing lines

  # Shadow
  shadow: true
  shadow_color: "#00000040"
  shadow_blur: 15
```

## Gradients

Content-mode backgrounds support the types below. Text fills and strokes use
the supported combinations in the text section; HTML templates use CSS.

### Types

```yaml
# Solid
background:
  type: solid
  colors: ["#1a1a2e"]

# Linear
background:
  type: linear
  colors: ["#1a1a2e", "#0f3460", "#e94560"]
  positions: [0.0, 0.5, 1.0]    # Optional color stops
  direction: 180                  # Last color points left (0=right, 90=bottom, 270=top)

# Radial
background:
  type: radial
  colors: ["#667eea", "#764ba2"]
  center: ["50%", "50%"]         # Center point
  radius: "70%"                  # Radius

# Conic
background:
  type: conic
  colors: ["#FF0000", "#00FF00", "#0000FF", "#FF0000"]
  center: ["50%", "50%"]
  start_angle: 0                 # Starting angle in degrees
```

Content-mode linear gradients use a different angle convention from CSS
`linear-gradient`: their last color points right at 0°, bottom at 90°, left at
180°, and top at 270°. See the [gradient renderer](https://github.com/bitomule/Koubou/blob/v0.20.0/src/koubou/renderers/gradient.py).
Use CSS's own angle convention in HTML templates.

## Layer Order

Content items render in this order (back to front):

1. **Background** (solid, gradient)
2. **Images** (in YAML order — first = bottom layer)
3. **Highlights** (annotations on top of images)
4. **Zooms** (magnified callouts)
5. **Text** (always on top)

## CLI Reference

The [CLI implementation](https://github.com/bitomule/Koubou/blob/v0.20.0/src/koubou/cli.py)
defines these commands and options. Check the working installation's `--help`
when its version differs.

```bash
# Generate screenshots
kou generate config.yaml
kou generate config.yaml --verbose
kou generate config.yaml --output json

# Live editing (watch for changes, auto-regenerate)
kou live config.yaml
kou live config.yaml --debounce 0.5 --verbose

# List available App Store sizes
kou list-sizes
kou list-sizes --output json

# List available device frames
kou list-frames
kou list-frames "iPhone 16"
kou list-frames "iPad" --output json

# Inspect frame geometry for layout work
kou inspect-frame "iPhone 16 Pro - Black Titanium - Portrait" --output-size iPhone6_9
kou inspect-frame "iPhone 16 Pro - Black Titanium - Portrait" --output-size iPhone6_9 --output json

# Create sample config
kou --create-config sample.yaml
kou --create-config sample.yaml --name "My App" --force

# Version
kou --version
```

### Output formats

All list/generate commands support `--output json` for machine-readable output (useful for automation). Default is `table` (human-readable rich output).

### Live mode

`kou live` watches configuration and discovered dependencies, regenerating
affected screenshots. Use `--debounce` to control the delay (default 0.5s).

In 0.20.0, the [dependency analyzer](https://github.com/bitomule/Koubou/blob/v0.20.0/src/koubou/dependency_analyzer.py)
tracks the HTML template tree but does not traverse declared HTML `assets`.
Captures outside that tree can therefore be absent from the watch set. After
changing one, explicitly rerun `kou generate <config.yaml>` or restart live
mode, then check that the resulting image contains the latest capture. Do not
assume an asset replacement refreshed the preview. The [live generator](https://github.com/bitomule/Koubou/blob/v0.20.0/src/koubou/live_generator.py)
uses this analyzer's paths and the strings catalog; no CLI upgrade is required
to use the explicit-generation workaround.
