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

module lid(thickness, height) {
    linear_extrude(height) {
        offset(r=thickness)
            children();
    }
    translate([0,0,-thickness])
    difference() {
        linear_extrude(height) {
                offset(r=-0.2)
                children();
        }
        translate([0,0, -0.5])
         linear_extrude(height+1) {
                offset(r=-1.2)
                children();
        }
    }
}


module box(wall_thick, bottom_layers, height) {
    if (render == "all" || render == "case") {
        translate([0,0, bottom_layers])
            wall(wall_thick, height) children();
        bottom(wall_thick, bottom_layers) children();
    }
    
    if (render == "all" || render == "lid") {
        translate([0, 0, height+bottom_layers+0.1])
        lid(wall_thick, bottom_layers) children();
    }
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


def _make_pcb_module(case):
    result = 'module pcb() {\n'
    result += f'    thickness = {case.pcb_thickness};\n\n'
    result += '    color("#009900")\n'
    result += '    difference() {\n'
    result += f'        linear_extrude(thickness) ' + '{\n'
    result += '            ' + _make_scad_polygon(case.pcb_path)
    result += '        }\n'
    for shape in case.pcb_holes:
        if shape.is_circle:
            result += f'    translate([{shape.point[0]}, {shape.point[1]}, -1])\n'
            result += f'        cylinder(thickness+2, {shape.radius}, {shape.radius}, $fn=32);\n'
        elif shape.is_rect:
            result += f'    translate([{shape.point[0]}, {shape.point[1]}, 0])\n'
            result += f'        cube([{shape.width}, {shape.height}, thickness + 2], center=true);\n'
        else:
            result += f'    translate([0, 0, -1])\n'
            result += f'    linear_extrude(thickness+2) \n'
            result += f'        {_make_scad_polygon(shape.path())}\n'
    result += '    }\n'
    result += '}\n\n'
    return result


def _make_outline_module(case):
    result = 'module case_outline() {\n'
    result += '    ' + _make_scad_polygon(case.inner_path)
    result += '}\n\n'
    return result


def generate(case, show_pcb=False):
    """
    :type case: Case
    """
    lid_model = 'cap'
    result = '/* [Rendering options] */\n'
    result += '// Show placeholder PCB in OpenSCAD preview\n'
    result += 'show_pcb = ' + ('true' if show_pcb else 'false') + ';\n'
    result += '// Lid mounting method\n'
    result += f'lid_model = "{lid_model}"; // [cap]\n'
    result += '// Conditional rendering\n'
    result += f'render = "lid"; // [all, case, lid]\n'
    result += '\n\n'

    result += '/* [Dimensions] */\n'
    result += '// Height of the PCB mounting stand-offs between the bottom of the case and the PCB\n'
    result += f'standoff_height = {case.standoff_height};\n'
    result += f'// PCB thickness\n'
    result += f'pcb_thickness = {case.pcb_thickness};\n'
    result += f'// Bottom layer thickness\n'
    result += f'floor_height = {case.floor_thickness};\n'
    result += f'// Case wall thickness\n'
    result += f'wall_thickness = {case.wall_thickness};\n'
    result += f'// Space between the top of the PCB and the top of the case\n'
    result += f'headroom = {max(case.max_connector_height, case.max_part_height - case.standoff_height - case.pcb_thickness)};\n'

    result += '/* [Hidden] */\n\n'
    result += f'inner_height = floor_height + standoff_height + pcb_thickness + headroom;\n'

    result += _template.lstrip() + "\n"

    for m in case.modules:
        result += m + "\n"

    result += _make_pcb_module(case)
    result += _make_outline_module(case)

    center = case.get_center()
    result += f'rotate([render == "lid" ? 180 : 0, 0, 0])\n'
    result += f'scale([1, -1, 1])\n'
    result += f'translate([-{center[0]}, -{center[1]}, 0]) ' + '{\n'

    result += f'    pcb_top = floor_height + standoff_height + pcb_thickness;\n'
    result += '\n'
    result += '    difference() {\n'
    result += f'        box(wall_thickness, floor_height, inner_height) ' + '{\n'
    result += '            case_outline();\n'
    result += '        }\n\n'

    for shape in case.cutouts:
        if shape.is_circle:
            result += f'    translate([{shape.point[0]}, {shape.point[1]}, -1])\n'
            result += f'        #cylinder(floor_height+2, {shape.radius}, {shape.radius});\n'
        elif shape.is_rect:
            result += f'    translate([{shape.point[0]}, {shape.point[1]}, 0])\n'
            result += f'        #cube([{shape.width}, {shape.height}, floor_height + 2], center=true);\n'
        else:
            result += f'    translate([0, 0, -1])\n'
            result += f'    #linear_extrude(floor_height+2) \n'
            result += f'        {_make_scad_polygon(shape.path())}\n'


    for shape in case.lid_holes:
        if shape.is_circle:
            result += f'    translate([{shape.point[0]}, {shape.point[1]}, inner_height])\n'
            result += f'        cylinder(floor_height+2, {shape.radius}, {shape.radius}, $fn=32);\n'
        elif shape.is_rect:
            result += f'    translate([{shape.point[0]}, {shape.point[1]}, inner_height+floor_height])\n'
            result += f'        cube([{shape.width}, {shape.height}, floor_height + 2], center=true);\n'
        else:
            result += f'    translate([0, 0, inner_height])\n'
            result += f'    linear_extrude(floor_height+2) \n'
            result += f'        {_make_scad_polygon(shape.path())}\n'


    for conn in sorted(case.connectors, key=lambda x: x.reference):
        result += f'    // {conn.reference} {conn.footprint} {conn.description}\n'
        result += f'    translate([{conn.position[0]}, {conn.position[1]}, pcb_top])\n' \
                  f'    rotate([0, 0, {-conn.position[2]}])\n' \
                  f'        #connector({conn.bounds[0]},{conn.bounds[1]},{conn.bounds[2]},{conn.bounds[3]},{conn.prop_height + 0.2});\n\n'

    for part in case.parts:
        if part.substract is None:
            continue
        z = 'floor_height'
        if part.offset_pcb:
            z = 'pcb_top'
        result += f'    // {part.description}\n'
        result += f'    translate([{part.position[0]}, {part.position[1]}, {z}])\n'
        if len(part.position) == 3:
            result += f'    rotate([0, 0, {-part.position[2]}])\n'
        result += f'        {part.substract}\n'

    result += '    }\n\n'

    result += '    if (show_pcb && $preview) {\n'
    result += '        translate([0, 0, floor_height + standoff_height])\n'
    result += '            pcb();\n'
    result += '    }\n\n'

    result += '    if (render == "all" || render == "case") {\n'
    for mount in case.pcb_mount:
        result += f'        // {mount[3]}\n'
        result += f'        translate([{mount[0][0]}, {mount[0][1]}, floor_height])\n'
        # This currently creates correct holes for the M3 threaded metal inserts I have. Not generic
        result += f'        mount({mount[1] + 0.2}, {mount[2]}, standoff_height);\n\n'

    has_constrained = False
    for part in case.parts:
        if part.constrain:
            has_constrained = True
            break

    if has_constrained:
        result += '        intersection() {\n'
        result += '            translate([0, 0, floor_height])\n'
        result += '            linear_extrude(inner_height)\n'
        result += '                case_outline();\n\n'
        result += '            union() {\n\n'

        for part in case.parts:
            if not part.constrain:
                continue
            if part.add is None:
                continue

            z = 'floor_height'
            if part.offset_pcb:
                z = 'pcb_top'
            result += f'            // {part.description}\n'
            result += f'            translate([{part.position[0]}, {part.position[1]}, {z}])\n'
            if len(part.position) == 3:
                result += f'            rotate([0, 0, {-part.position[2]}])\n'
            result += f'                {part.add}\n\n'

        result += '            }\n'
        result += '        }\n'

    for part in case.parts:
        if part.add is None:
            continue
        if part.constrain:
            continue
        result += f'        // {part.description}\n'
        z = 'floor_height'
        if part.offset_pcb:
            z = 'pcb_top'
        result += f'        translate([{part.position[0]}, {part.position[1]}, {z}])\n'
        if len(part.position) == 3:
            result += f'        rotate([0, 0, {-part.position[2]}])\n'
        result += f'            {part.add}\n\n'

    result += '    }\n'
    result += '}\n'
    return result
