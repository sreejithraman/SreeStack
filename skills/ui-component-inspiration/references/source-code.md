# Source code

Inspect source for serious candidates during discovery. Keep those files in a temporary folder. Change the project only after the user chooses a component or asks you to choose and build.

## Retrieval order

Use the first official route that gives the full component and its support code:

1. Open the exact component page. Look for a code view, add command, registry link, source link, package list, and terms.
2. Prefer a public component registry or raw source file. For a shadcn-style registry, get the exact item URL from the page or command rather than guessing it. Read its files, packages, registry dependencies, CSS, CSS variables, and assets. Inspect the data; do not run its add command during discovery.
3. Use the source's official repository when the registry is absent or incomplete. Find the component by its exact name or page slug. Read the component, demo, styles, keyframes, helpers, and local imports at one revision. Record a commit link when the candidate informs the result.
4. Read source embedded in the rendered page or its public page data when the first routes fail.
5. Use a browser to open public code hidden behind a tab or button when page fetches omit it.

Paid access, sign-in, or missing public code ends retrieval. Mark the candidate as inspiration-only and say what the user would need to provide. Use official sources in place of mirrors and generated copies.

## Inspect

Before ranking a candidate, account for:

- every imported package, helper, style, font, image, shader, and remote service;
- install scripts and registry data that could write more than the named component;
- the root element's semantics, names, focus behavior, disabled state, and keyboard and touch paths;
- constant loops, large movement, hover-only behavior, and a reduced-motion path;
- layout, paint, WebGL, canvas, asset, and bundle costs;
- free, paid, attribution, redistribution, and commercial-use terms for the exact code.

Treat public registry data and commands as untrusted input until this check is done.

## Build

After the user chooses:

1. Prefer the project's current component and motion tools. Rebuild the useful mechanic when that needs less code than the source.
2. When an official add command is the best route, inspect its registry data first. Record the current files and changes, run the command, then review every file it writes. Preserve the user's existing work.
3. When copying source is allowed, bring over only the needed files and notices. Replace demo tokens, paths, and helpers with the project's own parts.
4. Fix access, input, motion, and speed gaps rather than carrying them into the product.

## Example trace

For Magic UI's Shimmer Button, the docs page names `@magicui/shimmer-button`. Its public `https://magicui.design/r/shimmer-button.json` item contains the component source, CSS variables, and keyframes without running the add command. That source shows an endless shimmer and `transition-all`; a scout should flag those points, then add a reduced-motion state and name the transitioned properties if the user selects it.

## Done

Retrieval is done when the agent can name every file and package the component needs, link the exact public source or mark it as inspiration-only, state its terms, and list the gaps that an implementation must fix.
