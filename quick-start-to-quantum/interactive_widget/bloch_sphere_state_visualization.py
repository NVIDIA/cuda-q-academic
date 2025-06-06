# Interactive widget to visualize the state |ψ⟩ = cos(θ/2)|0⟩ + sin(θ/2)e^{iφ}|1⟩ on the Bloch sphere

def create_state_widget():
    # Clear any existing widgets
    import IPython.display
    IPython.display.clear_output()

    import cudaq
    import ipywidgets as widgets
    from ipywidgets import interactive_output, HBox, VBox
    from IPython.display import display, clear_output
    import numpy as np


    # Kernel to initialize a qubit and set it to the state |ψ⟩ = cos(θ/2)|0⟩ + sin(θ/2)e^{iφ}|1⟩
    @cudaq.kernel
    def state_kernel(theta: float, phi: float):
        qubit = cudaq.qubit()
        ry(theta, qubit)
        rz(phi, qubit)

    # Function to update the Bloch sphere plot based on the slider values
    def update_bloch_sphere(theta, phi):
        with output_bloch:
            clear_output(wait=True)  # Clear previous output
            state = cudaq.get_state(state_kernel, theta, phi)
            bloch_sphere = cudaq.add_to_bloch_sphere(state)
            cudaq.show(bloch_sphere)

    # Function to update the circuit diagram based on the slider values
    def update_circuit_diagram(theta, phi):
        with output_circuit:
            clear_output(wait=True)  # Clear previous output
            print(cudaq.draw(state_kernel, theta, phi))

    # Function to display the state in plain text with rounded angles
    def update_state_output(theta, phi):
        with output_state:
            clear_output(wait=True)  # Clear previous output
            theta_half = round(theta / 2, 3)
            phi = round(phi, 3)
            expression = f"|ψ⟩ = cos({theta_half})|0⟩ + sin({theta_half})e^(i{phi})|1⟩"
            print('|ψ⟩ = cos(θ/2)|0⟩ + sin(θ/2)e^(iφ)|1⟩')
            print(expression)

    # Create interactive sliders for angles
    slider_theta = widgets.FloatSlider(min=0, max=2*np.pi, step=0.01, value=0, description='θ:', continuous_update=False)
    slider_phi = widgets.FloatSlider(min=0, max=2*np.pi, step=0.01, value=0, description='φ:', continuous_update=False)

    # Add a new title to the widget
    title = widgets.HTML(value="<h3>Visualize the State |ψ⟩ with Varying Angles θ and φ (in radians)</h3>")

    # Display the title and sliders
    display(title)

    # Create output widgets
    output_bloch = widgets.Output()
    output_circuit = widgets.Output()
    output_state = widgets.Output()

    def update_all(theta, phi):
        update_bloch_sphere(theta, phi)
        update_circuit_diagram(theta, phi)
        update_state_output(theta, phi)

    interactive_plot = interactive_output(update_all, {'theta': slider_theta, 'phi': slider_phi})

    # Arrange sliders horizontally
    slider_box = HBox([slider_theta, slider_phi])

    # Display the state output above the sliders and the interactive plots side by side
    display(VBox([output_state, slider_box, HBox([output_bloch, output_circuit])]))

# When imported, this will create and display a new widget
if __name__ == '__main__':
    widget = create_state_widget()
    display(widget)