# Interactive widget to visualize the final qubit state on the Bloch sphere after rotating about the X, Y, and Z axes with varying angles (θx, θy, θz in radians)

def create_rotation_widget():
    # Clear any existing widgets
    import IPython.display
    IPython.display.clear_output()

    import cudaq
    import ipywidgets as widgets
    from ipywidgets import interactive_output, HBox, VBox
    from IPython.display import display, clear_output
    import numpy as np

    # Kernel to initialize a qubit in the zero ket state and rotate it about the x, y, and z axis by given angles
    @cudaq.kernel
    def rotation_kernel(theta_x: float, theta_y: float, theta_z: float):
        qubit = cudaq.qubit()
        rx(theta_x, qubit)
        ry(theta_y, qubit)
        rz(theta_z, qubit)

    # Function to update the Bloch sphere plot based on the slider values
    def update_bloch_sphere(theta_x, theta_y, theta_z):
        state = cudaq.get_state(rotation_kernel, theta_x, theta_y, theta_z)
        bloch_sphere = cudaq.add_to_bloch_sphere(state)
        cudaq.show(bloch_sphere)

    # Function to update the circuit diagram based on the slider values
    def update_circuit_diagram(theta_x, theta_y, theta_z):
        # Draw the circuit diagram
        print(cudaq.draw(rotation_kernel, theta_x, theta_y, theta_z))

    # Create interactive sliders for angles
    slider_x = widgets.FloatSlider(min=0, max=2*np.pi, step=0.01, value=0, description='θx:', continuous_update=False)
    slider_y = widgets.FloatSlider(min=0, max=2*np.pi, step=0.01, value=0, description='θy:', continuous_update=False)
    slider_z = widgets.FloatSlider(min=0, max=2*np.pi, step=0.01, value=0, description='θz:', continuous_update=False)

    # Add a new title to the widget
    title = widgets.HTML(value="<h3>Visualize the Final Qubit State on the Bloch Sphere after Rotating about the X, Y and Z Axis with Varying Angles (θx, θy, θz in radians)</h3>")

    # Create interactive outputs
    output_bloch = widgets.Output()
    output_circuit = widgets.Output()

    def update_all(theta_x, theta_y, theta_z):
        with output_bloch:
            output_bloch.clear_output(wait=True)
            update_bloch_sphere(theta_x, theta_y, theta_z)
        with output_circuit:
            output_circuit.clear_output(wait=True)
            update_circuit_diagram(theta_x, theta_y, theta_z)

    # Observe changes in sliders and update the outputs
    slider_x.observe(lambda _: update_all(slider_x.value, slider_y.value, slider_z.value), 'value')
    slider_y.observe(lambda _: update_all(slider_x.value, slider_y.value, slider_z.value), 'value')
    slider_z.observe(lambda _: update_all(slider_x.value, slider_y.value, slider_z.value), 'value')

    # Arrange sliders horizontally
    slider_box = HBox([slider_x, slider_y, slider_z])

    # Single display statement for the entire widget
    display(VBox([
        title,
        slider_box,
        HBox([output_bloch, output_circuit])
    ]))

    # Initial update
    update_all(slider_x.value, slider_y.value, slider_z.value)


# When imported, this will create and display a new widget
if __name__ == '__main__':
    widget = create_rotation_widget()
    display(widget)
