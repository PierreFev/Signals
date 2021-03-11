import pyglet
from pyglet import shapes, text

from devices import LampDevice
from network import Node

NODE_SIZE = 10
net_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255)]


class Renderer:
    group_background = pyglet.graphics.OrderedGroup(0)

    group_device_background = pyglet.graphics.OrderedGroup(10)
    group_wires = pyglet.graphics.OrderedGroup(11)
    group_device_foreground = pyglet.graphics.OrderedGroup(12)

    group_network_connections = pyglet.graphics.OrderedGroup(20)
    group_network_nodes = pyglet.graphics.OrderedGroup(21)
    group_network_text = pyglet.graphics.OrderedGroup(22)

    group_selection = pyglet.graphics.OrderedGroup(30)


    def __init__(self, window, theme):
        self.theme = theme
        self.window = window

    def render_simulation(self,simulation, batch):

        window_size = self.window.get_size()

        output = []
        # render devices/nodes
        for d in simulation.world.devices:
            is_selected = (d == simulation.selected_element)
            output += self.draw_device(d, d.pos[0], d.pos[1], is_selected, batch=batch)

        #render wire

        for wire in simulation.world.wires:
            pos0 = wire.n1.pos
            pos1 = wire.n2.pos
            line = shapes.Line(pos0[0], pos0[1], pos1[0], pos1[1], width=4, color=self.theme.get('wire_color'),batch=batch,group = Renderer.group_wires)
            output.append(line)
        # render selected node
        if isinstance(simulation.selected_element, Node):
            n = simulation.selected_element
            x = n.pos[0]
            y = n.pos[1]
            shape = shapes.Circle(x=x, y=y, radius=NODE_SIZE / 2+5, color=self.theme.get('node_selection'),batch=batch, group=Renderer.group_selection)
            if n.is_source:
                shape = shapes.Rectangle(x - NODE_SIZE / 2, y - NODE_SIZE / 2, NODE_SIZE+2, NODE_SIZE+2, color=self.theme.get('node_selection'),batch=batch,group=Renderer.group_selection)
            output.append(shape)
        # render networks
        for net in simulation.net_manager.networks:
            output += self.render_network(net, batch)

        fps_counter = text.Label('FPS: {0:.3f}'.format(simulation.fps), color=(255,255,255,255),
                           font_name='Arial',
                           font_size=12,
                           x=5, y=window_size[1]-20,
                           anchor_x='left', anchor_y='center',batch=batch, group = Renderer.group_network_text)
        output.append(fps_counter)
        return output

    def render_network(self,net, batch):
        color = net_colors[net.id % len(net_colors)]
        output = []
        for n in net.nodes:
            output+=self.draw_node(n, color, batch)
        return output



    def draw_device(self,device, x,y, selected, batch):
        inside_color = (0,0,0) if not selected else (50,50,50)
        output = []
        box = shapes.BorderedRectangle(x, y, device.size[0], device.size[1],
                                       color=inside_color,batch=batch, group=Renderer.group_device_background)
        output.append(box)
        color = (100, 100, 100)

        if isinstance(device, LampDevice):
            state = device.state
            light_color = (int(252*state/16), int(186*state/16), int(3*state/16))
            light_shape = shapes.Circle(x=x + 10, y=y + 10, radius=10, color=light_color,batch=batch, group=Renderer.group_device_foreground)
            output.append(light_shape)

        for c in device.con_indices:
            pos0 = device.nodes_arguments[c[0]][0]
            pos1 = device.nodes_arguments[c[1]][0]
            line = shapes.Line(x+pos0[0], y+pos0[1], x+pos1[0], y+pos1[1], width=4, color=(100, 100, 100), batch=batch, group=Renderer.group_device_foreground)
            output.append(line)

        for n in device.nodes_arguments:
            shape = shapes.Circle(x=x+n[0][0], y=y+n[0][1], radius=NODE_SIZE / 2, color=color, batch=batch, group=Renderer.group_device_foreground)
            if n[1]:
                shape = shapes.Rectangle(x+n[0][0] - NODE_SIZE / 2, y+n[0][1] - NODE_SIZE / 2, NODE_SIZE, NODE_SIZE,
                                         color=color, batch=batch, group=Renderer.group_device_foreground)
            output.append(shape)
        return output



    def draw_node(self,node, net_color, batch):

        x = node.pos[0]
        y = node.pos[1]
        output = []
        shape = shapes.Circle(x=x, y=y, radius=NODE_SIZE / 4, color=net_color, batch=batch, group = Renderer.group_network_nodes)
        output.append(shape)
        color = (255, 255, 255, 255)
        if node.current_net is not None:
            color = net_colors[node.current_net % len(net_colors)]
            color = (color[0], color[1], color[2], 255)
        label = text.Label(str(node.state), color=color,
                           font_name='Arial',
                           font_size=12,
                           x=x, y=y + 20,
                           anchor_x='center', anchor_y='center', batch=batch, group = Renderer.group_network_text)
        output.append(label)
        for c in node.connections:
            line = shapes.Line(c.node1.pos[0], c.node1.pos[1], c.node2.pos[0], c.node2.pos[1], width=2, color=net_color, batch=batch, group = Renderer.group_network_connections)
            output.append(line)
        return output
