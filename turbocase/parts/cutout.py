""" Ready to use connector cutouts for connectors with complicated shapes """
from turbocase.parts import BasePart
from turbocase.parts.shape import Line, Circle, Arc, Rect, Text


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
                    cylinder(length, height/2, height/2);
                translate([0, (width/2 - height/2), 0])
                    cylinder(length, height/2, height/2);
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

    def get_part_height(self):
        return 3.5


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

    def get_part_height(self):
        return self.height


class Cutout_HDMI_A_port(Cutout_HDMI_A):
    description = "Hole to fit the port of a HDMI-A connector"
    height = 6


class Cutout_Pinheader(BasePart):
    """
    module Cutout_Pinheader_substract(width, height) {
        translate([0, 0, height/2+0.1])
            cube([10, width+0.2, height+0.2], center=true);
    }
    """
    _substract = True
    _add = False
    _pcb_height = True
    _hide = 'Cutout_Pinheader'
    width = 2.54
    height = 2.54
    description = "Cutout for horizontal 2.54mm header"

    @classmethod
    def make_footprint(cls):
        width = cls.width
        length = 10
        return [
            # Outline
            Rect('User.6', [-length / 2, -(width / 2)], [length / 2, width / 2]),
            Line('User.6', [-length, 0], [length, 0]),
        ]

    def get_part_height(self):
        return self.height


class Cutout_Pinheader_01x01_254(Cutout_Pinheader):
    width = 2.54 * 1
    height = 2.54 * 1
    description = f'Cutout for horizontal 2.54mm {width}x{height} pinheader'


class Cutout_Pinheader_01x02_254(Cutout_Pinheader):
    width = 2.54 * 2
    height = 2.54 * 1
    description = f'Cutout for horizontal 2.54mm {width}x{height} pinheader'


class Cutout_Pinheader_01x03_254(Cutout_Pinheader):
    width = 2.54 * 3
    height = 2.54 * 1
    description = f'Cutout for horizontal 2.54mm {width}x{height} pinheader'


class Cutout_Pinheader_01x04_254(Cutout_Pinheader):
    width = 2.54 * 4
    height = 2.54 * 1
    description = f'Cutout for horizontal 2.54mm {width}x{height} pinheader'


class Cutout_Pinheader_01x05_254(Cutout_Pinheader):
    width = 2.54 * 5
    height = 2.54 * 1
    description = f'Cutout for horizontal 2.54mm {width}x{height} pinheader'


class Cutout_Pinheader_01x06_254(Cutout_Pinheader):
    width = 2.54 * 6
    height = 2.54 * 1
    description = f'Cutout for horizontal 2.54mm {width}x{height} pinheader'


class Cutout_Pinheader_01x07_254(Cutout_Pinheader):
    width = 2.54 * 7
    height = 2.54 * 1
    description = f'Cutout for horizontal 2.54mm {width}x{height} pinheader'


class Cutout_Pinheader_01x08_254(Cutout_Pinheader):
    width = 2.54 * 8
    height = 2.54 * 1
    description = f'Cutout for horizontal 2.54mm {width}x{height} pinheader'


class Cutout_Pinheader_01x09_254(Cutout_Pinheader):
    width = 2.54 * 9
    height = 2.54 * 1
    description = f'Cutout for horizontal 2.54mm {width}x{height} pinheader'


class Cutout_Pinheader_01x10_254(Cutout_Pinheader):
    width = 2.54 * 10
    height = 2.54 * 1
    description = f'Cutout for horizontal 2.54mm {width}x{height} pinheader'


class Cutout_Pinheader_02x01_254(Cutout_Pinheader):
    width = 2.54 * 1
    height = 2.54 * 2
    description = f'Cutout for horizontal 2.54mm {width}x{height} pinheader'


class Cutout_Pinheader_02x02_254(Cutout_Pinheader):
    width = 2.54 * 2
    height = 2.54 * 2
    description = f'Cutout for horizontal 2.54mm {width}x{height} pinheader'


class Cutout_Pinheader_02x03_254(Cutout_Pinheader):
    width = 2.54 * 3
    height = 2.54 * 2
    description = f'Cutout for horizontal 2.54mm {width}x{height} pinheader'


class Cutout_Pinheader_02x04_254(Cutout_Pinheader):
    width = 2.54 * 4
    height = 2.54 * 2
    description = f'Cutout for horizontal 2.54mm {width}x{height} pinheader'


class Cutout_Pinheader_02x05_254(Cutout_Pinheader):
    width = 2.54 * 5
    height = 2.54 * 2
    description = f'Cutout for horizontal 2.54mm {width}x{height} pinheader'


class Cutout_Pinheader_02x06_254(Cutout_Pinheader):
    width = 2.54 * 6
    height = 2.54 * 2
    description = f'Cutout for horizontal 2.54mm {width}x{height} pinheader'


class Cutout_Pinheader_02x07_254(Cutout_Pinheader):
    width = 2.54 * 7
    height = 2.54 * 2
    description = f'Cutout for horizontal 2.54mm {width}x{height} pinheader'


class Cutout_Pinheader_02x08_254(Cutout_Pinheader):
    width = 2.54 * 8
    height = 2.54 * 2
    description = f'Cutout for horizontal 2.54mm {width}x{height} pinheader'


class Cutout_Pinheader_02x09_254(Cutout_Pinheader):
    width = 2.54 * 9
    height = 2.54 * 2
    description = f'Cutout for horizontal 2.54mm {width}x{height} pinheader'


class Cutout_Pinheader_02x10_254(Cutout_Pinheader):
    width = 2.54 * 10
    height = 2.54 * 2
    description = f'Cutout for horizontal 2.54mm {width}x{height} pinheader'


class Cutout_Neutrik_DSeries(BasePart):
    """
    module Cutout_Neutrik_DSeries_substract() {
        r = 22/2;
        rs = 3.2/2;

        translate([-5, 0, r+1.5])
        rotate([0, 90, 0])
            cylinder(10, r, r);

        translate([-5, -19.8/2, 1.5+r+19.8/2])
        rotate([0, 90, 0])
            cylinder(10, rs, rs);

        translate([-5, 19.8/2, 1.5+r-19.8/2])
        rotate([0, 90, 0])
            cylinder(10, rs, rs);
    }
    """
    _substract = True
    _add = False
    _pcb_height = True
    description = "Chassis hole for a Neutrik D Series panel mount connector"

    @classmethod
    def make_footprint(cls):
        width = 23
        length = 10
        return [
            # Outline
            Rect('User.6', [-length / 2, -(width / 2)], [length / 2, width / 2]),
            Line('User.6', [-length, 0], [length, 0]),
            Text('User.6', [-length / 2, 0, 90], 'D Series front', justify_h='middle'),
        ]

    def get_part_height(self):
        return 26


class Cutout_CUI_SJ1_353x(BasePart):
    """
    module Cutout_CUI_SJ1_353x_substract() {
        r = 6.5/2;
        translate([-5, 0, 7])
        rotate([0, 90, 0])
            cylinder(10, r, r);
    }
    """
    _substract = True
    _add = False
    _pcb_height = True
    description = "Chassis hole for a CUI SJ1-353x 3.5mm jack"

    @classmethod
    def make_footprint(cls):
        width = 6.5
        length = 10
        return [
            # Outline
            Rect('User.6', [-length / 2, -(width / 2)], [length / 2, width / 2]),
            Line('User.6', [-length, 0], [length, 0]),
        ]

    def get_part_height(self):
        return 26
