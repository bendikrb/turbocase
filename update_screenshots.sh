#!/bin/sh

python3 -m turbocase test-boards/demo.kicad_pcb case.scad
openscad -o images/scad.png --colorscheme "Tomorrow Night" --imgsize 930,700 --viewall --autocenter case.scad

kicad-cli pcb export pdf -o case.pdf ./test-boards/demo.kicad_pcb --layers In1.Cu,F.Cu,Edge.Cuts,User.6,User.7,F.Silkscreen,F.Fab,F.Courtyard
convert -density 600 -resize 930x case.pdf[0] -quality 90 images/kicad.png
mogrify -background '#001029' -flatten images/kicad.png

rm -rf case.scad case.pdf