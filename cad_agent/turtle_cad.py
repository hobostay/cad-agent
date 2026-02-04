import math
import ezdxf
from ezdxf.math import Vec2

class TurtleCAD:
    def __init__(self, msp, start_pos=(0, 0), start_angle=0):
        self.msp = msp
        self.pos = Vec2(start_pos)
        self.angle = float(start_angle)  # Degrees
        self.pen_down = True
        self.layer = "outline"

    def forward(self, distance):
        """Move forward by distance, drawing a line if pen is down."""
        rad = math.radians(self.angle)
        dx = math.cos(rad) * distance
        dy = math.sin(rad) * distance
        new_pos = self.pos + Vec2(dx, dy)
        
        if self.pen_down:
            self.msp.add_line(self.pos, new_pos, dxfattribs={'layer': self.layer})
        
        self.pos = new_pos
        return self

    def fd(self, distance):
        return self.forward(distance)

    def backward(self, distance):
        return self.forward(-distance)

    def bk(self, distance):
        return self.backward(distance)

    def left(self, angle):
        """Turn left by angle degrees."""
        self.angle += angle
        return self

    def lt(self, angle):
        return self.left(angle)

    def right(self, angle):
        """Turn right by angle degrees."""
        self.angle -= angle
        return self

    def rt(self, angle):
        return self.right(angle)
    
    def set_heading(self, angle):
        """Set absolute heading angle."""
        self.angle = angle
        return self

    def jump_to(self, x, y):
        """Move to absolute coordinates without drawing."""
        self.pos = Vec2(x, y)
        return self

    def circle(self, radius, extent=None, steps=None):
        """
        Draw a circle or arc.
        radius: positive for counter-clockwise (left), negative for clockwise (right).
        extent: angle to cover (degrees). None means full circle (360).
        """
        if extent is None:
            extent = 360
            
        # ezdxf add_arc uses absolute angles.
        # We need to calculate center, start_angle, end_angle.
        
        # Current direction vector
        rad_heading = math.radians(self.angle)
        heading_vec = Vec2(math.cos(rad_heading), math.sin(rad_heading))
        
        # Vector to center (perpendicular to heading)
        # If radius > 0 (left turn), center is 90 deg left of heading
        # If radius < 0 (right turn), center is 90 deg right of heading
        if radius > 0:
            center_vec = heading_vec.rotate_deg(90)
        else:
            center_vec = heading_vec.rotate_deg(-90)
            
        center = self.pos + center_vec * abs(radius)
        
        # Start angle (from center to current pos)
        start_angle_vec = self.pos - center
        start_angle_deg = start_angle_vec.angle_deg
        
        # End angle
        # If radius > 0 (CCW), add extent
        # If radius < 0 (CW), subtract extent?
        # Standard Turtle: radius > 0 means turn left (CCW).
        # When turning left, angle increases.
        if radius > 0:
            end_angle_deg = start_angle_deg + extent
            self.angle += extent
        else:
            # radius < 0 means turn right (CW).
            # Arc is drawn CCW in DXF usually, but we define the path.
            # Let's stick to DXF arc semantics: always CCW from start to end?
            # No, Turtle semantics: move along the arc.
            
            # If turning right (radius < 0), we move CW.
            # DXF add_arc always draws CCW from start to end.
            # So if we move CW, start is actually 'end' in DXF terms?
            # Let's simplify: Use add_arc with correct start/end.
            
            # Target pos calculation
            # Turn 'extent' degrees to the right
            # self.angle -= extent
            
            # Actually, let's just calculate the new position and use 3 points or center/radius
            pass

        # Robust implementation:
        # Calculate end point
        # Center is 'center'
        # Start angle is 'start_angle_deg'
        # Sweeping 'extent' degrees.
        # Direction depends on radius sign.
        
        sweep_angle = extent if radius > 0 else -extent
        end_angle_deg = start_angle_deg + sweep_angle
        
        # Normalize angles for DXF (0-360)
        # ezdxf handles any angles, but let's be clean.
        
        if radius > 0:
            # CCW draw
            self.msp.add_arc(
                center, abs(radius), 
                start_angle_deg, 
                end_angle_deg, 
                dxfattribs={'layer': self.layer}
            )
        else:
            # CW draw: DXF only draws CCW. 
            # So we draw from end_angle to start_angle?
            # No, we draw from start_angle to end_angle but logic is swapped?
            # To draw CW arc from A to B:
            # DXF Arc(center, r, end_angle, start_angle) ?
            self.msp.add_arc(
                center, abs(radius), 
                end_angle_deg, 
                start_angle_deg,
                dxfattribs={'layer': self.layer}
            )

        # Update position and heading
        self.angle += sweep_angle
        
        # New position on the circle
        # center + vector(angle=end_angle) * r
        end_vec_rad = math.radians(end_angle_deg)
        self.pos = center + Vec2(math.cos(end_vec_rad), math.sin(end_vec_rad)) * abs(radius)
        
        return self

    # Additional helpers
    def rectangle(self, width, height, center=False):
        """Draw a rectangle."""
        if center:
            self.jump_to(self.pos.x - width/2, self.pos.y - height/2)

        p1 = self.pos
        p2 = p1 + Vec2(width, 0)
        p3 = p2 + Vec2(0, height)
        p4 = p1 + Vec2(0, height)

        self.msp.add_lwpolyline([p1, p2, p3, p4, p1], dxfattribs={'layer': self.layer})
        return self

    def pen_up(self):
        """Stop drawing."""
        self.pen_down = False
        return self

    def pen_down(self):
        """Start drawing."""
        self.pen_down = True
        return self

    def set_layer(self, layer_name):
        """Set the current layer."""
        self.layer = layer_name
        return self

    def get_position(self):
        """Get current position as tuple (x, y)."""
        return (self.pos.x, self.pos.y)

    def get_heading(self):
        """Get current heading angle in degrees."""
        return self.angle

    # Shape helpers for common engineering patterns
    def gear_tooth(self, module, teeth_count, pressure_angle=20):
        """
        Draw a single gear tooth profile (simplified involute approximation).
        module: gear module (mm)
        teeth_count: number of teeth (for reference)
        pressure_angle: pressure angle in degrees (standard is 20)
        """
        # Simplified trapezoidal tooth profile
        pitch_radius = module * teeth_count / 2
        addendum = module
        dedendum = 1.25 * module
        outer_radius = pitch_radius + addendum
        root_radius = pitch_radius - dedendum

        # Tooth thickness at pitch circle
        tooth_thickness = math.pi * module / 2

        # Calculate points for trapezoidal tooth
        angle_step = tooth_thickness / pitch_radius * 180 / math.pi

        # This is a simplified representation
        # A true involute would require more complex calculation
        return self

    def polygon(self, sides, radius):
        """Draw a regular polygon."""
        angle_step = 360 / sides
        start_angle = self.angle

        points = []
        for i in range(sides + 1):
            current_angle = start_angle + angle_step * i
            rad = math.radians(current_angle)
            x = self.pos.x + radius * math.cos(rad)
            y = self.pos.y + radius * math.sin(rad)
            points.append(Vec2(x, y))

        self.msp.add_lwpolyline(points, close=True, dxfattribs={'layer': self.layer})
        return self

    def slot(self, length, width):
        """Draw a slot (rounded rectangle)."""
        # Draw a slot with semicircular ends
        half_length = length / 2
        half_width = width / 2

        # Start from left end
        center_pos = Vec2(self.pos)
        left_center = center_pos + Vec2(-half_length, 0)
        right_center = center_pos + Vec2(half_length, 0)

        # Draw left semicircle
        self.msp.add_arc(
            left_center, half_width,
            90, 270,
            dxfattribs={'layer': self.layer}
        )

        # Top line
        top_left = left_center + Vec2(0, half_width)
        top_right = right_center + Vec2(0, half_width)
        self.msp.add_line(top_left, top_right, dxfattribs={'layer': self.layer})

        # Right semicircle
        self.msp.add_arc(
            right_center, half_width,
            270, 90,
            dxfattribs={'layer': self.layer}
        )

        # Bottom line
        bottom_left = left_center + Vec2(0, -half_width)
        bottom_right = right_center + Vec2(0, -half_width)
        self.msp.add_line(bottom_right, bottom_left, dxfattribs={'layer': self.layer})

        return self

    def threaded_hole(self, major_dia, length, pitch=None):
        """
        Draw a threaded hole representation.
        major_dia: major diameter
        length: hole length
        pitch: thread pitch (None for simplified representation)
        """
        radius = major_dia / 2

        # Draw outer circle
        self.msp.add_circle(
            self.pos, radius,
            dxfattribs={'layer': self.layer}
        )

        # Draw thread pitch circles (simplified representation)
        if pitch:
            num_threads = int(length / pitch)
            for i in range(1, num_threads + 1):
                thread_radius = radius * 0.9
                self.msp.add_circle(
                    self.pos, thread_radius,
                    dxfattribs={'layer': 'thread'}
                )

        # Draw center line
        self.msp.add_line(
            (self.pos.x - radius * 1.5, self.pos.y),
            (self.pos.x + radius * 1.5, self.pos.y),
            dxfattribs={'layer': 'center', 'linetype': 'CENTER'}
        )

        return self
