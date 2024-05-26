from turbocase.parts import BasePart
from turbocase.parts.shape import Circle


class ScrewHole(BasePart):
    """
    module ScrewHole_substract(hole_diameter, head_diameter) {
        translate([0,0,-10])
            cylinder(15, (hole_diameter/2)+0.2, (hole_diameter/2)+0.2, $fn=32);
    }
    module ScrewHole(hole_diameter, head_diameter) {
        difference() {
            cylinder(1, (head_diameter/2)+0.2, (head_diameter/2)+0.2, $fn=32);

            ScrewHole_substract(hole_diameter, head_diameter);
        }
    }
    """
    _substract = True
    _add = True
    _hide = 'ScrewHole'
    hole_diameter = 0
    head_diameter = 0

    @classmethod
    def make_footprint(cls):
        return [
            Circle('User.6', [0, 0], [0, cls.hole_diameter / 2]),
            Circle('User.6', [0, 0], [0, cls.head_diameter / 2]),
        ]


class ScrewHoleCountersunk(ScrewHole):
    """
    module ScrewHoleCountersunk_substract(hole_diameter, head_diameter, head_height) {
        translate([0,0,-head_height+1.2])
            cylinder(head_height, (hole_diameter/2)+0.2, (head_diameter/2)+0.2, $fn=32);

        translate([0,0, -10])
            cylinder(12, (hole_diameter/2)+0.2, (hole_diameter/2)+0.2, $fn=32);

    }
    module ScrewHoleCountersunk(hole_diameter, head_diameter, head_height) {
        difference() {
            cylinder(1, (head_diameter/2)+1.2, (head_diameter/2)+1.2, $fn=32);

            ScrewHoleCountersunk_substract(hole_diameter, head_diameter, head_height);
        }
    }
    """

    _substract = True
    _add = True
    _hide = 'ScrewHoleCountersunk'
    hole_diameter = 0
    head_diameter = 0
    head_height = 0

    @classmethod
    def make_footprint(cls):
        return [
            Circle('User.6', [0, 0], [0, cls.hole_diameter / 2]),
            Circle('User.6', [0, 0], [0, cls.head_diameter / 2]),
            Circle('User.6', [0, 0], [0, cls.head_diameter / 2 + 1.2]),
        ]


class ScrewHole_M3_DIN967(ScrewHole):
    description = "Hole for an M3 DIN967 standard pan-head screw (optical drive screw)"
    hole_diameter = 3
    head_diameter = 7


class ScrewHole_M4_DIN967(ScrewHole):
    description = "Hole for an M4 DIN967 standard pan-head screw"
    hole_diameter = 4
    head_diameter = 9


class ScrewHole_M5_DIN965_Countersunk(ScrewHoleCountersunk):
    description = "Hole for an M5 DIN965 standard countersunk screw"
    hole_diameter = 5
    head_diameter = 9.2
    head_height = 2.5


class ScrewHole_M4_DIN965_Countersunk(ScrewHoleCountersunk):
    description = "Hole for an M4 DIN965 standard countersunk screw"
    hole_diameter = 4
    head_diameter = 7.5
    head_height = 2.2


class ScrewHole_M3_DIN965_Countersunk(ScrewHoleCountersunk):
    description = "Hole for an M3 DIN965 standard countersunk screw"
    hole_diameter = 3
    head_diameter = 5.6
    head_height = 1.65


class ScrewHole_M25_DIN965_Countersunk(ScrewHoleCountersunk):
    description = "Hole for an M2.5 DIN965 standard countersunk screw"
    hole_diameter = 2.5
    head_diameter = 4.7
    head_height = 1.5


class ScrewHole_M2_DIN965_Countersunk(ScrewHoleCountersunk):
    description = "Hole for an M2 DIN965 standard countersunk screw"
    hole_diameter = 2
    head_diameter = 3.8
    head_height = 1.2


class ScrewHole_M16_DIN965_Countersunk(ScrewHoleCountersunk):
    description = "Hole for an M1.6 DIN965 standard countersunk screw"
    hole_diameter = 1.6
    head_diameter = 3
    head_height = 0.96
