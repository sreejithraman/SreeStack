---
name: manual-verify
description: Verify changes through real user workflows when hands-on testing would add confidence, including web apps in a browser and iOS apps in Simulator.
---

# Manual Verify

Think like someone who uses this product: who are they, what are they trying to
get done, and how could these changes affect them?

1. **Choose workflows.** Read the changes and identify the affected audience
   and tasks. Use judgment to pick realistic workflows, including nearby behavior
   that could break. Cover relevant error or edge cases without turning every
   change into a full product audit.

2. **Use the product.** Use a browser for web apps and iOS Simulator for iOS apps.
   For other tools, use the interface their users would use. Carry out the chosen
   workflows and compare what happens with what the user needs. Check that the
   result makes sense and is usable, beyond whether the action succeeds.

   If login or another step needs the user, tell them exactly what to do and
   where, then resume once they finish. Continue any independent checks meanwhile.
   If the environment cannot support a needed check, report the gap.

3. **Report what happened.** Briefly state the workflows tested, expected and
   observed results, and any failures or gaps. Include screenshots or other
   evidence when useful. Base conclusions on what you exercised; distinguish
   untested behavior from passing checks.
