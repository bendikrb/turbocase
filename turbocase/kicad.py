import inspect
import os
import sys
from functools import total_ordering

import sexpdata

from turbocase.cases import Case, Connector, Part
from turbocase.vector import Vector
import turbocase.parts
from turbocase.parts import *


def get_all_parts():
    result = {}
    modules = inspect.getmembers(turbocase.parts, predicate=inspect.ismodule)
    for name, mod in modules:
        defines = dict([(name, cls) for name, cls in mod.__dict__.items() if isinstance(cls, type)])
        for name in defines:
            if name in ['BasePart', 'Rect', 'Circle', 'Shape', 'Line', 'Symbol', 'Arc']:
                continue
            if defines[name]._hide == name:
                continue
            result[name] = defines[name]
    return result


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


@total_ordering
class Shape:
    @classmethod
    def from_single(cls, graphic):
        res = cls()
        res.append(graphic)
        return res

    def __init__(self):
        self.parts = []
        self.start = ()
        self.end = ()
        self.point = ()
        self.radius = 0
        self._bounds = None

    def __repr__(self):
        single = self.parts[0].name in ['gr_rect', 'gr_poly', 'gr_circle']

        if single:
            return f'<Shape {self.parts[0].name}>'

        return f'<Shape {len(self.parts)} parts>'

    def append(self, graphic):
        self._bounds = None
        self.parts.append(graphic)

        if graphic.name == 'gr_circle':
            self.point = graphic['center'][:]
            handle = Vector(graphic['end'][0], graphic['end'][1])
            self.radius = abs((handle - Vector(self.point[0], self.point[1])).mag())
        if graphic.name == 'gr_rect':
            start = tuple(graphic['start'][:])
            end = tuple(graphic['end'][:])
            self.point = (start[0] + end[0]) / 2, (start[1] + end[1]) / 2

    def path(self):
        single = self.parts[0].name in ['gr_rect', 'gr_poly', 'gr_circle']
        path = []
        if single:
            part = self.parts[0]
            if part.name == 'gr_poly':
                for xy in part['pts']['xy']:
                    path.append(xy[:])
                return path
            if part.name == 'gr_rect':
                start = tuple(part['start'][:])
                end = tuple(part['end'][:])
                path.append(start)
                path.append((end[0], start[1]))
                path.append(end)
                path.append((start[0], end[1]))
                return path
            if part.name == 'gr_circle':
                return [self.point]

        point = tuple(self.parts[0]['start'][:])
        path.append(point)
        for item in self.parts:
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
        return path

    def bounds(self):
        if self._bounds is not None:
            return self._bounds

        coords = self.path()
        min_x = coords[0][0]
        max_x = 0
        min_y = coords[0][1]
        max_y = 0
        for point in coords:
            min_x = min(min_x, point[0])
            max_x = max(max_x, point[0])
            min_y = min(min_y, point[1])
            max_y = max(max_y, point[1])
        self._bounds = min_x, min_y, max_x, max_y
        return self._bounds

    @property
    def width(self):
        bounds = self.bounds()
        return bounds[2] - bounds[0]

    @property
    def height(self):
        bounds = self.bounds()
        return bounds[3] - bounds[1]

    @property
    def area(self):
        return self.width * self.height

    @property
    def is_circle(self):
        return len(self.parts) == 1 and self.parts[0].name == 'gr_circle'

    @property
    def is_rect(self):
        return len(self.parts) == 1 and self.parts[0].name == 'gr_rect'

    def __lt__(self, other):
        return self.area < other.area


def sort_outline(shapes):
    # No sorting needed since you can only have one poly as outline
    if shapes[0].name == 'gr_poly':
        return shapes

    result = []
    unused = []

    for s in shapes:
        if s.name in ['gr_poly', 'gr_circle', 'gr_rect']:
            result.append(Shape.from_single(s))
        else:
            unused.append(s)

    if len(unused) == 0:
        return list(sorted(result, reverse=True))

    # Start first shape from seperate parts
    shape = Shape()
    shape.point = tuple(unused[0]['end'][:])
    shape.append(unused[0])
    del unused[0]

    while len(unused) > 0:
        for i, item in enumerate(unused):
            start = tuple(item['start'][:])
            end = tuple(item['end'][:])
            if start == shape.point:
                new_point = end
                break
            if end == shape.point:
                new_point = start
                break
        else:
            # None of the unused parts fit the current shape, start a new shape
            result.append(shape)
            shape = Shape()
            shape.point = tuple(unused[0]['end'][:])
            shape.append(unused[0])
            del unused[0]
            continue

        shape.point = new_point
        shape.append(item)
        del unused[i]
    result.append(shape)
    return list(sorted(result, reverse=True))


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

            if name in ['segment', 'gr_line', 'gr_arc', 'gr_poly', 'gr_rect', 'gr_circle']:
                for sub in symbol:
                    if isinstance(sub, list):
                        if sub[0].value() == 'layer' and sub[1] == outline_layer:
                            outline_shapes.append(Sym(symbol))

            if name == 'footprint':
                footprint = Sym(symbol)

                if ':MountingHole_' in footprint[0]:
                    mountingholes.append(footprint)
                elif 'TurboCase' in footprint[0]:
                    parts.append(footprint)
                else:
                    for prop in footprint['property']:
                        if len(prop) == 2 and prop[0] == 'Height':
                            connectors.append(footprint)

    outline = sort_outline(outline_shapes)

    path = outline[0].path()

    result.inner_path = path
    if len(outline) > 1:
        result.cutouts = outline[1:]

    for hole in mountingholes:
        center = hole['at'][:]

        drill = 0
        drill_space = 0
        for pad in hole['pad']:
            if pad['drill'][0] > drill:
                drill = pad['drill'][0]
                drill_space = pad['size'][0]

        space = drill + 2
        if 'fp_circle' in hole:
            for circle in hole['fp_circle']:
                if circle['layer'][0] != 'F.CrtYd':
                    continue
                diam = max(circle['end'][0], circle['end'][1]) * 2
                if diam > space:
                    space = diam
        else:
            space = drill_space

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

        if len(shapes) == 0:
            sys.stderr.write(f"Could not process connector {ref}: no graphics on the F.Fab layer found\n")
            continue

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
    partlib = get_all_parts()

    for part in parts:
        part_id = part[0].split(':')[1]
        if part_id not in partlib:
            sys.stderr.write(f"Unknown part: {part_id}\n")
            continue
        partcls = partlib[part_id]
        modules.add(partcls.get_module())

        inst = partcls()

        p = Part()
        p.description = inst.description
        if inst._add:
            p.add = inst.insert(part)
        if inst._substract:
            p.substract = inst.substract(part)
        p.position = part.attr['at'][:]
        p.offset_pcb = inst._pcb_height

        result.parts.append(p)

        if 'Height' in part.property:
            ph = float(part.property['Height'])
            result.max_part_height = max(result.max_part_height, ph)
    result.modules = list(modules)

    return result
