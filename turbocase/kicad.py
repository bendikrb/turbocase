import os
import sys

import sexpdata

from turbocase.cases import Case, Connector, Part
from turbocase.vector import Vector
import turbocase.parts


class Sym:
    def __init__(self, symbol):
        self.raw = symbol
        self.name = symbol[0].value()
        self.attr = {}
        self.values = []
        self.property = {}

        arrays = ['pad', 'property', 'fp_text', 'fp_line', 'fp_rect', 'fp_circle', 'xy']

        for part in symbol:
            if isinstance(part, sexpdata.Symbol):
                continue
            if isinstance(part, list):
                key = part[0].value()

                if key == 'property':
                    if len(part) == 2:
                        self.property[part[1]] = True
                    else:
                        self.property[part[1]] = part[2]

                if key in arrays:
                    if key not in self.attr:
                        self.attr[key] = []
                    self.attr[key].append(Sym(part))
                else:
                    self.attr[key] = Sym(part)
            else:
                self.values.append(part)

    def __repr__(self):
        values = ' '.join(map(repr, self.values))
        if len(values) > 0:
            return f'<{self.name} {values}>'
        return f'<{self.name}>'

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.values[item]
        if isinstance(item, slice):
            return self.values[item.start:item.stop:item.step]
        return self.attr[item]

    def __contains__(self, item):
        return item in self.attr

    def __len__(self):
        return len(self.values)


def sort_outline(shapes):
    # No sorting needed since you can only have one poly as outline
    if shapes[0].name == 'gr_poly':
        return shapes

    result = []
    unused = shapes[:]
    point = tuple(unused[0]['end'][:])
    result.append(unused[0])
    del unused[0]

    while len(unused) > 0:
        for i, item in enumerate(unused):
            start = tuple(item['start'][:])
            end = tuple(item['end'][:])
            if start == point:
                new_point = end
                break
            if end == point:
                new_point = start
                break
        else:
            raise ValueError("Incomplete shape")

        point = new_point
        result.append(item)
        del unused[i]
    return result


def shape_bounds(primitives):
    coords = []
    for p in primitives:
        coords.append(p['start'][:])
        coords.append(p['end'][:])
    min_x = coords[0][0]
    max_x = 0
    min_y = coords[0][1]
    max_y = 0
    for point in coords:
        min_x = min(min_x, point[0])
        max_x = max(max_x, point[0])
        min_y = min(min_y, point[1])
        max_y = max(max_y, point[1])
    return min_x, min_y, max_x, max_y


def unindent(raw):
    raw = raw.lstrip('\n')
    indent = len(raw) - len(raw.lstrip())
    result = []
    for line in raw.splitlines():
        result.append(line[indent:])
    return '\n'.join(result)


def load_pcb(pcb_file, outline_layer=None):
    if outline_layer is None:
        outline_layer = 'User.6'

    with open(pcb_file) as handle:
        pcb = sexpdata.load(handle)

    result = Case()

    outline_shapes = []
    mountingholes = []
    connectors = []
    parts = []

    for symbol in pcb:
        if not isinstance(symbol, list):
            continue
        if isinstance(symbol[0], sexpdata.Symbol):
            name = symbol[0].value()

            if name == 'general':
                general = Sym(symbol)
                result.pcb_thickness = general['thickness'][0]

            if name in ['segment', 'gr_line', 'gr_arc', 'gr_poly', 'gr_rect']:
                for sub in symbol:
                    if isinstance(sub, list):
                        if sub[0].value() == 'layer' and sub[1] == outline_layer:
                            outline_shapes.append(Sym(symbol))

            if name == 'footprint':
                footprint = Sym(symbol)

                if 'MountingHole' in footprint[0]:
                    mountingholes.append(footprint)
                elif 'TurboCase' in footprint[0]:
                    parts.append(footprint)
                else:
                    for prop in footprint['property']:
                        if len(prop) == 2 and prop[0] == 'Height':
                            connectors.append(footprint)

    outline = sort_outline(outline_shapes)

    path = []
    if outline[0].name == 'gr_poly':
        poly = outline[0]['pts']['xy']
        for xy in poly:
            path.append(xy[:])
    elif outline[0].name == 'gr_rect':
        rect = outline[0]
        start = tuple(rect['start'][:])
        end = tuple(rect['end'][:])
        path.append(start)
        path.append((end[0], start[1]))
        path.append(end)
        path.append((start[0], end[1]))
    else:
        point = tuple(outline[0]['start'][:])
        path.append(point)
        for item in outline:
            start = tuple(item['start'][:])
            end = tuple(item['end'][:])

            if item.name == 'gr_arc':
                a = Vector(start[0], start[1])
                b = Vector(end[0], end[1])

                mid = Vector(item['mid'][0], item['mid'][1])

                # Figure out the center of the arc
                v1 = (a + b) / 2 - mid
                v2 = a - mid
                cos_ang = (v1 * v2) / (v1.mag() * v2.mag())
                radius = (v2.mag() / 2) / cos_ang

                c = mid + (v1 / v1.mag()) * radius

                points = [a, mid, b]
                newpoints = [a]
                for i in range(1, len(points)):
                    p1 = points[i - 1]
                    p2 = points[i]
                    dir = ((p1 + p2) / 2) - c
                    p = c + (dir / dir.mag()) * radius
                    newpoints.append(p)
                    newpoints.append(p2)

                if start == point:
                    path.extend(newpoints[1:])
                else:
                    path.extend(reversed(newpoints[:-1]))
                point = path[-1]
            else:
                if point == start:
                    new_point = end
                else:
                    new_point = start

                path.append(new_point)
                point = new_point

    result.inner_path = path

    for hole in mountingholes:
        center = hole['at'][:]

        drill = 0
        for pad in hole['pad']:
            if pad['drill'][0] > drill:
                drill = pad['drill'][0]

        space = drill + 2
        for circle in hole['fp_circle']:
            if circle['layer'][0] != 'F.CrtYd':
                continue
            diam = max(circle['end'][0], circle['end'][1]) * 2
            if diam > space:
                space = diam

        result.pcb_mount.append((center, drill, space, hole.property['Reference']))

    max_height = 0
    for item in connectors:
        ref = item.property['Reference']
        footprint = item.property['Footprint']
        desc = item.property['Description']
        height = float(item.property['Height'])
        max_height = max(max_height, height)

        shapes = []
        for stype in ['fp_line', 'fp_rect']:
            if stype in item:
                for line in item[stype]:
                    if line['layer'][0] == 'F.Fab':
                        shapes.append(line)

        c = Connector()
        c.prop_height = height
        c.reference = ref
        c.footprint = footprint
        c.description = desc
        c.bounds = shape_bounds(shapes)
        c.position = item['at'][:]
        result.connectors.append(c)
    result.max_connector_height = max_height

    modules = set()

    for part in parts:
        part_id = part[0].split(':')[1]
        if not hasattr(turbocase.parts, part_id):
            sys.stderr.write(f"Unknown part: {part.name}\n")
            continue

        func = getattr(turbocase.parts, part_id)
        modules.add(unindent(func.__doc__))

        p = Part()
        p.script = func()
        p.position = part.attr['at'][:]

        result.parts.append(p)
    result.modules = list(modules)

    return result
