_template = """

module wall (thickness, height) {
    linear_extrude(height) {
        difference() {
            offset(r=thickness)
                children();
            children();
        }
    }
}

module bottom(thickness, height) {
    linear_extrude(height) {
        offset(r=thickness)
            children();
    }
}

module box(wall_thick, bottom_layers, height) {
    
    translate([0,0, bottom_layers])
        wall(wall_thick, height) children();
    bottom(wall_thick, bottom_layers) children();
}

module mount(drill, space, height) {
    translate([0,0,height/2])
        difference() {
            cylinder(h=height, r=(space/2), center=true, $fn=32);
            cylinder(h=(height*2), r=(drill/2), center=true, $fn=32);
        }
}

module connector(min_x, min_y, max_x, max_y, height) {
    size_x = max_x - min_x;
    size_y = max_y - min_y;
    translate([(min_x + max_x)/2, (min_y + max_y)/2, height/2])
        cube([size_x, size_y, height], center=true);
}
"""


def _make_scad_polygon(points):
    result = 'polygon(points = ['
    parts = []
    for p in points:
        parts.append(f'[{p[0]},{p[1]}]')
    result += ', '.join(parts)
    result += ']);\n'
    return result


def generate(case):
    """
    :type case: Case
    """

    result = _template + "\n"

    for m in case.modules:
        result += m + "\n"

    center = case.get_center()
    result += f'translate([-{center[0]}, -{center[1]}, 0]) ' + '{\n'

    result += f'    standoff_height = 5;\n'
    result += f'    floor_height = {case.floor_thickness};\n'
    result += f'    pcb_thickness = {case.pcb_thickness};\n'
    result += f'    inner_height = standoff_height + pcb_thickness + {case.max_connector_height};\n'
    result += f'    pcb_top = floor_height + standoff_height + pcb_thickness;\n'
    result += '\n'
    result += '    difference() {\n'
    result += f'        box({case.wall_thickness}, {case.floor_thickness}, inner_height) ' + '{\n'
    result += '            ' + _make_scad_polygon(case.inner_path)
    result += '        }\n\n'

    for conn in sorted(case.connectors, key=lambda x: x.reference):
        result += f'    // {conn.reference} {conn.footprint} {conn.description}\n'
        result += f'    translate([{conn.position[0]}, {conn.position[1]}, pcb_top])\n' \
                  f'    rotate([0, 0, {conn.position[2] + 180}])\n' \
                  f'        #connector({conn.bounds[0]},{conn.bounds[1]},{conn.bounds[2]},{conn.bounds[3]},{conn.prop_height + 0.2});\n\n'

    result += '    }\n\n'

    for mount in case.pcb_mount:
        result += f'    // {mount[3]}\n'
        result += f'    translate([{mount[0][0]}, {mount[0][1]}, {case.floor_thickness}])\n'
        # This currently creates correct holes for the M3 threaded metal inserts I have. Not generic
        result += f'    mount({mount[1] + 0.2}, {mount[2]}, 5);\n\n'

    for part in case.parts:
        result += f'    translate([{part.position[0]}, {part.position[1]}, {case.floor_thickness}])\n'
        result += f'        {part.script}\n'

    result += '}\n'
    return result
