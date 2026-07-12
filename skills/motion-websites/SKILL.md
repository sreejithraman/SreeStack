---
name: motion-websites
metadata:
  owner: sree
description: Motion-score and build expressive websites. Use when the user wants a motion-first website or wants an existing web experience given coordinated animation, scroll storytelling, interactive media, or spatial/3D polish.
---

# Motion Websites

A beautiful motion website has an original **art direction** and a coherent **motion score**: every movement supports hierarchy, feedback, continuity, or atmosphere.

## Steps

1. **Read the stage.**

   Inspect the project, routes, design system, content, assets, runtime, and existing animation dependencies. Choose the branch: new experience, motion pass on an existing experience, or one signature interaction. When `.openai/hosting.json` exists, use `sites:sites-building` for the site work.

   Complete when the target surface, preserved stack, content source, brand constraints, and branch are known or recorded as explicit assumptions.

2. **Set the art direction.**

   Derive one sentence that names the audience, desired feeling, and visual tension. From it choose a type pairing, palette, shape language, media treatment, density, and motion intensity. Use owned, generated, or license-clear assets. Treat references as ingredients for an original identity.

   Complete when the direction is specific enough that two implementers would make recognizably related work, and different enough from any single reference to stand on its own.

3. **Write the motion score.**

   Read [MOTION-GRAMMAR.md](MOTION-GRAMMAR.md). Define the signature moment, supporting motifs, triggers, properties, timing, easing, sequencing, interaction states, and reduced-motion equivalents. Match motion intensity to content and audience.

   Complete when every planned movement has a purpose, an owner component, a trigger, and a reduced-motion/static state; the signature moment remains the clear peak.

4. **Build progressively.**

   Establish the static hierarchy first, then implement the score with the smallest suitable engine. Preserve the project's framework and conventions. Turn repeated choreography into a small primitive only after its second real use. Keep touch, coarse-pointer, loading, resize, route-change, and cleanup behavior inside the owning component.

   Complete when the experience is coherent with animation unavailable, the signature moment works on desktop and its mobile adaptation is intentional, and every interactive state remains usable by keyboard and touch.

5. **Pass the gates.**

   Read and apply every gate in [QUALITY-GATES.md](QUALITY-GATES.md). Invoke `manual-verify` and exercise the real surface at desktop and mobile sizes, once with reduced motion. Inspect visible behavior, console output, overflow, loading, and interaction continuity.

   Complete when every gate passes with evidence, or the handoff names the exact gate, evidence, and external blocker.

6. **Hand off the score.**

   Report the art-direction sentence, signature moment, motion engine choices, verification evidence, and the files that own the reusable primitives. Include commands or content/asset controls the user will need next.

   Complete when another agent can extend the experience without reverse-engineering its motion logic.
