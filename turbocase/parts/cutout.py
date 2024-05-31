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


class Cutout_HDMI_A(BasePart):
    """
    module Cutout_HDMI_A_substract(height) {
        width = 16;
        length = 10;
        a1 = height-1.4;
        a2 = 1;
        b2 = 1;
        translate([-length/2, -width/2, height+0.9])
        rotate([0,90,0])
            linear_extrude(length)
            offset(r=-0.5)
            offset(r=-0.5)
            offset(r=0.5)
            offset(r=0.5)
            polygon(points = [[0,0], [0,width], [a1,width],[a1, width-a2],[height, width-a2-b2],[height, a2+b2],[a1, a2], [a1, 0]]);
    }
    """
    _substract = True
    _add = False
    _pcb_height = True
    height = 5
    description = "Hole to fit the plug of a HDMI-A connector"

    @classmethod
    def make_footprint(cls):
        width = 16
        length = 10
        return [
            # Outline
            Rect('User.6', [-length / 2, -(width / 2)], [length / 2, width / 2]),
            Line('User.6', [-length, 0], [length, 0]),
        ]


class Cutout_HDMI_A_port(Cutout_HDMI_A):
    description = "Hole to fit the port of a HDMI-A connector"
    height = 6
