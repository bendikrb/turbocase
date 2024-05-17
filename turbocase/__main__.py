import argparse

from turbocase import scad
from turbocase.kicad import load_pcb


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('pcb', help='Input kicad PCB file')
    parser.add_argument('output', help='Generated openSCAD case template')
    parser.add_argument('--layer', help='Layer with the case inner-outline [defaults to User.6]', default='User.6')
    parser.add_argument('--bottom', help='Bottom thickness in mm [default 1.2]', default=1.2, type=float)
    parser.add_argument('--wall', help='Wall thickness in mm [default 1.2]', default=1.2, type=float)
    parser.add_argument('--standoff', help='Height generated for the PCB mounts in mm[default 5]', default=5, type=float)
    args = parser.parse_args()

    case = load_pcb(args.pcb, args.layer)

    case.floor_thickness = args.bottom
    case.wall_thickness = args.wall
    case.standoff_height = args.standoff

    code = scad.generate(case)
    with open(args.output, 'w') as handle:
        handle.write(code)


if __name__ == '__main__':
    main()
