#!/bin/sh
# Prints shell export lines for the agents' shared dotenv file, for runtimes
# such as Claude Code that do not load it themselves. Like Codex's .env loading,
# file values replace inherited ones, the last duplicate wins, and keys starting
# with CLAUDE_ are ignored. Use:
#   eval "$(sh load-env.sh)"
#
# The file is UTF-8 text without NUL bytes that ends with a newline. Each line
# is blank, a # comment, or KEY=value with an optional `export ` prefix and
# optional whitespace around `=`. A value is empty, unquoted ASCII without
# whitespace or any of # " ' \ $, single-quoted without ' or \, or double-quoted
# without " \ $. Any other line makes the loader export nothing and print one
# warning that names the line, never the value.
LC_ALL=C
export LC_ALL
file="${AGENTS_SHARED_ENV:-$HOME/.config/agents/shared.env}"
[ -r "$file" ] || exit 0

# Rejects the whole file; the warning names where, never a value.
reject() {
  printf 'load-env: %s: %s; nothing exported\n' "$where" "$1" >&2
  exit 0
}

where="$file"
# macOS iconv accepts lead bytes F5-FF and code points above U+10FFFF, which
# tr and sed reject here.
if [ "$(tr -d '\000\365-\377' < "$file" | wc -c)" -ne "$(wc -c < "$file")" ] ||
  [ -n "$(sed -n "/$(printf '\364[\220-\277]')/=" "$file")" ] ||
  ! iconv -f UTF-8 -t UTF-8 < "$file" > /dev/null 2>&1; then
  reject "not UTF-8 text without NUL bytes"
fi

exports=
number=0
while { IFS= read -r line && unterminated=; } || { unterminated=1; [ -n "$line" ]; }; do
  number=$((number + 1))
  where="$file:$number"
  if [ -n "$unterminated" ]; then
    case "$line" in *[[:space:]]) reject "whitespace at end of file without a final newline" ;; esac
  fi
  line="${line#"${line%%[![:space:]]*}"}"
  line="${line%"${line##*[![:space:]]}"}"
  case "$line" in '' | '#'*) continue ;; esac
  case "$line" in export[[:space:]]*)
    line="${line#export}"
    line="${line#"${line%%[![:space:]]*}"}" ;;
  esac
  case "$line" in *=*) ;; *) reject "not a KEY=value entry" ;; esac
  key="${line%%=*}"
  key="${key%"${key##*[![:space:]]}"}"
  value="${line#*=}"
  value="${value#"${value%%[![:space:]]*}"}"
  case "$key" in '' | [0-9]* | *[!A-Za-z0-9_]*) reject "invalid key" ;; esac
  case "$value" in
    \'*\')
      value="${value#?}"
      value="${value%?}"
      case "$value" in *[\'\\]*) reject "' or \\ inside single quotes" ;; esac ;;
    \"*\")
      value="${value#?}"
      value="${value%?}"
      case "$value" in *[\"\\\$]*) reject "\", \\ or \$ inside double quotes" ;; esac ;;
    *[[:space:]\#\"\'\\\$]*) reject "unquoted value with whitespace, #, a quote, \\ or \$" ;;
    *[![:print:]]*) reject "unquoted value with a non-ASCII or control character" ;;
  esac
  case "$key" in [Cc][Ll][Aa][Uu][Dd][Ee]_*) continue ;; esac
  quoted=$(printf '%s' "$value" | sed "s/'/'\\\\''/g")
  exports="${exports}export $key='$quoted'
"
done < "$file"
printf '%s' "$exports"
