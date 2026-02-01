# -*- coding: utf-8 -*-
import ezdxf
from ezdxf import units

doc = ezdxf.new("R2010", setup=True)
doc.units = units.MM

doc.layers.add("outline", color=1)
doc.layers.add("hole", color=2)

msp = doc.modelspace()

# 100×60 矩形底板，原点左下角
msp.add_lwpolyline(
    [(0, 0), (100, 0), (100, 60), (0, 60), (0, 0)],
    close=True,
    dxfattribs={"layer": "outline"},
)

# 四角圆孔 φ10，距边 10mm → (10,10), (90,10), (90,50), (10,50)
for x, y in [(10, 10), (90, 10), (90, 50), (10, 50)]:
    msp.add_circle(
        center=(x, y),
        radius=5.0,
        dxfattribs={"layer": "hole"},
    )

doc.saveas("test_plate.dxf")
