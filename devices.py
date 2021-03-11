from pyglet import shapes
from pyglet.window import mouse

import network


class Device:
    nodes_arguments = []
    con_indices = []

    def __init__(self, pos, size=(50, 50)):
        self.nodes = [network.Node(arg[0],self, arg[1]) for arg in self.nodes_arguments]
        self.pos = pos
        self.size = size
        self.world = None
        if pos is not None:
            for n in self.nodes:
                old_pos = n.pos
                n.pos = tuple(old_pos[i] + self.pos[i] for i in [0, 1])
        for c in self.con_indices:
            con = network.Connection(self.nodes[c[0]], self.nodes[c[1]], c[2])
            self.nodes[c[0]].connections.add(con)

    def update(self):
        pass
    def change_connections(self):
        pass

    def on_mouse_event(self, global_x, global_y, button, release):
        pass


class SourceDevice(Device):
    nodes_arguments = [((25, 25), True)]

    def __init__(self, pos):
        super().__init__(pos, (50, 50))


class ConnectorDevice(Device):
    nodes_arguments = [((25, 25), False)]

    def __init__(self, pos):
        super().__init__(pos, (50, 50))

class LampDevice(Device):
    nodes_arguments = [((25, 25), False)]

    def __init__(self, pos):
        self.state = False
        super().__init__(pos, (50, 50))

    def update(self):
        self.state = self.nodes[0].state
        super().update()

class ValveDevice(Device):
    nodes_arguments = [((10, 10), False), ((40, 10), False), ((25, 40), False)]
    con_indices = [(0, 1, 0), (1, 0, 16)]
    def __init__(self, pos):
        self.state = False
        super().__init__(pos, (50, 50))

    def update(self):
        manager = self.world.simulation.net_manager
        cathode = self.nodes[0]
        anode = self.nodes[1]
        gate = self.nodes[2]

        out = cathode.state-gate.state
        if out < 0:
            out = 0

        manager.update_connection(cathode, anode, 16-out)

        super().update()

class ResistorDevice(Device):
    nodes_arguments = [((10, 25), False), ((40, 25), False)]
    con_indices = [(0, 1, 1), (1, 0, 1)]


class DiodeDevice(Device):
    nodes_arguments = [((10, 25), False), ((40, 25), False)]
    con_indices = [(0, 1, 0), (1, 0, 16)]


class SwitchDevice(Device):
    nodes_arguments = [((10, 25), False), ((40, 25), False)]
    con_indices = [(0, 1, 0), (1, 0, 0)]

    def __init__(self, pos):
        self.state = True
        super().__init__(pos)

    def switch_state(self):
        print('switch')
        manager = self.world.simulation.net_manager
        node1 = self.nodes[0]
        node2 = self.nodes[1]
        if self.state:
            manager.update_connection( node1,node2,16)
            manager.update_connection( node2,node1,16)
        else:
            manager.update_connection( node1,node2,0)
            manager.update_connection( node2,node1,0)

        self.state = not self.state

    def on_mouse_event(self, global_x, global_y, button, release):
        if button is mouse.LEFT and release is True:
            self.switch_state()
        super().on_mouse_event(global_x, global_y, button, release)


class BreakerSwitchDevice(SwitchDevice):

    def switch_state(self):
        print('switch')
        manager = self.world.simulation.net_manager
        node1 = self.nodes[0]
        node2 = self.nodes[1]
        if self.state:
            manager.update_connection( node1,node2,None)
            manager.update_connection( node2,node1,None)
        else:
            manager.update_connection( node1,node2,0)
            manager.update_connection( node2,node1,0)

        self.state = not self.state