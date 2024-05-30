from turbocase.parts import BasePart
from turbocase.parts.shape import Line, Circle, Arc, Rect


class CaseCorner(BasePart):
    """
    module CaseCorner(size, hole_diameter, head_diameter, head_height) {
        translate([0, 0, -floor_height])
        difference() {
            union() {
                cylinder(inner_height, size/2, size/2, $fn=32);
                translate([-size, 0, inner_height/2])
                    cube([size*2, size, inner_height], center=true);
            }

            cylinder(inner_height+1, hole_diameter/2, hole_diameter/2, $fn=32);

            translate([0, 0, floor_height])
                CaseCorner_substract(size, hole_diameter, head_diameter, head_height);
        }
    }

    module CaseCorner_substract(size, hole_diameter, head_diameter, head_height) {
        translate([0, 0, 0.11]) {
            cylinder(inner_height+floor_height, hole_diameter/2, hole_diameter/2, $fn=32);
            translate([0, 0, inner_height+floor_height-head_height])
                cylinder(head_height, hole_diameter/2, head_diameter/2, $fn=32);
        }
    }
    """
    _substract = True
    _add = True
    _constrain = True
    _hide = 'CaseCorner'
    description = "Corner screw mount for a screw-mount lid"
    size = 8
    hole_diameter = 0
    head_diameter = 0
    head_height = 0

    @classmethod
    def make_footprint(cls):
        return [
            # Screw hole
            Circle('User.6', [0, 0], [0, cls.hole_diameter / 2]),
            Circle('User.6', [0, 0], [0, cls.head_diameter / 2], style='dot'),

            # Shape
            Arc('User.6', [0, cls.size / 2], [0, -cls.size / 2], [0, cls.size / 2]),
            Line('User.6', [-cls.size, cls.size / 2], [0, cls.size / 2]),
            Line('User.6', [-cls.size, -cls.size / 2], [0, -cls.size / 2]),
        ]


class CaseCorner_M3(CaseCorner):
    description = "Corner screw mount for a screw-mount lid with an M3 sized screw"
    hole_diameter = 3
    head_diameter = 5.6
    head_height = 1.65
    size = head_diameter


class CaseCorner_M4(CaseCorner):
    description = "Corner screw mount for a screw-mount lid with an M4 sized screw"
    hole_diameter = 4
    head_diameter = 7.5
    head_height = 2.2
    size = head_diameter


class CasePost(BasePart):
    """
    module CasePost(size, hole_diameter, head_diameter, head_height) {
        difference() {
            cylinder(inner_height, size/2, size/2, $fn=32);
            cylinder(inner_height+1, hole_diameter/2, hole_diameter/2, $fn=32);
            CasePost_substract(size, hole_diameter, head_diameter, head_height);
        }
    }

    module CasePost_substract(size, hole_diameter, head_diameter, head_height) {
        translate([0, 0, 0.11]) {
            cylinder(inner_height+floor_height, hole_diameter/2, hole_diameter/2, $fn=32);
            translate([0, 0, inner_height+floor_height-head_height])
                cylinder(head_height, hole_diameter/2, head_diameter/2, $fn=32);
        }
    }
    """
    _substract = True
    _add = True
    _hide = 'CasePost'
    description = "Screw mount post for a screw-mount lid"
    size = 8
    hole_diameter = 0
    head_diameter = 0
    head_height = 0

    @classmethod
    def make_footprint(cls):
        return [
            # Screw hole
            Circle('User.6', [0, 0], [0, cls.hole_diameter / 2]),
            Circle('User.6', [0, 0], [0, cls.head_diameter / 2], style='dot'),

            # Shape
            Circle('User.6', [0, 0], [0, cls.size / 2]),
        ]


class CasePost_M3(CasePost):
    description = "Screw mount post for a screw-mount lid with an M3 sized screw"
    hole_diameter = 3
    head_diameter = 5.6
    head_height = 1.65
    size = head_diameter


class CasePost_M4(CasePost):
    description = "Screw mount post for a screw-mount lid with an M4 sized screw"
    hole_diameter = 4
    head_diameter = 7.5
    head_height = 2.2
    size = head_diameter
