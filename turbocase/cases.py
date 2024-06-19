class Connector:
    def __init__(self):
        self.reference = None
        self.description = None
        self.prop_height = None
        self.footprint = None
        self.position = None
        self.bounds = None

    def center(self):
        return (self.bounds[0] + self.bounds[2]) / 2, (self.bounds[1] + self.bounds[3]) / 2

    def width(self):
        return self.bounds[2] - self.bounds[0]

    def height(self):
        return self.bounds[3] - self.bounds[1]

    def depth(self):
        return self.prop_height


class Mount:
    def __init__(self, ref, position, drill, size):
        self.position = position
        self.drill = drill
        self.size = size
        self.ref = ref
        self.insert = None


class Part:
    def __init__(self):
        self.position = None
        self.description = None

        self.add = None
        self.substract = None
        self.lid = None
        self.constrain = False

        self.offset_pcb = False

        self.screw_size = None
        self.insert_module = None


class Case:
    connectors: list[Connector]

    def __init__(self):
        self.inner_path = []
        self.pcb_mount = []
        self.pcb_thickness = 1.6
        self.pcb_path = []
        self.pcb_holes = []
        self.lid_holes = []
        self.lid_model = "cap"
        self.floor_thickness = 1.2
        self.wall_thickness = 1.2
        self.standoff_height = 5

        self.cutouts = []

        self.max_connector_height = 0
        self.connectors = []

        self.modules = []
        self.parts = []
        self.max_part_height = 0

    def get_path_bounds(self, path):
        if path[0] == 'circle':
            radius = path[2]
            pos = path[1]
            return pos[0] - radius, pos[0] + radius, pos[1] - radius, pos[1] + radius
        min_x = path[0][0]
        max_x = 0
        min_y = path[0][1]
        max_y = 0
        for point in path:
            min_x = min(min_x, point[0])
            max_x = max(max_x, point[0])
            min_y = min(min_y, point[1])
            max_y = max(max_y, point[1])
        return min_x, min_y, max_x, max_y

    def get_inner_bounds(self):
        return self.get_path_bounds(self.inner_path)

    def get_pcb_bounds(self):
        return self.get_path_bounds(self.pcb_path)

    def get_case_size(self):
        min_x, min_y, max_x, max_y = self.get_inner_bounds()
        return max_x - min_x + (2 * self.wall_thickness), max_y - min_y + (2 * self.wall_thickness)

    def get_center(self):
        bounds = self.get_inner_bounds()
        return (bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2

    def _diam_to_screw(self, diameter):
        sizes = {
            'M1': 1,
            'M2.5': 2.5,
            'M3': 3,
            'M4': 4,
            'M4.5': 4.5,
            'M5': 5,
            'M6': 6,
            'M8': 8,
        }
        distance = 100
        best = None
        screw_diam = 0
        for size in sizes:
            d = abs(diameter - sizes[size])
            if d < distance:
                distance = d
                best = size
                screw_diam = sizes[size]
        return best, screw_diam

    def get_inserts(self):
        diameters = set()
        for mount in self.pcb_mount:
            diameters.add(mount.drill)
            mount.insert = self._diam_to_screw(mount.drill)

        for part in self.parts:
            if part.screw_size is not None:
                diameters.add(part.screw_size)
                part.insert_module = self._diam_to_screw(part.screw_size)

        result = set()
        for d in diameters:
            result.add(self._diam_to_screw(d))
        return result
