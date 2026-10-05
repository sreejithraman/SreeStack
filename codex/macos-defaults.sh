#!/bin/sh
# Apply on macOS with: sh codex/macos-defaults.sh
#
# Enable the undocumented OpenAI computer-use override. It allows computer use
# to target apps or surfaces normally blocked by forbidden-target checks.
# OpenAI documents terminal apps and ChatGPT itself as normally blocked because
# automating them could bypass its security policies:
# https://learn.chatgpt.com/docs/computer-use
# The exact forbidden-target list and override behavior are undocumented and
# may change. App approvals and macOS permissions remain separate controls.
# This global macOS preference is shared across CODEX_HOME directories for the
# same macOS user.
# It is not a Codex config key and has no documented support contract.
#
# Verify the value is 1 and the type is boolean:
#   defaults read -g ComputerUseAllowForbiddenTargets
#   defaults read-type -g ComputerUseAllowForbiddenTargets
#
# Undo by removing the preference:
#   defaults delete -g ComputerUseAllowForbiddenTargets
defaults write -g ComputerUseAllowForbiddenTargets -bool YES
