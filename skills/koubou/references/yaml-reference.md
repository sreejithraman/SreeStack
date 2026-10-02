# YAML Config Reference

## Minimal config (HTML template mode)

```yaml
project:
  name: "My App"
  output_dir: "output"
  device: "iPhone 16 Pro - Black Titanium - Portrait"
  output_size: "iPhone6_9"

screenshots:
  01_hero:
    template: "templates/hero.html"
    variables:
      headline: "Your Headline"
      subtitle: "Your subtitle text"
      bg_start: "#1a1a2e"
      bg_end: "#0f3460"
    assets:
      app_screenshot: "screenshots/home.png"
```

## Project section

```yaml
project:
  name: "App Name"                                        # Project name
  output_dir: "output"                                    # Where screenshots go
  device: "iPhone 16 Pro - Black Titanium - Portrait"     # Device frame to use
  output_size: "iPhone6_9"                                # App Store size (or [width, height])
```

`output_size` accepts named sizes or custom `[width, height]` arrays. See sizes table below.

Design implication:
- The skill should read `project.device` and `project.output_size` before writing templates. Typography scale, layout density, and device crop should adapt to this canvas instead of using one fixed CSS recipe.
- The skill should run `kou inspect-frame "<device>" --output-size <size> --output json` and use the returned geometry instead of estimating screen area and margins by eye.

## Screenshots section

Each key under `screenshots:` is a screenshot ID (used as filename).

### HTML template mode (recommended)

```yaml
screenshots:
  01_hero:
    template: "templates/hero.html"        # Path to HTML template
    variables:                             # Text — localizable via xcstrings
      headline: "Clean Your iPhone"
      subtitle: "Free up space instantly"
      bg_start: "#1a1a2e"
      bg_end: "#0f3460"
    assets:                                # Images — pre-rendered with device frame
      app_screenshot: "screenshots/home.png"
```

Recommended HTML annotation for measured layouts:

```html
<h1 data-kou-id="headline" data-kou-role="headline">{{headline}}</h1>
<p data-kou-id="subtitle" data-kou-role="supporting">{{subtitle}}</p>
<img data-kou-id="device" data-kou-role="device" src="{{app_screenshot}}" alt="">
```

Annotated HTML emits sibling `*.layout.json` sidecars with normalized geometry
and overlaps. Use a reported `layout_path` when present, but do not treat CLI
JSON as a complete output inventory: Koubou 0.20.0 reports only one result per
configured slide even when localization generates several languages. Enumerate
the expected language × slide PNGs in `project.output_dir`, check each PNG and
its sibling sidecar, and review all of them.

For each checked export, use a fresh, empty, ignored output directory and retain
the complete stdout/stderr log. In 0.20.0, a per-language render error can be
caught while other languages succeed; the CLI can still report success, and
old PNGs/sidecars in a reused directory remain. Reject any per-task generation
error and any expected output not produced by the current run. Missing files
or missing required annotations are verification failures. Do not accept an
old pair merely because it exists. Preserve earlier accepted files separately;
for a targeted change, export only the affected requested scope into the fresh
directory. Do not upgrade a working installation automatically to avoid these
limitations.

Technical sources: the [0.20.0 CLI result loop](https://github.com/bitomule/Koubou/blob/v0.20.0/src/koubou/cli.py)
and [HTML sidecar writer and localized generation](https://github.com/bitomule/Koubou/blob/v0.20.0/src/koubou/generator.py).
Generation logs can precede the final JSON array on stdout; preserve the full
log and inspect the final result rather than blindly parsing all stdout as JSON.

### variables vs assets

| Field | Template syntax | What it does | Localized? |
|-------|----------------|-------------|-----------|
| `variables` | `{{key}}` | Text substitution | Yes (via xcstrings) |
| `assets` | `{{key}}` | Image path; PNG/JPEG can receive a device frame | Directory convention or language mapping |

Both use `{{key}}` in the HTML. The difference:
- **variables**: Pure text replacement. Values are extracted as xcstrings keys for localization
- **assets**: File paths staged into the template sandbox. With a selected device and framing enabled, Koubou pre-renders files with `.png`, `.jpg`, or `.jpeg` extensions inside the device frame; other formats pass through unchanged.

### Disabling device frame

With a selected device, HTML framing defaults to enabled for `.png`, `.jpg`,
and `.jpeg` assets (extension matching ignores case). WebP and SVG bypass that
branch. Convert a capture to PNG when it needs automatic framing, or use the
measured composition recipe below. See the
[HTML asset preparation implementation](https://github.com/bitomule/Koubou/blob/v0.20.0/src/koubou/generator.py#L466).
To disable framing per screenshot:

```yaml
  fullscreen_slide:
    template: "templates/contrast.html"
    frame: false                          # No device frame for this slide
    variables:
      headline: "Bold Statement"
      subtitle: "A concrete supporting benefit"
      bg_start: "#1a1a2e"
      bg_end: "#0f3460"
```

### Mixed device and brand assets

HTML framing is per slide, not per asset. On a framed slide, an ordinary PNG
icon or badge would also receive a device frame. For mixed assets, prepare a
correctly framed device-only PNG separately (retain any frame license notice),
then disable framing on the composition slide. Use the device image's actual
bounds and aspect ratio; a complete earlier marketing slide is not a device
asset.

See the [HTML asset preparation implementation](https://github.com/bitomule/Koubou/blob/v0.20.0/src/koubou/generator.py)
for per-slide framing and `frame: false` passthrough.

```yaml
screenshots:
  branded_hero:
    template: "templates/branded.html"
    frame: false
    variables:
      headline: "A concrete app benefit"
    assets:
      device_image: "assets/framed-device.png"
      app_icon: "assets/app-icon.png"
```

```html
<h1 data-kou-id="headline" data-kou-role="headline">{{headline}}</h1>
<img data-kou-id="device" data-kou-role="device" src="{{device_image}}" alt="">
<img data-kou-id="app-icon" data-kou-role="brand" src="{{app_icon}}" alt="">
```

This passes both assets through without double framing. Position and scale
them explicitly in CSS, then inspect the final device/screen alignment and
sidecars. If no suitable framed device asset exists, compose a licensed frame
and capture in HTML using measured screen bounds with `frame: false`; do not
guess bezel geometry or silently frame the icon.

## Defaults section (optional)

```yaml
defaults:
  background:
    type: linear
    colors: ["#1a1a2e", "#16213e"]
    direction: 180
```

Applied to content-mode screenshots that don't specify their own background. Not used by HTML template mode (templates define their own backgrounds in CSS).

## Localization

```yaml
localization:
  base_language: "en"
  languages: ["en", "es", "de", "ja"]
  xcstrings_path: "koubou-strings.xcstrings"
```

### How text localization works

1. All `variables` values are extracted as localization keys
2. Koubou creates/updates the xcstrings file with these keys
3. Base language gets the value as-is with `state: "translated"`
4. Other languages get empty values with `state: "needs_translation"`
5. Edit translations in Xcode or any xcstrings editor
6. On generation, koubou substitutes the translated text for each language

The [XCStrings manager and content resolver](https://github.com/bitomule/Koubou/blob/v0.20.0/src/koubou/localization.py)
implement extraction, translation state, and fallback to base text when a
translation is missing. Verify translations before claiming a localized output.

### How asset localization works

**Convention-based** (recommended): Place localized screenshots in language subdirectories.

```
screenshots/
  en/
    home.png
    features.png
  es/
    home.png
    features.png
```

Config just references the base path — koubou resolves `screenshots/home.png` to `screenshots/{lang}/home.png` automatically:

```yaml
assets:
  app_screenshot: "screenshots/home.png"
```

Resolution order: `screenshots/{current_lang}/home.png` → `screenshots/{base_lang}/home.png` → `screenshots/home.png`

See [localized asset resolution](https://github.com/bitomule/Koubou/blob/v0.20.0/src/koubou/generator.py)
for this directory fallback.

**Explicit mapping**: HTML assets and content-mode image items both support
language maps. In HTML, put the map under the named asset:

```yaml
assets:
  app_screenshot:
    en: "screenshots/en/home.png"
    es: "screenshots/es/home.png"
    default: "screenshots/home.png"
```

In a content-mode image item, use its singular `asset` field:

```yaml
asset:
  en: "screenshots/en/home.png"
  es: "screenshots/es/home.png"
  default: "screenshots/home.png"
```

The [configuration schema](https://github.com/bitomule/Koubou/blob/v0.20.0/src/koubou/config.py)
accepts both forms; the [asset resolver](https://github.com/bitomule/Koubou/blob/v0.20.0/src/koubou/generator.py)
chooses the current language (exact code, then language-only fallback such as
`es-MX` → `es`), then `default` when that language is absent.
Without either, resolution returns no asset path and HTML staging omits that
asset; include a suitable fallback or supply every requested language and
verify the visible capture in each output.

### Localized output structure

```
output/
  en/
    iPhone_16_Pro_-_Black_Titanium_-_Portrait/
      01_hero.png
      02_feature.png
  es/
    iPhone_16_Pro_-_Black_Titanium_-_Portrait/
      01_hero.png
      02_feature.png
```

## Complete example

```yaml
project:
  name: "Undolly"
  output_dir: "AppStore/output"
  device: "iPhone 16 Pro - Black Titanium - Portrait"
  output_size: "iPhone6_9"

localization:
  base_language: "en"
  languages: ["en", "es"]
  xcstrings_path: "AppStore/koubou-strings.xcstrings"

screenshots:
  01_hero:
    template: "AppStore/templates/hero.html"
    variables:
      headline: "Find Duplicate Photos"
      subtitle: "Free up gigabytes of space"
      bg_start: "#1a1a2e"
      bg_end: "#0f3460"
    assets:
      app_screenshot: "screenshots/home.png"

  02_scan:
    template: "AppStore/templates/feature_top.html"
    variables:
      headline: "Smart Scanning"
      subtitle: "AI-powered duplicate detection"
      bg_start: "#0f3460"
      bg_end: "#1a1a2e"
    assets:
      app_screenshot: "screenshots/scan.png"

  03_results:
    template: "AppStore/templates/feature_side.html"
    variables:
      headline: "Review Results"
      subtitle: "Keep what matters"
      bg_start: "#1a1a2e"
      bg_mid: "#162447"
      bg_end: "#1b1b3a"
    assets:
      app_screenshot: "screenshots/results.png"

  04_statement:
    template: "AppStore/templates/contrast.html"
    frame: false
    variables:
      headline: "Your Photos, Organized"
      subtitle: "Made for people who care"
      bg_start: "#0f3460"
      bg_end: "#1a1a2e"

  05_more:
    template: "AppStore/templates/features_list.html"
    frame: false
    variables:
      headline: "And So Much More"
      feature_1_title: "iCloud Sync"
      feature_1_sub: "Your library across devices"
      feature_2_title: "Batch Delete"
      feature_2_sub: "Review before removing"
      feature_3_title: "Smart Albums"
      feature_3_sub: "Keep your collection organized"
      accent_start: "#5b9a86"
      accent_end: "#347365"
      bg_start: "#1a1a2e"
      bg_end: "#0f3460"
```

The closing template in the design guide shows one feature row. Repeat it for
features 2 and 3 with their matching variables and unique annotations. These
sample claims must be replaced with features the actual app supports. Before
rendering, check that every `{{placeholder}}` in each template has a matching
variable or asset; Koubou's [HTML staging](https://github.com/bitomule/Koubou/blob/v0.20.0/src/koubou/renderers/html_staging.py)
uses literal substitution and does not reject unresolved tokens.

## Devices

### Recommended defaults

| Use case | Device name | Output size |
|----------|------------|-------------|
| iPhone (standard) | `iPhone 16 Pro - Black Titanium - Portrait` | `iPhone6_9` |
| iPhone (max) | `iPhone 16 Pro Max - Black Titanium - Portrait` | `iPhone6_9` |
| iPad | `iPad Pro 13 - M4 - Space Gray - Portrait` | `iPadPro13` |

### Finding device names

```bash
kou list-frames                    # All available frames (100+)
kou list-frames "iPhone 16"        # Filter by search term
kou list-frames "iPad"             # iPad frames
kou list-frames --output json      # Machine-readable
kou inspect-frame "iPhone 16 Pro - Black Titanium - Portrait" --output-size iPhone6_9 --output json
```

Device names must match exactly as shown by `kou list-frames`.

## App Store Sizes

These are Koubou's named output canvases. Use `kou list-sizes` to check the
working installation; select the required store canvas separately from the
device-frame model. See the [size definitions](https://github.com/bitomule/Koubou/blob/v0.20.0/src/koubou/appstore_sizes.json).

| Name | Dimensions |
|------|------------|
| `iPhone6_9` | 1320x2868 |
| `iPhone6_7` | 1290x2796 |
| `iPhone6_5` | 1242x2688 |
| `iPhone6_1` | 1179x2556 |
| `iPhone5_5` | 1242x2208 |
| `iPadPro13` | 2064x2752 |
| `iPadPro12_9` | 2048x2732 |
| `iPadPro11` | 1668x2388 |

List all: `kou list-sizes`

Custom dimensions: `output_size: [1320, 2868]`
