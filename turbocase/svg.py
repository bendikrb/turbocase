import logging

try:
    import svgwrite
    from svgwrite.masking import Mask
    from svgwrite.path import Path
    from svgwrite.shapes import Circle, Rect

    svg_support = True
except ImportError:
    svg_support = False


def path_to_svg(path):
    d = []
    first = True
    for point in path:
        if first:
            d.append(f'M {point[0]} {point[1]}')
            first = False
        else:
            d.append(f'L {point[0]} {point[1]}')
    return d


def generate_pcb(case):
    bounds = case.get_pcb_bounds()
    size = bounds[2] - bounds[0], bounds[3] - bounds[1]

    svg = svgwrite.Drawing("board.svg", size=(f'{size[0]}mm', f'{size[1]}mm'),
                           viewBox=f"{bounds[0]} {bounds[1]} {size[0]} {size[1]}")

    d = path_to_svg(case.pcb_path)
    svg.add(Path(d, id="pcb", fill="none", stroke="#FFF", stroke_width="0.1"))

    for hole in case.pcb_holes:
        if hole.is_circle:
            svg.add(Circle(center=hole.point, r=hole.radius, fill="white"))
        else:
            d = path_to_svg(hole.path())
            svg.add(Path(d, fill="#FFF"))

    return svg.tostring()


def generate_case(case):
    bounds = case.get_inner_bounds()
    size = bounds[2] - bounds[0], bounds[3] - bounds[1]

    svg = svgwrite.Drawing("board.svg", size=(f'{size[0]}mm', f'{size[1]}mm'),
                           viewBox=f"{bounds[0]} {bounds[1]} {size[0]} {size[1]}")

    d = path_to_svg(case.inner_path)
    svg.add(Path(d, id="pcb", fill="none", stroke="#FFF", stroke_width="0.1"))

    for hole in case.cutouts:
        if hole.is_circle:
            svg.add(Circle(center=hole.point, r=hole.radius, fill="white"))
        else:
            d = path_to_svg(hole.path())
            svg.add(Path(d, fill="#FFF"))

    return svg.tostring()


def generate(case, show_pcb):
    """
    :type case: Case
    """
    log = logging.getLogger('svg')

    if not svg_support:
        log.critical('Exporting SVG files requires the svgwriter python module')
        exit(1)

    if show_pcb:
        log.info("Exporting SVG for PCB with holes because --show-pcb is enabled")
        return generate_pcb(case)
    else:
        log.info("Exporting SVG for case outline")
        return generate_case(case)
