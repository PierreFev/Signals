import pyglet
import math

from pyglet import shapes, text
from pyglet.window import mouse

import devices
import render
import network
from gui import GUI
from simulation import Simulation

c_blue = (51, 92, 103)
c_beige = (255, 243, 176)
c_orange = (224, 159, 62)
c_red = (158, 42, 43)
c_dark_red = (84, 11, 14)
# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    window = pyglet.window.Window(width=1600, height=800)
    simulation = Simulation()
    #for i in range(20):
    #    for j in range(30):
    #        simulation.add_device_to_world(devices.ConnectorDevice((i*50,j*50)))
    theme = {'background_color': c_blue, 'gui_frame_color': c_orange, 'node_selection':c_red, 'wire_color': c_orange}
    gui = GUI(window, simulation, theme)

    renderer = render.Renderer(window, theme)
    @window.event
    def on_mouse_motion(x, y, dx, dy):
        gui.update_mouse_position(x, y)

    #@window.event
    #def on_key_release(symbol, modifiers):
    #    if symbol == 32:
    #        simulation.current_mode += 1
    #        simulation.current_mode %= len(MODES)
    #        print('mode: ', MODES[simulation.current_mode])

    @window.event
    def on_mouse_release(x, y, button, modifiers):
        if not gui.on_mouse_release_event(x, y, button, modifiers):
            pass
            #simulation.on_mouse_release(x, y, button, modifiers)


    @window.event
    def on_draw():
        window.clear()
        batch = pyglet.graphics.Batch()
        #gui.render_background(batch=batch)

        out = renderer.render_simulation(simulation, batch)

        batch.draw()
        gui.render()




    pyglet.clock.schedule_interval(simulation.update, 1 / 4.0)
    pyglet.app.run()
