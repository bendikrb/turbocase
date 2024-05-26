from turbocase.parts import BasePart
from turbocase.parts.shape import Rect


class BatteryHolder_Cylindrical(BasePart):
    """
    module BatteryHolder_Cylindrical(diameter, length) {
        length = length/10;
        border = 3.5;
        bs = 1;
        union() {
            difference() {
                cube([diameter+(2*bs), length+(2*border), diameter/2]);

                rotate([-90, 0, 0])
                translate([diameter/2+bs, -(diameter/2), border])
                cylinder(length, diameter/2, diameter/2, $fn=48);
            }

            translate([diameter/2+bs, 0, diameter/2])
            rotate([-90, 0, 0])
            cylinder(border, diameter/2, diameter/2, $fn=48);

            translate([diameter/2+bs, length+border, diameter/2])
            rotate([-90, 0, 0])
            cylinder(border, diameter/2, diameter/2, $fn=48);
        }
    }
    """
    diameter = 0
    length = 0
    _hide = 'BatteryHolder_Cylindrical'

    @classmethod
    def make_footprint(cls):
        off_h = 3.5
        off_v = 1
        length = cls.length / 10
        return [
            Rect('User.6', [0, 0], [cls.diameter + (2 * off_v), length + (2 * off_h)]),
            Rect('User.6', [off_v, off_h], [off_v + cls.diameter, off_h + length]),
        ]


class BatteryHolder_18650(BatteryHolder_Cylindrical):
    description = "3D Printed 18650 battery holder"
    diameter = 18
    length = 650


class BatteryHolder_18650_Protected(BatteryHolder_18650):
    description = "3D Printed 18650 battery holder for slightly longer protected cells"
    length = 670
    dummy = 42
