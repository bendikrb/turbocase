from turbocase.parts import BasePart
from turbocase.parts.shape import Line, Circle, Arc, Rect


class Cutout_TypeC(BasePart):
    """
    module Cutout_TypeC_substract() {
        width = 10;
        length = 10;
        height = 3.5;
        translate([-length/2, 0, height/2])
        rotate([0,90,0])
            union() {
                translate([0, -(width/2 - height/2), 0])
                    cylinder(length, height/2, height/2, $fn=32);
                translate([0, (width/2 - height/2), 0])
                    cylinder(length, height/2, height/2, $fn=32);
                translate([0, 0, length/2])
                    cube([height, width-height, length], center=true);
            }
    }
    """
    _substract = True
    _add = False
    _pcb_height = True
    description = "Hole to fit the plug of a Type-C connector"

    @classmethod
    def make_footprint(cls):
        width = 10
        length = 10
        return [
            # Outline
            Rect('User.6', [-length / 2, -(width / 2)], [length / 2, width / 2]),
            Line('User.6', [-length, 0], [length, 0]),
        ]
