import base64
import hmac
import uuid
import zlib
from hashlib import sha256

from sexpdata import Symbol, dumps

from turbocase.parts import *
import turbocase.parts
import inspect


def make_uuid(name, index):
    h = hmac.new(name.encode(), str(index).encode(), digestmod=sha256)
    return str(uuid.UUID(bytes=h.digest()[:16], version=4))


def make_property(part, name, value):
    return [
        Symbol('property'), name, value,
        [Symbol('at'), 0, 0, 0],
        [Symbol('unlocked'), Symbol('yes')],
        [Symbol('layer'), "F.SilkS"],
        [Symbol('hide'), Symbol('yes')],
        [Symbol('uuid'), make_uuid(part.__name__, name)],
        [Symbol('effects'),
         [Symbol('font'),
          [Symbol('size'), 1, 1],
          [Symbol('thickness'), 0.1],
          ],
         ],
    ]


def make_footprint(part):
    footprint = [Symbol('footprint'), part.__name__]
    footprint.append([Symbol('version'), Symbol('20240108')])
    footprint.append([Symbol('generator'), Symbol('turbocase')])
    footprint.append([Symbol('descr'), part.description])
    footprint.append(
        [Symbol('attr'), Symbol('board_only'), Symbol('exclude_from_pos_files'), Symbol('exclude_from_bom'),
         Symbol('allow_missing_courtyard')])
    footprint.append([Symbol('zone_connect'), 0])

    if part._add or part._substract:
        mod = part.get_module()
        enc = base64.b64encode(zlib.compress(mod.encode())).decode()
        footprint.append(make_property(part, 'TurboCaseModule', enc))
        inst = part()
        if part._add:
            code = inst.insert(inst)
            footprint.append(make_property(part, 'TurboCaseAdd', code))
        if part._substract:
            code = inst.substract(inst)
            footprint.append(make_property(part, 'TurboCaseSub', code))
        if part._lid:
            code = inst.lid(inst)
            footprint.append(make_property(part, 'TurboCaseLid', code))
        if part._constrain:
            footprint.append(make_property(part, 'TurboCaseConstrain', 'yes'))
        if part._pcb_height:
            footprint.append(make_property(part, 'TurboCaseOffsetPCB', 'yes'))

        ph = inst.get_part_height()
        if ph is not None and ph > 0:
            footprint.append(make_property(part, 'TurboCaseHeight', str(ph)))

        sd = inst.get_screw_diameter()
        if sd is not None and sd > 0:
            footprint.append(make_property(part, 'TurboCaseScrewSize', str(sd)))

    salt = 0
    for shape in part.make_footprint():
        salt += 1
        graphic = shape.graphic(make_uuid(part.__name__, salt))
        footprint.append(graphic)
    return footprint


def main():
    modules = inspect.getmembers(turbocase.parts, predicate=inspect.ismodule)
    parts = set()
    for name, mod in modules:
        defines = dict([(name, cls) for name, cls in mod.__dict__.items() if isinstance(cls, type)])
        for name in defines:
            if name in ['BasePart', 'Rect', 'Circle', 'Shape', 'Line', 'Symbol', 'Arc', 'Text']:
                continue
            if defines[name]._hide == name:
                continue
            parts.add(defines[name])

    for part in parts:
        print(f"Generating footprint {part.__name__}...")
        fp = make_footprint(part)
        sexpr = dumps(fp, pretty_print=True)
        with open(f'TurboCase.pretty/{part.__name__}.kicad_mod', 'w') as handle:
            handle.write(sexpr)


if __name__ == '__main__':
    main()
