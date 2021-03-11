import pyglet
from pyglet import shapes, text
from pyglet.window import mouse

import devices
import render
import simulation
from network import Node


class GUIButton:
    def __init__(self, name, item):
        self.name = name
        self.item = item


class GUIMode:
    def __init__(self, name, cursor='default'):
        self.name = name
        self.cursor = cursor


class DevicePlacementMode(GUIMode):
    def __init__(self, device_cls):
        self.device_cls = device_cls
        super().__init__('device_placement')




class GUI:

    def __init__(self, window, sim, theme):
        self.size_x, self.size_y = window.get_size()
        self.simulation = sim
        self.window = window
        self.buttons = [GUIButton(*t) for t in
                        [('Source', devices.SourceDevice(None)), ('Connector', devices.ConnectorDevice(None)),
                         ('Resistor', devices.ResistorDevice(None)),('diode', devices.DiodeDevice(None)),
                         ('breaker switch', devices.BreakerSwitchDevice(None)),('switch', devices.SwitchDevice(None)),
                         ('valve', devices.ValveDevice(None)),
                         ('lamp', devices.LampDevice(None)),('Wire', None)]]
        self.mouse_pos_x = 0
        self.mouse_pos_y = 0

        self.current_mode = None

        self.theme = theme

    def on_mouse_event_on_world(self,x,y,button,modifiers):

        if self.current_mode is None:
            if button == mouse.LEFT:
                self.simulation.select_element_at(x,y)
            elif button == mouse.RIGHT:
                self.simulation.delete_element_at(x,y)
            return


        if isinstance(self.current_mode, DevicePlacementMode):
            device = self.current_mode.device_cls((x,y))
            self.simulation.add_device_to_world(device)

        if self.current_mode.name == 'wire_placement':
            old_sel = self.simulation.selected_element
            self.simulation.select_element_at(x, y)
            new_sel = self.simulation.selected_element
            if isinstance(old_sel, Node) and isinstance(new_sel, Node):
                self.simulation.create_wire_connection(old_sel, new_sel)
                self.simulation.selected_element = None


    def on_mouse_release_event(self, x, y, button, modifiers):

        if (button == mouse.RIGHT):
            self.current_mode = None
            self.simulation.selected_element = None
        if y > 100:
            self.on_mouse_event_on_world(x,y,button,modifiers)

        element = self.get_gui_element_at(x, y)
        if element is None:
            return True

        if (button == mouse.LEFT):

            element = self.get_gui_element_at(x,y)
            if isinstance(element, GUIButton):
                if isinstance(element.item, devices.Device):
                    self.current_mode = DevicePlacementMode(type(element.item))
                    self.simulation.selected_element = None
                if element.name == 'Wire':
                    self.current_mode = GUIMode('wire_placement')
                    self.simulation.selected_element = None
        return False


    def get_gui_element_at(self, x, y):
        for i, b in enumerate(self.buttons):
            size = 80
            posx = 20 + i * (size + 10)
            posy = 10

            if (posx < x < posx + size and posy < y < posy + size):
                return b
        return None

    def update_mouse_position(self, x, y):
        self.mouse_pos_x = x
        self.mouse_pos_y = y

    def render_background(self, batch):
        group = pyglet.graphics.OrderedGroup(0)
        shape = shapes.Rectangle(0, 0, self.size_x, self.size_y, color=self.theme.get('background_color'),batch=batch)
        shape.draw()

    def render(self):
        self.window.set_mouse_cursor()
        shape = shapes.Rectangle(0, 0, self.size_x, 100, color=self.theme.get('gui_frame_color'))
        shape.draw()
        for i, b in enumerate(self.buttons):
            size = 80
            posx = 20 + i * (size + 10)
            posy = 10
            overed = posx < self.mouse_pos_x < posx + size and posy < self.mouse_pos_y < posy + size
            self.render_button(b, (posx, posy), (size, size), overed=overed)

    def render_button(self, button, pos, size, overed=False, selected=False):
        b_color = (50, 50, 50) if overed else (0, 0, 0)
        box = shapes.BorderedRectangle(pos[0], pos[1], size[0], size[1], color=b_color, border_color=(255, 255, 255))
        dev = button.item
        label = text.Label(button.name, x=pos[0] + size[0] / 2, y=pos[1] + size[1] / 2, anchor_x='center',
                           anchor_y='center')
        box.draw()
        #if dev is not None:
        #    self.draw_device(dev, pos[0] + 10, pos[1] + 10)
        label.draw()
