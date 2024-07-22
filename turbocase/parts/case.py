""" Generic case structural parts """
from turbocase.parts import BasePart
from turbocase.parts.shape import Line, Circle, Arc, Rect


class CaseCorner(BasePart):
    """
    module CaseCorner(size, hole_diameter, head_diameter, head_height) {
        translate([0, 0, -floor_height])
        difference() {
            union() {
                cylinder(inner_height, size/2, size/2);
                translate([-size, 0, inner_height/2])
                    cube([size*2, size, inner_height], center=true);
            }

            cylinder(inner_height+1, hole_diameter/2, hole_diameter/2);

            translate([0, 0, floor_height])
                CaseCorner_substract(size, hole_diameter, head_diameter, head_height);

            translate([0, 0, inner_height+0.01])
                children();

        }
    }

    module CaseCorner_substract(size, hole_diameter, head_diameter, head_height) {
        translate([0, 0, 0.11]) {
            cylinder(inner_height+floor_height, hole_diameter/2, hole_diameter/2);
            translate([0, 0, inner_height+floor_height-head_height])
                cylinder(head_height, hole_diameter/2, head_diameter/2);
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

    def get_screw_diameter(self):
        return self.hole_diameter


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
            cylinder(inner_height, size/2, size/2);
            cylinder(inner_height+1, hole_diameter/2, hole_diameter/2);
            CasePost_substract(size, hole_diameter, head_diameter, head_height);
        }
    }

    module CasePost_substract(size, hole_diameter, head_diameter, head_height) {
        translate([0, 0, 0.11]) {
            cylinder(inner_height+floor_height, hole_diameter/2, hole_diameter/2);
            translate([0, 0, inner_height+floor_height-head_height])
                cylinder(head_height, hole_diameter/2, head_diameter/2);
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


class SnapMount(BasePart):
    """
    module SnapMount() {
        size = 3;
        snap_size = 3;
        hang = 0.4;

        st = standoff_height+pcb_thickness+1;
        sh = standoff_height+pcb_thickness;
        sw = 1;
        snapper = [[0,0], [0, st], [sw, st], [sw+hang, sh], [sw, sh], [sw, 0]];
        rotate([0, 0, 180])
        translate([0, size-sw, 0]) {
            translate([-snap_size/2, -size, 0])
            rotate([90, 0, 90])
            linear_extrude(snap_size)
                polygon(snapper);

            translate([0, 0, standoff_height/2])
                cube([size, size, standoff_height], center=true);
        }
    }
    """
    description = "Snap-in mount for a PCB edge"

    @classmethod
    def make_footprint(cls):
        size = 3
        thick = 1
        return [
            # Outline
            Line('User.6', [-size, 0], [size, 0]),
            Rect('User.6', [-thick / 2, 0], [thick / 2, thick]),
        ]


class LidClip(BasePart):
    """
    module LidClip_substract() {
        size = 11;
        hang = 0.6;

        if(render == "case") {
            translate([0, 0, lid_model == "inner-fit" ? -headroom+4.5 : 0])
            translate([0, size/2, inner_height-1])
            rotate([90, 0, 0])
                cylinder(size, hang, hang);
        }
    }

    module LidClip_lid() {
        size = 10;
        r = 0.4;
        w = 0.99;

        translate([-0.2, 0, 0]) {

            if(render == "lid") {
                translate([0, 0, lid_model == "inner-fit" ? -headroom+4.5 : 0])
                translate([0, -size/2, inner_height-1]) {
                    translate([-w,0, -r])
                        cube([w, size-(r*2), r*2]);

                    translate([0, 0, 0])
                        rotate([90, 0, 0])
                        sphere(r);

                    translate([-w, 0, 0])
                        rotate([0, 90, 0])
                        cylinder(w, r, r);

                    translate([0, size-r*2, 0])
                        rotate([90, 0, 0])
                        sphere(r);

                    translate([-w, size-r*2, 0])
                        rotate([0, 90, 0])
                        cylinder(w, r, r);


                    rotate([-90, 0, 0])
                        cylinder(size-(r*2), r, r);
                }
            }
        }
    }
    """
    description = "Clip to snap the lid to the case, put this against the inside edge"
    _substract = True
    _lid = True
    _add = False

    @classmethod
    def make_footprint(cls):
        size = 10
        thick = 1
        return [
            # Outline
            Line('User.6', [-thick, -size / 2 + 1], [-thick, size / 2 - 1]),
            Line('User.6', [0, -size / 2], [0, size / 2]),
            Line('User.6', [-thick, -size / 2 + 1], [0, -size / 2]),
            Line('User.6', [-thick, size / 2 - 1], [0, size / 2]),
        ]
