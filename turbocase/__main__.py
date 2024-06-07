import argparse
import logging

from turbocase import scad, svg
from turbocase.kicad import load_pcb


class NiceLogFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    white = "\x1b[97;20m"
    blue = "\x1b[36;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = '[%(levelname)-8s] %(name)-7s - %(message)s'

    FORMATS = {
        logging.DEBUG: blue + format + reset,
        logging.INFO: white + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('pcb', help='Input kicad PCB file')
    parser.add_argument('output', help='Generated openSCAD case template')
    parser.add_argument('--layer', help='Layer with the case inner-outline [defaults to User.6]', default='User.6')
    parser.add_argument('--lid-layer', help='Layer with lid-specific holes [defaults to User.7]', default='User.7')
    parser.add_argument('--bottom', help='Bottom thickness in mm [default 1.2]', default=1.2, type=float)
    parser.add_argument('--wall', help='Wall thickness in mm [default 1.2]', default=1.2, type=float)
    parser.add_argument('--standoff', help='Height generated for the PCB mounts in mm[default 5]', default=5,
                        type=float)
    parser.add_argument('--show-pcb', help='Show the PCB placeholder by default [default false]', default=False,
                        action='store_true')
    parser.add_argument('--lid', help='Lid construction model', choices=['cap', 'inner-fit'], default='cap')

    parser.add_argument('--verbose', '-v', action='store_true', help='Show log messages')
    parser.add_argument('--debug', action='store_true', help='Display a lot of debugging info')

    args = parser.parse_args()

    format = 'scad'
    if args.output.endswith('.svg'):
        format = 'svg'

    ch = logging.StreamHandler()
    ch.setFormatter(NiceLogFormatter())
    if args.verbose:
        logging.basicConfig(level=logging.INFO, handlers=[ch])
    elif args.debug:
        logging.basicConfig(level=logging.DEBUG, handlers=[ch])
    else:
        logging.basicConfig(handlers=[ch])

    log = logging.getLogger('main')

    log.info(f'Loading pcb from "{args.pcb}"')
    log.info(f'Using case drawing from layer [{args.layer}] and lid features from [{args.lid_layer}]')
    case = load_pcb(args.pcb, args.layer, args.lid_layer)

    log.info(f"PCB loaded")
    log.info(f"   Case size:         {case.get_case_size()[0]}mm x {case.get_case_size()[1]}mm")
    log.info(f"   Mounting holes:    {len(case.pcb_mount)}")
    log.info(f"   Parts with height: {len(case.connectors)}")
    log.info(f"   Case prefabs:      {len(case.parts)}")
    inserts = case.get_inserts()
    di = []
    for i in inserts:
        di.append(i[0])
    sizes = ', '.join(di)
    log.info(f'   Insert sizes:      {sizes}')

    case.floor_thickness = args.bottom
    case.wall_thickness = args.wall
    case.standoff_height = args.standoff
    case.lid_model = args.lid

    log.info(f'Generating output at "{args.output}"')
    if format == 'scad':
        code = scad.generate(case, show_pcb=args.show_pcb)
        with open(args.output, 'w') as handle:
            handle.write(code)
    elif format == 'svg':
        code = svg.generate(case, show_pcb=args.show_pcb)
        with open(args.output, 'w') as handle:
            handle.write(code)


if __name__ == '__main__':
    main()
