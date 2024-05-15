import os

import sexpdata

from turbocase.cases import Case, Connector


class Sym:
    def __init__(self, symbol):
        self.raw = symbol
        self.name = symbol[0].value()
        self.attr = {}
        self.values = []
        self.property = {}

        arrays = ['pad', 'property', 'fp_text', 'fp_line', 'fp_rect']

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


def load_pcb(pcb_file, outline_layer=None):
    if outline_layer is None:
        outline_layer = 'User.6'

    with open(pcb_file) as handle:
        pcb = sexpdata.load(handle)

    result = Case()

    outline_shapes = []
    mountingholes = []
    connectors = []

    for symbol in pcb:
        if not isinstance(symbol, list):
            continue
        if isinstance(symbol[0], sexpdata.Symbol):
            name = symbol[0].value()

            if name == 'general':
                general = Sym(symbol)
                result.pcb_thickness = general['thickness'][0]

            if name in ['segment', 'gr_line', 'gr_arc']:
                for sub in symbol:
                    if isinstance(sub, list):
                        if sub[0].value() == 'layer' and sub[1] == outline_layer:
                            outline_shapes.append(Sym(symbol))

            if name == 'footprint':
                footprint = Sym(symbol)

                if 'MountingHole' in footprint[0]:
                    mountingholes.append(Sym(symbol))

                for prop in footprint['property']:
                    if len(prop) == 2 and prop[0] == 'Height':
                        connectors.append(footprint)

    outline = sort_outline(outline_shapes)

    path = []
    point = tuple(outline[0]['start'][:])
    path.append(point)
    for item in outline:
        start = tuple(item['start'][:])
        end = tuple(item['end'][:])

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
        space = 0
        for pad in hole['pad']:
            if pad['drill'][0] > drill:
                drill = pad['drill'][0]
                space = pad['size'][0]

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

    return result
