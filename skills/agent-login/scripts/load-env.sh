#!/bin/sh
# Prints shell export lines for the agents' shared dotenv file, for runtimes
# such as Claude Code that do not load it themselves. Variables that are
# already set win, as with Codex's own .env loading. Use:
#   eval "$(sh load-env.sh)"
file="${AGENTS_SHARED_ENV:-$HOME/.config/agents/shared.env}"
[ -r "$file" ] || exit 0
while IFS= read -r line || [ -n "$line" ]; do
  line="${line#"${line%%[![:space:]]*}"}"
  line="${line%"${line##*[![:space:]]}"}"
  case "$line" in '' | '#'*) continue ;; esac
  case "$line" in export[[:space:]]*)
    line="${line#export}"
    line="${line#"${line%%[![:space:]]*}"}" ;;
  esac
  case "$line" in *=*) ;; *) continue ;; esac
  key="${line%%=*}"
  key="${key%"${key##*[![:space:]]}"}"
  case "$key" in '' | [0-9]* | *[!A-Za-z0-9_]*) continue ;; esac
  value="${line#*=}"
  case "$value" in
    \"*\") value="${value#\"}"; value="${value%\"}" ;;
    \'*\') value="${value#\'}"; value="${value%\'}" ;;
  esac
  quoted=$(printf '%s' "$value" | sed "s/'/'\\\\''/g")
  printf "[ -n \"\${%s+x}\" ] || export %s='%s'\n" "$key" "$key" "$quoted"
done < "$file"
