import math
import time
from pyglet.window import mouse

import devices
import network

NODE_SIZE = 10
class Simulation:

    def __init__(self):
        self.current_mode = 2
        self.selected_element = None
        self.world = World()
        self.world.simulation = self
        self.net_manager = network.NetworkManager()
        self.fps = 0
        self.need_redraw = True

    def add_device_to_world(self, device):
        self.world.devices.append(device)
        device.world = self.world
        for n in device.nodes:
            if n.is_source:
                self.net_manager.create_net(n)
        self.need_redraw = True

    def remove_wire_connection(self, wire):
        self.world.wires.remove(wire)
        self.net_manager.remove_connection(wire.n1, wire.n2)
        self.net_manager.remove_connection(wire.n2, wire.n1)
        self.need_redraw = True

    def create_wire_connection(self, node1, node2):
        if node1 == node2:
            print('cant connect the same node')
            return
        self.world.wires.append(Wire(node1, node2))
        self.net_manager.create_connection(node1, node2)
        self.net_manager.create_connection(node2, node1)
        self.need_redraw = True

    def update(self, dt):

        self.net_manager.update()
        for dev in self.world.devices:
            dev.update()

        self.fps = 1./dt


    def delete_element_at(self,x,y):
        element = self.get_element_at(x,y)
        if isinstance(element, Wire):
            self.remove_wire_connection(element)
            return

    def get_element_at(self,x,y):
        #we check for wires
        wire = self.world.get_wire_at(x,y)
        if wire is not None:
            return wire
        node = self.world.get_closest_node(x,y)
        if node is not None:
            return node
        device = self.world.get_closest_device(x, y)
        if device is not None:
            return device
        return None

    def select_element_at(self, x,y):

        element = self.get_element_at(x,y)

        if isinstance(element, network.Node):
            self.selected_element = element
            return
        if isinstance(element, devices.Device):
            element.on_mouse_event(x, y, mouse.LEFT, True)
            self.selected_element = element
            return

class Wire:
    def __init__(self, node1, node2):
        self.n1 = node1
        self.n2 = node2
class World:
    def __init__(self):
        self.wires = []
        self.devices = []
        self.simulation = None

    def get_closest_device(self, x, y):
        for d in self.devices:
            if d.pos[0] < x < d.pos[0] + d.size[0]:
                if d.pos[1] < y < d.pos[1] + d.size[1]:
                    return d
        return None

    def get_closest_node(self, x, y, radius = NODE_SIZE):
        for d in self.devices:
            for n in d.nodes:
                if (n.pos[0] - x) ** 2 + (n.pos[1] - y) ** 2 < radius ** 2:
                    return n
        return None

    def get_wire_at(self, x, y):
        for w in self.wires:
            if self.is_near_wire(w, x, y):
                return w
        return None

    def is_near_wire(self, wire, x, y):
        x0 = wire.n1.pos[0]
        y0 = wire.n1.pos[1]
        x1 = wire.n2.pos[0]
        y1 = wire.n2.pos[1]

        v = ((x - x0), (y - y0))
        dist = math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)
        u = ((x1 - x0) / dist, (y1 - y0) / dist)

        dot = sum(v[i] * u[i] for i in [0, 1])
        if dot < 0 or dot > dist:
            return False
        b0 = v[0] - dot * u[0]
        b1 = v[1] - dot * u[1]

        return (b0 ** 2 + b1 ** 2) < 5 ** 2