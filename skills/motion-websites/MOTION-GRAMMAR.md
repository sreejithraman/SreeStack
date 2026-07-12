# Motion Grammar

Read this while writing the motion score.

## Score anatomy

Define motion in five lanes. Empty lanes are valid; coherence beats coverage.

| Lane | Purpose | Typical triggers | Good defaults |
|---|---|---|---|
| Entrance | Establish hierarchy | mount, in-view | opacity plus 8–24px travel, short stagger |
| Interaction | Confirm agency | hover, focus, press, drag | direct response, quick settle, visible focus |
| Continuity | Connect states | route, expand, filter, layout change | shared geometry or crossfade |
| Scroll | Reveal relationships | section progress, sticky phase | restrained parallax, progress, pin only when narrative needs it |
| Ambient | Create atmosphere | time, pointer proximity, media loop | slow, low-amplitude, pausable |

For every scored movement record:

`element → purpose → trigger → property → timing/ease → owner → reduced/static state`

## Signature moment

Give each page one peak: a cinematic reveal, spatial product turn, editorial mask, cursor-responsive field, scroll narrative, or typographic transformation. Supporting movement should reuse one or two motifs from the peak—direction, blur, spring character, clipping, or depth—at lower intensity.

The peak earns complexity when it communicates the product, brand, or story. If removing it leaves meaning unchanged, simplify it into atmosphere.

## Engine choice

Choose after the score exists.

| Need | Engine |
|---|---|
| Hover, focus, disclosure, simple entrance | CSS transitions/keyframes |
| React state, layout continuity, viewport reveals, modest scroll links | Motion |
| Multi-phase scrubbed timelines, precise pinning, orchestration across many owners | GSAP + ScrollTrigger |
| Direct media/canvas synchronization | `requestAnimationFrame` with one clock |
| Genuine spatial interaction | Three.js, React Three Fiber, or an existing project 3D layer |

Prefer one primary engine per surface. A second engine needs a distinct job and a clear ownership boundary.

## Timing character

- Feedback responds in roughly 80–180ms.
- Small transitions usually settle in 180–350ms.
- Editorial entrances can occupy 400–800ms when the hierarchy benefits.
- Ambient cycles should feel slower than conscious UI feedback.
- Staggers describe reading order; cap the tail so the interface does not make users wait.
- Springs suit physical or playful identities. Curated cubic curves suit editorial and premium identities.

Tune these ranges to the project rather than treating them as constants.

## Archetypes

- **Cinematic media:** full-bleed image/video, deliberate focal point, restrained chrome, crossfade or mask reveal.
- **Editorial reveal:** strong typography, clipping, split lines, asymmetric pacing, quiet interaction.
- **Product spotlight:** staged feature focus, material/light response, spatial turn, precise CTA feedback.
- **Spatial portfolio:** depth layers, cursor proximity, gallery continuity, optional 3D centerpiece.
- **Interactive interface:** data flow, connected states, diagram motion, purposeful micro-feedback.
- **Playful brand:** elastic shapes, characterful springs, cursor toys, bold color rhythm.
- **Premium SaaS:** calm hierarchy, glass or tonal surfaces, subtle depth, controlled feature reveals.
- **Scroll narrative:** discrete chapters, progress-linked transformation, pinned moments with a clear exit.

Use an archetype as a skeleton. Art direction supplies the identity.

## Asset direction

Choose a focal point and crop rule for every hero asset. Video gets a poster and an intentional loading state. Heavy media loads near need rather than at page start. Mobile may use a different crop, lighter asset, shorter loop, or still frame. Generated assets should share lighting, palette, grain, and camera language.

