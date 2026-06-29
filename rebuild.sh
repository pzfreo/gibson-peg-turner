#!/usr/bin/env bash
#
# rebuild.sh — regenerate CAD from source, then slice + pack every plate.
#
#   1. Removes stale estampo_output/ build dirs.
#   2. For each print config: rebuilds its source part(s), and ONLY if that
#      build succeeds, runs `estampo run` (load → arrange → plate → slice →
#      pack). A failed source build SKIPS its slice so estampo never packages
#      stale geometry.
#   3. Rebuilds the remaining (non-print) parts for completeness.
#
# Profiles are pinned per-config (profiles/), so slicing is reproducible.
#
# External deps:
#   * tuner_case*.py need the pip-hinge package        (pip install pip-hinge)
#   * marking_template.py needs sibling gib-tuners-mk2 (env: GIB_TUNERS_MK2)

set -uo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO"

fail=0

run_script() {  # $1 = path to a build123d script; returns its exit status
  echo "  - $1"
  ( cd "$(dirname "$1")" && python "$(basename "$1")" )
}

echo "==> Cleaning old estampo outputs"
rm -rf ./*/estampo_output

# config-dir | source script that must rebuild before slicing
PRINTS=(
  "peg-turner|peg-turner/peg_turner.py"
  "tuner-case|tuner-case/tuner_case_v2.py"
  "tuner-jig|tuner-jig/tuner_jig.py"
)

echo "==> Rebuilding print parts, then slicing + packing"
for entry in "${PRINTS[@]}"; do
  dir="${entry%%|*}"; src="${entry##*|}"
  if run_script "$src"; then
    echo "    -> estampo run ($dir)"
    if ! ( cd "$dir" && estampo run estampo.toml ); then
      echo "    !! estampo FAILED: $dir"; fail=1
    fi
  else
    echo "    !! build FAILED: $src — SKIPPING estampo for '$dir' (won't slice stale geometry)"
    fail=1
  fi
done

# Parts not consumed by any estampo config — rebuilt for completeness only.
EXTRAS=(
  "peg-turner/peg_turner_drill.py"
  "marking-template/marking_template.py"
  "tuner-case/tuner_case.py"
)

echo "==> Rebuilding remaining (non-print) parts"
for src in "${EXTRAS[@]}"; do
  if ! run_script "$src"; then
    echo "    !! build FAILED: $src"; fail=1
  fi
done

if [ "$fail" -eq 0 ]; then
  echo "==> Done — all builds and prints succeeded."
else
  echo "==> Done WITH FAILURES (see !! lines above)."
fi
exit "$fail"
