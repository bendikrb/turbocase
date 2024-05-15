import argparse

from turbocase import scad
from turbocase.kicad import load_pcb


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('pcb', help='Input kicad PCB file')
    parser.add_argument('output', help='Generated openSCAD case template')
    parser.add_argument('--layer', help='Layer with the case inner-outline [defaults to User.6]', default='User.6')
    args = parser.parse_args()

    case = load_pcb(args.pcb, args.layer)
    code = scad.generate(case)
    with open(args.output, 'w') as handle:
        handle.write(code)


if __name__ == '__main__':
    main()
