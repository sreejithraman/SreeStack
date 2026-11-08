#!/bin/sh
# Prints shell export lines for the agents' shared dotenv file, for runtimes
# such as Claude Code that do not load it themselves. Like Codex's .env loading,
# file values replace inherited ones, the last duplicate wins, and keys starting
# with CLAUDE_ are ignored. Use:
#   eval "$(sh load-env.sh)"
#
# Supported entries, one per line: KEY=value, with an optional `export ` prefix
# and optional whitespace around `=`. A value is empty, unquoted without
# whitespace or any of # " ' \ $, single-quoted with no inner ', or
# double-quoted with no inner " \ $. Nothing may follow a closing quote. Other
# entries export nothing and print a warning that names the key, not the value.
file="${AGENTS_SHARED_ENV:-$HOME/.config/agents/shared.env}"
[ -r "$file" ] || exit 0

warn() {
  printf 'load-env: %s:%s: %s; not exported\n' "$file" "$number" "$1" >&2
}

number=0
open_quote=
while IFS= read -r line || [ -n "$line" ]; do
  number=$((number + 1))
  if [ -n "$open_quote" ]; then
    case "$line" in *"$open_quote"*) open_quote= ;; esac
    continue
  fi
  line="${line#"${line%%[![:space:]]*}"}"
  line="${line%"${line##*[![:space:]]}"}"
  case "$line" in '' | '#'*) continue ;; esac
  case "$line" in export[[:space:]]*)
    line="${line#export}"
    line="${line#"${line%%[![:space:]]*}"}" ;;
  esac
  case "$line" in *=*) ;; *) warn "not a KEY=value entry"; continue ;; esac
  key="${line%%=*}"
  key="${key%"${key##*[![:space:]]}"}"
  case "$key" in
    '' | [0-9]* | *[!A-Za-z0-9_]*) warn "invalid key"; continue ;;
    [Cc][Ll][Aa][Uu][Dd][Ee]_*) continue ;;
  esac
  value="${line#*=}"
  value="${value#"${value%%[![:space:]]*}"}"
  case "$value" in
    [\"\']*)
      quote="${value%"${value#?}"}"
      inner="${value#?}"
      case "$inner" in
        *"$quote") inner="${inner%?}" ;;
        *"$quote"*) warn "$key: text after closing quote"; continue ;;
        *) open_quote="$quote"; warn "$key: unterminated or multiline quote"; continue ;;
      esac
      case "$quote$inner" in
        *"$quote"*"$quote"*) warn "$key: inner quote"; continue ;;
        \"*[\\\$]*) warn "$key: escape or substitution in double quotes"; continue ;;
      esac
      value="$inner" ;;
    *[[:space:]\#\"\'\\\$]*) warn "$key: unquoted value with whitespace, #, quote, \\ or \$"; continue ;;
  esac
  quoted=$(printf '%s' "$value" | sed "s/'/'\\\\''/g")
  printf "export %s='%s'\n" "$key" "$quoted"
done < "$file"
if [ -n "$open_quote" ]; then warn "quote never closed; later lines skipped"; fi
