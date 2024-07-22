module = """
        r = 22/2;
        rs = 3.2/2;

        translate([-5, 0, r+1.5])
        rotate([0, 90, 0])
            cylinder(10, r, r);

        translate([-5, -19.8/2, 1.5+r+19.8/2])
        rotate([0, 90, 0])
            cylinder(10, rs, rs);

        translate([-5, 19.8/2, 1.5+r-19.8/2])
        rotate([0, 90, 0])
            cylinder(10, rs, rs);
"""

import zlib
import base64
compressed = zlib.compress(module.encode())
encoded = base64.b64encode(compressed).decode()
print(encoded)

ec2 = base64.b64encode(module.encode()).decode()
print(ec2)