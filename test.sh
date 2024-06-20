#!/bin/sh
set -euo pipefail
for file in test-boards/*.kicad_pcb; do
  echo "testing $file..."
  turbocase --verbose "$file" out.scad
done