import logging

_template = """
module wall (thickness, height) {
    linear_extrude(height, convexity=10) {
        difference() {
            offset(r=thickness)
                children();
            children();
        }
    }
}

module bottom(thickness, height) {
    linear_extrude(height, convexity=3) {
        offset(r=thickness)
            children();
    }
}

module lid(thickness, height, edge) {
    linear_extrude(height, convexity=10) {
        offset(r=thickness)
            children();
    }
    translate([0,0,-edge])
    difference() {
        linear_extrude(edge, convexity=10) {
                offset(r=-0.2)
                children();
        }
        translate([0,0, -0.5])
         linear_extrude(edge+1, convexity=10) {
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
        lid(wall_thick, bottom_layers, lid_model == "inner-fit" ? headroom-2.5: bottom_layers) 
            children();
    }
}

module mount(drill, space, height) {
    translate([0,0,height/2])
        difference() {
            cylinder(h=height, r=(space/2), center=true);
            cylinder(h=(height*2), r=(drill/2), center=true);
            
            translate([0, 0, height/2+0.01])
                children();
        }
        
}

module connector(min_x, min_y, max_x, max_y, height) {
    size_x = max_x - min_x;
    size_y = max_y - min_y;
    translate([(min_x + max_x)/2, (min_y + max_y)/2, height/2])
        cube([size_x, size_y, height], center=true);
}
"""


def esc(inp):
    return inp.replace('.', '_')


def _make_scad_polygon(points, label):
    if len(points) == 0:
        log = logging.getLogger('scad')
        log.error(f'Shape "{label}" had no points')
        return 'circle();'

    if points[0] == 'circle':
        return f'translate([{points[1][0]}, {points[1][0]}, 0]) circle(r={points[2]});'

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
    result += '            ' + _make_scad_polygon(case.pcb_path, 'edge.cuts')
    result += '        }\n'
    for shape in case.pcb_holes:
        if shape.is_circle:
            result += f'    translate([{shape.point[0]}, {shape.point[1]}, -1])\n'
            result += f'        cylinder(thickness+2, {shape.radius}, {shape.radius});\n'
        elif shape.is_rect:
            result += f'    translate([{shape.point[0]}, {shape.point[1]}, 0])\n'
            result += f'        cube([{shape.width}, {shape.height}, thickness + 2], center=true);\n'
        else:
            result += f'    translate([0, 0, -1])\n'
            result += f'    linear_extrude(thickness+2) \n'
            result += f'        {_make_scad_polygon(shape.path(), "pcb hole")}\n'
    result += '    }\n'
    result += '}\n\n'
    return result


def _make_outline_module(case):
    result = 'module case_outline() {\n'
    result += '    ' + _make_scad_polygon(case.inner_path, 'case outline')
    result += '}\n\n'
    return result


def _make_insert_parameters(insert):
    result = f'/* [{insert[0]} screws] */\n'
    result += '// Outer diameter for the insert\n'
    # 0.77 is added partially as a sane-ish default, but also to force OpenSCAD to allow 2 positions of floating point
    # precision in the customizer for this value
    result += f'insert_{esc(insert[0])}_diameter = {insert[1] + 0.77};\n'
    result += '// Depth of the insert\n'
    result += f'insert_{esc(insert[0])}_depth = {insert[1] * 1.5};\n'
    result += '\n'
    return result


def _make_insert_module(insert):
    insert = esc(insert)
    result = f'module Insert_{insert}() ' + '{\n'
    result += f'    translate([0, 0, -insert_{insert}_depth])\n'
    result += f'        cylinder(insert_{insert}_depth, insert_{insert}_diameter/2, insert_{insert}_diameter/2);\n'

    result += f'    translate([0, 0, -0.3])\n'
    result += f'        cylinder(0.3, insert_{insert}_diameter/2, insert_{insert}_diameter/2+0.3);\n'

    result += '}\n\n'
    return result


def _make_part(part, indent, substract=False, lid=False):
    s = 'Substract: ' if substract else ''
    result = f'{indent}// {s}{part.description}\n'
    z = 'floor_height'
    if part.offset_pcb:
        z = 'pcb_top'
    result += f'{indent}translate([{part.position[0]}, {part.position[1]}, {z}])\n'
    if len(part.position) == 3:
        result += f'{indent}rotate([0, 0, {-part.position[2]}])\n'
    if substract:
        result += f'{indent}    {part.substract};\n\n'
    elif lid:
        result += f'{indent}    {part.lid};\n\n'
    else:
        if part.insert_module:
            result += f'{indent}    {part.add}\n'
            result += f'{indent}        Insert_{part.insert_module[0]}();\n\n'
        else:
            result += f'{indent}    {part.add};\n\n'

    return result


def generate(case, show_pcb=False):
    """
    :type case: Case
    """
    result = '/* [Rendering options] */\n'
    result += '// Show placeholder PCB in OpenSCAD preview\n'
    result += 'show_pcb = ' + ('true' if show_pcb else 'false') + ';\n'
    result += '// Lid mounting method\n'
    result += f'lid_model = "{case.lid_model}"; // [cap, inner-fit]\n'
    result += '// Conditional rendering\n'
    result += f'render = "case"; // [all, case, lid]\n'
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
    result += '\n'

    for insert in case.get_inserts():
        result += _make_insert_parameters(insert)

    result += '/* [Hidden] */\n'
    result += '$fa=$preview ? 10 : 4;\n'
    result += '$fs=0.2;\n'
    result += f'inner_height = floor_height + standoff_height + pcb_thickness + headroom;\n'
    result += '\n'

    result += _template.lstrip() + "\n"

    for m in case.modules:
        result += m + "\n"

    result += _make_pcb_module(case)
    result += _make_outline_module(case)
    for insert in case.get_inserts():
        result += _make_insert_module(insert[0])

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
            result += f'    #linear_extrude(floor_height+2, convexity=10) \n'
            result += f'        {_make_scad_polygon(shape.path(), "case cutout")}\n'

    for shape in case.lid_holes:
        if shape.is_circle:
            result += f'    translate([{shape.point[0]}, {shape.point[1]}, inner_height])\n'
            result += f'        cylinder(floor_height+2, {shape.radius}, {shape.radius});\n'
        elif shape.is_rect:
            result += f'    translate([{shape.point[0]}, {shape.point[1]}, inner_height+floor_height])\n'
            result += f'        cube([{shape.width}, {shape.height}, floor_height + 2], center=true);\n'
        else:
            result += f'    translate([0, 0, inner_height])\n'
            result += f'    linear_extrude(floor_height+2) \n'
            result += f'        {_make_scad_polygon(shape.path(), "lid hole")}\n'

    for conn in sorted(case.connectors, key=lambda x: x.reference):
        result += f'    // {conn.reference} {conn.footprint} {conn.description}\n'
        result += f'    translate([{conn.position[0]}, {conn.position[1]}, pcb_top])\n' \
                  f'    rotate([0, 0, {-conn.position[2]}])\n' \
                  f'        #connector({conn.bounds[0]},{conn.bounds[1]},{conn.bounds[2]},{conn.bounds[3]},{conn.prop_height + 0.2});\n\n'

    for part in case.parts:
        if part.substract is None:
            continue

        result += _make_part(part, '    ', substract=True)

    result += '    }\n\n'

    result += '    if (show_pcb && $preview) {\n'
    result += '        translate([0, 0, floor_height + standoff_height])\n'
    result += '            pcb();\n'
    result += '    }\n\n'

    result += '    if (render == "all" || render == "case") {\n'
    for mount in case.pcb_mount:
        result += f'        // {mount.ref} [{mount.insert}]\n'
        result += f'        translate([{mount.position[0]}, {mount.position[1]}, floor_height])\n'
        # This currently creates correct holes for the M3 threaded metal inserts I have. Not generic
        result += f'        mount({mount.drill}, {mount.size}, standoff_height)\n'
        result += f'            Insert_{esc(mount.insert[0])}();\n'

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
            result += _make_part(part, '            ')

        result += '            }\n'
        result += '        }\n'

    for part in case.parts:
        if part.add is None:
            continue
        if part.constrain:
            continue
        result += _make_part(part, '        ')

    result += '    }\n'

    for part in case.parts:
        if part.lid is None:
            continue
        result += _make_part(part, '        ', lid=True)

    result += '}\n'
    return result
