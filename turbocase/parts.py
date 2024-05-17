def BatteryHolder_18650():
    """
    module BatteryHolder_cylindrical(diameter, length10) {
        length = length10/10;
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
    return 'BatteryHolder_cylindrical(18, 670);'
