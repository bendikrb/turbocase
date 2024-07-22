""" Battery mounting parts """
from turbocase.parts import BasePart
from turbocase.parts.shape import Rect, Text


class BatteryHolder_Cylindrical(BasePart):
    """
    module BatteryHolder_Cylindrical(diameter, length) {
        length = length/10 + 1;
        border = 3.5;
        bs = 1;
        grip=12;
        difference() {
            union() {
                difference() {
                    cube([diameter+(2*bs), length+(2*border), diameter/2]);

                    rotate([-90, 0, 0])
                    translate([diameter/2+bs, -(diameter/2), border])
                    cylinder(length, diameter/2, diameter/2);
                }

                translate([diameter/2+bs, 0, diameter/2])
                rotate([-90, 0, 0])
                cylinder(border, diameter/2, diameter/2);

                translate([diameter/2+bs, length+border, diameter/2])
                rotate([-90, 0, 0])
                cylinder(border, diameter/2, diameter/2);
            }

            translate([0, -0.005, diameter*0.75])
                cube([diameter+(2*bs), length+(2*border)+0.01, diameter/2]);

            translate([diameter/2+bs, border/2, diameter])
                cube([diameter*0.75, border/2, diameter*1.7], center=true);

            translate([diameter/2+bs, border/2+length+border, diameter])
                cube([diameter*0.75, border/2, diameter*1.7], center=true);

            translate([diameter/2+bs, 0, diameter*0.75])
                cube([1, border, diameter*1.7], center=true);
            translate([diameter/2+bs, length+border*2, diameter*0.75])
                cube([1, border, diameter*1.7], center=true);

            translate([diameter/2+bs, length/2+border, diameter/2-1])
                cube([diameter+border, length-(grip*2), diameter], center=true);

            translate([diameter/2+bs, border+(grip/2)-0.6, diameter/2-1])
                cube([diameter, grip-1.2, diameter], center=true);

            translate([diameter/2+bs, border-(grip/2)+1.2 + length, diameter/2-1])
                cube([diameter, grip-1.2, diameter], center=true);
        }
    }
    """
    diameter = 0
    length = 0
    _hide = 'BatteryHolder_Cylindrical'
    _name = '18650'
    _desc = 'unprotected'

    @classmethod
    def make_footprint(cls):
        off_h = 3.5
        off_v = 1
        length = cls.length / 10 + 1
        return [
            Rect('User.6', [0, 0], [cls.diameter + (2 * off_v), length + (2 * off_h)]),
            Rect('User.6', [off_v, off_h], [off_v + cls.diameter, off_h + length]),
            Text('User.6', [cls.diameter / 2 - 1, length / 2 + off_h, 90], cls._name, size=3, justify_h='middle',
                 justify_v='bottom'),
            Text('User.6', [cls.diameter / 2 + 1, length / 2 + off_h, 90], cls._desc, size=2, justify_h='middle',
                 justify_v='top'),
        ]

    def get_part_height(self):
        return self.diameter + 0.5


class BatteryHolder_18650(BatteryHolder_Cylindrical):
    description = "3D Printed 18650 button-top cell holder"
    diameter = 18
    length = 650
    _name = '18650'
    _desc = 'Unprotected'


class BatteryHolder_18650_Protected(BatteryHolder_18650):
    description = "3D Printed 18650 button-top cell holder for slightly longer protected cells"
    length = 700
    _name = '18650'
    _desc = 'Protected'


class BatteryHolder_18650_Keystone289(BatteryHolder_18650):
    description = "3D Printed 18650 button-top cell holder. Mounted by a Keystone 289 and 228 spring contact"
    length = 650 + 80
    _name = '18650'
    _desc = 'Unprotected, Keystone 289'


class BatteryHolder_18650_Protected_Keystone289(BatteryHolder_18650):
    description = "3D Printed 18650 button-top cell holder for protected cells. Mounted by a Keystone 289 and 228 spring contact"
    length = 700 + 80
    _name = '18650'
    _desc = 'Protected, Keystone 289'
