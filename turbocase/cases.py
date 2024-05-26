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


class Part:
    def __init__(self):
        self.position = None
        self.description = None

        self.add = None
        self.substract = None

        self.offset_pcb = False


class Case:
    connectors: list[Connector]

    def __init__(self):
        self.inner_path = []
        self.pcb_mount = []
        self.pcb_thickness = 1.6
        self.floor_thickness = 1.2
        self.wall_thickness = 1.2
        self.standoff_height = 5

        self.cutouts = []

        self.max_connector_height = 0
        self.connectors = []

        self.modules = []
        self.parts = []
        self.max_part_height = 0

    def get_inner_bounds(self):
        min_x = self.inner_path[0][0]
        max_x = 0
        min_y = self.inner_path[0][1]
        max_y = 0
        for point in self.inner_path:
            min_x = min(min_x, point[0])
            max_x = max(max_x, point[0])
            min_y = min(min_y, point[1])
            max_y = max(max_y, point[1])
        return min_x, min_y, max_x, max_y

    def get_center(self):
        bounds = self.get_inner_bounds()
        return (bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2
