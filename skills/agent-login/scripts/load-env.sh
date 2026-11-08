#!/bin/sh
# Prints shell export lines for the agents' shared dotenv file, for runtimes
# such as Claude Code that do not load it themselves. Like Codex's .env loading,
# file values replace inherited ones, the last duplicate wins, and keys starting
# with CLAUDE_ are ignored. Use:
#   eval "$(sh load-env.sh)"
#
# Supported entries, one per line: KEY=value, with an optional `export ` prefix
# and optional whitespace around `=`. A value is empty, unquoted without
# whitespace or any of # $, single-quoted with no inner ', or double-quoted with
# no inner " or $. The closing quote ends the line. Keys and unquoted values
# are ASCII. A last line without a final newline may not end in whitespace.
#
# A backslash, or a quote anywhere but around a whole value, can make dotenv
# parsers disagree on where entries end, so such a line exports nothing from the
# whole file. Any other unsupported entry is skipped. Each warning names the
# line, and the key when it is known, never the value.
LC_ALL=C
export LC_ALL
file="${AGENTS_SHARED_ENV:-$HOME/.config/agents/shared.env}"
[ -r "$file" ] || exit 0

warn() {
  printf 'load-env: %s:%s: %s\n' "$file" "$number" "$1" >&2
}

# Calls "$1" with each line that is neither blank nor a comment, trimmed.
# Sets open_end when the last line has no newline and ends in whitespace.
each_entry() {
  number=0
  while { IFS= read -r line && open_end=; } || {
    case "$line" in *[[:space:]]) open_end=1 ;; *) open_end= ;; esac
    [ -n "$line" ]
  }; do
    number=$((number + 1))
    line="${line#"${line%%[![:space:]]*}"}"
    line="${line%"${line##*[![:space:]]}"}"
    case "$line" in '' | '#'*) continue ;; esac
    "$1" "$line"
  done < "$file"
}

# Sets key and value from an entry; fails when it has no `=`.
split_entry() {
  entry="$1"
  case "$entry" in export[[:space:]]*)
    entry="${entry#export}"
    entry="${entry#"${entry%%[![:space:]]*}"}" ;;
  esac
  case "$entry" in *=*) ;; *) return 1 ;; esac
  key="${entry%%=*}"
  key="${key%"${key##*[![:space:]]}"}"
  value="${entry#*=}"
  value="${value#"${value%%[![:space:]]*}"}"
}

has_clear_boundary() {
  case "$1" in *\\*) return 1 ;; *[\"\']*) ;; *) return 0 ;; esac
  split_entry "$1" || return 1
  case "$key" in *[\"\']*) return 1 ;; esac
  quote="${value%"${value#?}"}"
  case "$quote" in \" | \') ;; *) return 1 ;; esac
  inner="${value#?}"
  case "$inner" in *"$quote") inner="${inner%?}" ;; *) return 1 ;; esac
  case "$inner" in *"$quote"*) return 1 ;; esac
}

require_clear_boundary() {
  has_clear_boundary "$1" && return
  warn "backslash or quote outside a whole value; nothing exported from this file"
  exit 0
}

export_entry() {
  if [ -n "$open_end" ]; then
    warn "whitespace at end of file without a final newline; not exported"
    return
  fi
  if ! split_entry "$1"; then warn "not a KEY=value entry; not exported"; return; fi
  case "$key" in
    '' | [0-9]* | *[!A-Za-z0-9_]*) warn "invalid key; not exported"; return ;;
    [Cc][Ll][Aa][Uu][Dd][Ee]_*) return ;;
  esac
  case "$value" in
    \"*)
      value="${value#?}"
      value="${value%?}"
      case "$value" in *\$*) warn "$key: \$ in double quotes; not exported"; return ;; esac ;;
    \'*)
      value="${value#?}"
      value="${value%?}" ;;
    *[[:space:]\#\$]*) warn "$key: unquoted value with whitespace, # or \$; not exported"; return ;;
    *[![:print:]]*) warn "$key: unquoted value with a non-ASCII or control character; not exported"; return ;;
  esac
  quoted=$(printf '%s' "$value" | sed "s/'/'\\\\''/g")
  printf "export %s='%s'\n" "$key" "$quoted"
}

each_entry require_clear_boundary
each_entry export_entry
