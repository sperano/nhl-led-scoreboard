#!/bin/bash

if [ -z "$VIRTUAL_ENV" ] || [ "$VIRTUAL_ENV" != "$HOME/nhlsb-venv" ]; then
  echo "Python virtual environment 'nhlsb-venv' not activated. Activating..."
  if [ -f "$HOME/nhlsb-venv/bin/activate" ]; then
    source "$HOME/nhlsb-venv/bin/activate"
  else
    echo "ERROR: Virtual environment activation script not found at $HOME/nhlsb-venv/bin/activate"
    exit 1
  fi
fi

ROOT=$(dirname "$(git rev-parse --git-dir)")
CURRENTLY_BUILT_VER=$(cat "${ROOT}"/VERSION) # stored somewhere, e.g. spec file in my case
LASTVER=$(lastversion falkyre/nhl-led-scoreboard -gt "${CURRENTLY_BUILT_VER}")
if [[ $? -eq 0 ]]; then
  # LASTVER is newer, update and trigger build
  # ....
  echo "New version V${LASTVER} available!! You are running V${CURRENTLY_BUILT_VER}"

else
  echo "You are running the latest version V${CURRENTLY_BUILT_VER}"
fi
