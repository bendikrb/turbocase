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
    def __init__(self, layer, center, end, style=None):
        self.layer = layer
        self.center = center
        self.end = end
        self.style = style or 'default'

    def graphic(self, uuid):
        return (
            Symbol('fp_circle'),
            (Symbol('center'), *self.center),
            (Symbol('end'), *self.end),
            (Symbol('stroke'),
             (Symbol('width'), 0.2),
             (Symbol('type'), Symbol(self.style)),
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


class Text(Shape):
    def __init__(self, layer, position, text, size=1, thickness=0.1, justify_h=None, justify_v=None):
        self.layer = layer
        self.position = position
        self.text = text
        self.size = size
        self.thickness = thickness
        self.justify_h = justify_h or 'left'
        self.justify_v = justify_v or 'bottom'

    def graphic(self, uuid):

        justify = []
        if self.justify_h not in ['middle', 'center']:
            justify.append(Symbol(self.justify_h))
        if self.justify_v not in ['middle', 'center']:
            justify.append(Symbol(self.justify_v))

        return (
            Symbol('fp_text'),
            Symbol('user'),
            self.text,
            (Symbol('at'), *self.position),
            (Symbol('effects'),
             (Symbol('font'),
              (Symbol('size'), self.size, self.size),
              (Symbol('thickness'), self.thickness),
              ),
             (Symbol('justify'), *justify),
             ),
            (Symbol('layer'), self.layer),
            (Symbol('uuid'), uuid),
        )
