#!/usr/bin/env bash
set -euo pipefail

# Ejecuta la suite de tests dentro del contenedor Docker
docker compose run --rm algorithm pytest -v
