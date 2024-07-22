import base64
import inspect
import logging
import zlib
from functools import total_ordering
import math

import sexpdata

from turbocase.cases import Case, Connector, Part, Mount
from turbocase.vector import Vector
import turbocase.parts
from turbocase.parts import *


def get_all_parts():
    result = {}
    modules = inspect.getmembers(turbocase.parts, predicate=inspect.ismodule)
    for name, mod in modules:
        defines = dict([(name, cls) for name, cls in mod.__dict__.items() if isinstance(cls, type)])
        for name in defines:
            if name in ['BasePart', 'Rect', 'Circle', 'Shape', 'Line', 'Symbol', 'Arc', 'Text']:
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

    @classmethod
    def make_circle(cls, center, radius, layer=None):
        if layer is None:
            layer = 'User.6'

        return Shape.from_single(Sym([sexpdata.Symbol('gr_circle'),
                                      [sexpdata.Symbol('center'), center[0], center[1]],
                                      [sexpdata.Symbol('end'), center[0], center[1] + radius],
                                      [sexpdata.Symbol('layer'), layer],
                                      ]))

    @classmethod
    def make_rect(cls, start, end, layer=None):
        if layer is None:
            layer = 'User.6'

        return Shape.from_single(Sym([sexpdata.Symbol('gr_rect'),
                                      [sexpdata.Symbol('start'), start[0], start[1]],
                                      [sexpdata.Symbol('end'), end[0], end[1]],
                                      [sexpdata.Symbol('layer'), layer],
                                      ]))

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

    def _degrees(self, r):
        deg = math.degrees(r) + 90
        if deg < 0:
            deg += 360
        return deg % 360

    def _frange(self, start, stop, step):
        n_items = int(math.ceil((stop - start) / step))
        return (start + i * step for i in range(n_items))

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
                return ['circle', self.point, self.radius]

        point = tuple(self.parts[0]['start'][:])
        path.append(point)
        for item in self.parts:
            start = tuple(item['start'][:])
            end = tuple(item['end'][:])

            if item.name == 'gr_arc':
                a = Vector(start[0], start[1])
                b = Vector(end[0], end[1])
                mid = Vector(item['mid'][0], item['mid'][1])

                # Figure out the center and radius of the arc
                v1 = (a + b) / 2 - mid
                v2 = a - mid
                cos_ang = (v1 * v2) / (v1.mag() * v2.mag())
                radius = round((v2.mag() / 2) / cos_ang, 5)
                c = mid + (v1 / v1.mag()) * radius
                c = Vector(round(c.x, 5), round(c.y, 5))

                # Calculate new points with the center at 0,0
                a_c = a - c
                b_c = b - c
                m_c = mid - c
                alpha_a = math.atan2(a_c.y, a_c.x)
                alpha_b = math.atan2(b_c.y, b_c.x)
                alpha_m = math.atan2(m_c.y, m_c.x)
                deg_a = self._degrees(alpha_a)
                deg_b = self._degrees(alpha_b)
                deg_m = self._degrees(alpha_m)

                # Swap angles to make them clockwise
                if deg_a > deg_b:
                    temp = deg_a
                    deg_a = deg_b
                    deg_b = temp
                    temp = a
                    a = b
                    b = temp

                # Swap around direction for big arcs
                if deg_a < deg_m < deg_b:
                    pass
                else:
                    temp = deg_a
                    deg_a = deg_b
                    deg_b = temp
                    temp = a
                    a = b
                    b = temp

                length = (deg_b - deg_a) % 360
                num_points = int(abs(length) / 9) * max(int(radius / 3), 1)

                newpoints = []
                step = length / num_points
                for deg in self._frange(0, length, step):
                    deg += deg_a
                    deg %= 360
                    rad = math.radians(deg - 90)
                    vec = Vector(round(math.cos(rad), 5), round(math.sin(rad), 5))
                    newpoints.append((vec * radius) + c)
                newpoints.append(b)

                previous = Vector(point[0], point[1])
                if (newpoints[0] - previous).mag() < (newpoints[-1] - previous).mag():
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
        if self.is_circle:
            c = self.point
            return c[0] - self.radius, c[0] + self.radius, c[1] - self.radius, c[1] + self.radius
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


def point_match(a, b):
    # Match a coordinate with a margin of error
    if abs(a[0] - b[0]) < 0.001 and abs(a[1] - b[1]) < 0.001:
        return True
    return False


def sort_outline(shapes):
    if len(shapes) == 0:
        return []

    # No sorting needed since you can only have one poly as outline
    if shapes[0].name == 'gr_poly':
        return [Shape.from_single(shapes[0])]

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
            if point_match(start, shape.point):
                new_point = end
                break
            if point_match(end, shape.point):
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


def load_pcb(pcb_file, outline_layer=None, lid_layer=None):
    if outline_layer is None:
        outline_layer = 'User.6'
    if lid_layer is None:
        lid_layer = 'User.7'

    log = logging.getLogger('kicad')

    with open(pcb_file) as handle:
        pcb = sexpdata.load(handle)

    result = Case()

    outline_shapes = []
    lid_shapes = []
    edgecuts_shapes = []
    mountingholes = []
    connectors = []
    parts = []
    log.debug('Extracting data from PCB file...')
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
                            log.debug(f'[{outline_layer}] {symbol[0]}')
                            outline_shapes.append(Sym(symbol))
                        if sub[0].value() == 'layer' and sub[1] == lid_layer:
                            log.debug(f'[{lid_layer}] {symbol[0]}')
                            lid_shapes.append(Sym(symbol))
                        if sub[0].value() == 'layer' and sub[1] == 'Edge.Cuts':
                            log.debug(f'[Edge.Cuts] {symbol[0]}')
                            edgecuts_shapes.append(Sym(symbol))

            if name == 'footprint':
                footprint = Sym(symbol)

                if ':MountingHole_' in footprint[0]:
                    log.debug(f'Mounting hole detected: {footprint[0]}')
                    mountingholes.append(footprint)
                elif 'TurboCase' in footprint[0]:
                    log.debug(f'TurboCase footprint: {footprint[0]}')
                    parts.append(footprint)
                else:
                    for prop in footprint['property']:
                        if len(prop) == 2 and prop[0] == 'Height':
                            log.debug(f'Part with Height property set: {footprint[0]} is {prop[1]}mm tall')
                            connectors.append(footprint)
                        if len(prop) == 2 and prop[0] == 'TurboCaseModule':
                            log.debug(f'Part with embedded OpenSCAD model: {footprint[0]}')
                            parts.append(footprint)

    log.debug('Sorting case outline shapes...')
    outline = sort_outline(outline_shapes)
    log.debug('Sorting edge-cut shapes...')
    edge_cuts = sort_outline(edgecuts_shapes)
    log.debug('Sorting lid shapes...')
    lid = sort_outline(lid_shapes)

    if len(outline) == 0:
        log.critical(f'No case outline defined on [{outline_layer}], making rectangular case from [Edge.Cuts]')
        bb = edge_cuts[0].bounds()
        outline.append(
            Shape.make_rect(Vector(bb[0], bb[1]) - Vector(1, 1), Vector(bb[2], bb[3]) + Vector(1, 1)))

    path = outline[0].path()
    if len(edge_cuts):
        result.pcb_path = edge_cuts[0].path()
    else:
        log.warning("Could not load a PCB shape from the [Edge.Cuts] layer. No PCB preview will be available.")
        result.pcb_path = []
    if len(edge_cuts) > 1:
        result.pcb_holes = edge_cuts[1:]

    result.inner_path = path
    if len(outline) > 1:
        result.cutouts = outline[1:]

    result.lid_holes = lid

    for hole in mountingholes:
        center = hole['at'][:]
        ref = hole.property['Reference'] if 'Reference' in hole.property else 'REF#'
        drill = 0
        drill_space = 0
        for pad in hole['pad']:
            if 'drill' not in pad:
                continue
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
            log.debug(f'Mounting hole [{ref}] margin diameter is {space} from circle graphic')
        else:
            log.debug(f'Mounting hole [{ref}] margin diameter is {space} from pad dimensions')
            space = drill_space
        result.pcb_mount.append(Mount(hole.property['Reference'], center, drill, space))
        result.pcb_holes.append(Shape.make_circle(center, drill / 2))

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
            log.error(f"Could not process connector {ref}: no graphics on the F.Fab layer found")
            continue

        c = Connector()
        c.prop_height = height
        c.reference = ref
        c.footprint = footprint
        c.description = desc
        c.bounds = shape_bounds(shapes)
        c.position = item['at'][:]
        if len(c.position) == 2:
            c.position = c.position + [0]
        result.connectors.append(c)
    result.max_connector_height = max_height

    modules = set()
    partlib = get_all_parts()

    for part in parts:
        p = Part()
        p.position = part.attr['at'][:]
        ph = None
        if 'TurboCaseModule' in part.property:
            # Part with embedded OpenSCAD code

            # Decompress the module code from the property
            modules.add(zlib.decompress(base64.b64decode(part.property['TurboCaseModule'])).decode())

            p.description = part.property['Description'] if 'Description' in part.property else ''
            if p.description.strip() == "":
                p.description = part.property['Footprint'] if 'Footprint' in part.property else 'Unknown'

            if 'TurboCaseAdd' in part.property:
                p.add = part.property['TurboCaseAdd']
            if 'TurboCaseSub' in part.property:
                p.substract = part.property['TurboCaseSub']
            if 'TurboCaseLid' in part.property:
                p.lid = part.property['TurboCaseLid']
            p.constrain = bool(part.property['TurboCaseConstrain']) if 'TurboCaseConstrain' in part.property else False
            p.offset_pcb = bool(part.property['TurboCaseOffsetPCB']) if 'TurboCaseOffsetPCB' in part.property else False
            p.screw_size = float(part.property['TurboCaseScrewSize']) if 'TurboCaseScrewSize' in part.property else None
            if 'TurboCaseHeight' in part.property:
                ph = float(part.property['TurboCaseHeight'])
        else:
            # Part from the embedded Python library
            part_id = part[0].split(':')[1]
            if part_id not in partlib:
                log.error(f"Unknown part: {part_id}")
                continue
            partcls = partlib[part_id]
            modules.add(partcls.get_module())

            inst = partcls()

            p.description = inst.description
            if inst._add:
                p.add = inst.insert(part)
            if inst._substract:
                p.substract = inst.substract(part)
            if inst._lid:
                p.lid = inst.lid(part)
            p.constrain = inst._constrain
            p.offset_pcb = inst._pcb_height
            p.screw_size = inst.get_screw_diameter()
            ph = inst.get_part_height()

        if ph is not None:
            if p.offset_pcb:
                ph += result.pcb_thickness + result.standoff_height
        else:
            ph = 0.0

        result.parts.append(p)

        if 'Height' in part.property:
            ph = float(part.property['Height'])
        result.max_part_height = max(result.max_part_height, ph)
    result.modules = list(modules)

    return result
