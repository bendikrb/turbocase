from sexpdata import Symbol


class Shape:
    def graphic(self, uuid):
        return ()


class Line(Shape):
    def __init__(self, layer, start, end):
        self.layer = layer
        self.start = start
        self.end = end

    def graphic(self, uuid):
        return (
            Symbol('fp_line'),
            (Symbol('start'), *self.start),
            (Symbol('end'), *self.end),
            (Symbol('stroke'),
             (Symbol('width'), 0.2),
             (Symbol('type'), Symbol('default')),
             ),
            (Symbol('layer'), self.layer),
            (Symbol('uuid'), uuid),
        )


class Circle(Shape):
    def __init__(self, layer, center, end):
        self.layer = layer
        self.center = center
        self.end = end

    def graphic(self, uuid):
        return (
            Symbol('fp_circle'),
            (Symbol('center'), *self.center),
            (Symbol('end'), *self.end),
            (Symbol('stroke'),
             (Symbol('width'), 0.2),
             (Symbol('type'), Symbol('default')),
             ),
            (Symbol('fill'), Symbol('none')),
            (Symbol('layer'), self.layer),
            (Symbol('uuid'), uuid),
        )


class Arc(Shape):
    def __init__(self, layer, start, end, middle):
        self.layer = layer
        self.start = start
        self.middle = middle
        self.end = end

    def graphic(self, uuid):
        return (
            Symbol('fp_arc'),
            (Symbol('start'), *self.start),
            (Symbol('mid'), *self.middle),
            (Symbol('end'), *self.end),
            (Symbol('stroke'),
             (Symbol('width'), 0.2),
             (Symbol('type'), Symbol('default')),
             ),
            (Symbol('layer'), self.layer),
            (Symbol('uuid'), uuid),
        )


class Rect(Shape):
    def __init__(self, layer, start, end):
        self.layer = layer
        self.start = start
        self.end = end

    def graphic(self, uuid):
        return (
            Symbol('fp_rect'),
            (Symbol('start'), *self.start),
            (Symbol('end'), *self.end),
            (Symbol('stroke'),
             (Symbol('width'), 0.2),
             (Symbol('type'), Symbol('default')),
             ),
            (Symbol('fill'), Symbol('none')),
            (Symbol('layer'), self.layer),
            (Symbol('uuid'), uuid),
        )
