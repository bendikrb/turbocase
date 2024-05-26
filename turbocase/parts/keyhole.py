from turbocase.parts import BasePart
from turbocase.parts.shape import Line, Circle, Arc


class KeyHole(BasePart):
    """
    module KeyHole_substract(hole_diameter, head_diameter, head_height) {
        margin = 0.2;
        translate([0,0,-10])
            union() {
                cylinder(15, (hole_diameter/2)+margin, (hole_diameter/2)+margin, $fn=32);

                translate([0, head_diameter/2, 7.5])
                    cube([hole_diameter+(2*margin), head_diameter, 15], center=true);

                translate([0, head_diameter, 0])
                    cylinder(15, (head_diameter/2)+margin, (head_diameter/2)+margin, $fn=32);
            }
    }
    module KeyHole(hole_diameter, head_diameter, head_height) {
        margin = 0.2;
        wall = 0.6;

        difference() {
            union() {
                cylinder(1, (head_diameter/2)+margin+wall, (head_diameter/2)+margin+wall, $fn=32);

                translate([0, head_diameter, 0])
                cylinder(1, (head_diameter/2)+margin+wall, (head_diameter/2)+margin+wall, $fn=32);

                translate([0, head_diameter/2, 0.5])
                    cube([(head_diameter)+(2*margin)+(2*wall), head_diameter, 1], center=true);
            }
            union() {
                translate([0, 0, -0.05])
                cylinder(1.1, (head_diameter/2)+margin, (head_diameter/2)+margin, $fn=32);

                translate([0, head_diameter, -0.05])
                cylinder(1.1, (head_diameter/2)+margin, (head_diameter/2)+margin, $fn=32);

                translate([0, head_diameter/2, 0.5])
                    cube([(head_diameter)+(2*margin), head_diameter, 1.1], center=true);
            }
        }
    }
    """
    _substract = True
    _add = True
    _hide = 'KeyHole'
    hole_diameter = 0
    head_diameter = 0
    head_height = 0

    @classmethod
    def make_footprint(cls):
        margin = 0.2
        wall = 0.6
        hole_radius = cls.hole_diameter / 2
        hd = cls.head_diameter + margin
        width = (cls.head_diameter / 2) + wall
        height = cls.head_diameter + wall * 2
        return [
            # Outline
            Arc('User.6', [-width, 0], [width, 0], [0, -width]),
            Arc('User.6', [-width, cls.head_diameter], [width, cls.head_diameter], [0, cls.head_diameter + width]),
            Line('User.6', [-width, 0], [-width, cls.head_diameter]),
            Line('User.6', [width, 0], [width, cls.head_diameter]),

            # Slot
            Arc('User.6', [-hole_radius, 0], [hole_radius, 0], [0, -hole_radius]),
            Line('User.6', [-hole_radius, 0], [-cls.hole_diameter / 2, hd]),
            Line('User.6', [cls.hole_diameter / 2, 0], [cls.hole_diameter / 2, hd]),
            Circle('User.6', [0, cls.head_diameter], [cls.head_diameter / 2, hd]),
        ]


class KeyHole_M3(KeyHole):
    hole_diameter = 3
    head_diameter = 5.6
    head_height = 1.65


class KeyHole_M4(KeyHole):
    hole_diameter = 4
    head_diameter = 7.5
    head_height = 2.2
