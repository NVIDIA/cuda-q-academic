def create_t_and_s_widget():
    # Clear any existing widgets
    import IPython.display
    IPython.display.clear_output()
    
    import cudaq
    import ipywidgets as widgets
    from ipywidgets import interactive_output, HBox, VBox
    from IPython.display import display, clear_output
    import numpy as np

    # Kernel to initialize a qubit and apply T or S gate
    @cudaq.kernel
    def state_kernel(theta: float, phi: float, gate_choice: int):
        qubit = cudaq.qubit()
        ry(theta, qubit)
        rz(phi, qubit)
        
        if gate_choice == 1:
            t(qubit)
        elif gate_choice == 2:
            s(qubit)

    # Function to update the Bloch sphere plots
    def update_bloch_spheres(theta, phi):
        with output_bloch:
            clear_output(wait=True)
            
            bloch_spheres = []
            
            # Get all three states
            initial_state = cudaq.get_state(state_kernel, theta, phi, 0)
            t_state = cudaq.get_state(state_kernel, theta, phi, 1)
            s_state = cudaq.get_state(state_kernel, theta, phi, 2)
            
            # Create Bloch spheres
            bloch_spheres.append(cudaq.add_to_bloch_sphere(initial_state))
            bloch_spheres.append(cudaq.add_to_bloch_sphere(t_state))
            bloch_spheres.append(cudaq.add_to_bloch_sphere(s_state))
            
            # Show all three spheres
            cudaq.show(bloch_spheres, nrows=1, ncols=3)
            print("Initial State | After T Gate | After S Gate")

    # Function to display the state in plain text
    def update_state_output(theta, phi):
        with output_state:
            clear_output(wait=True)
            theta_half = round(theta / 2, 3)
            phi = round(phi, 3)
            expression = f"|ψ⟩ = cos({theta_half})|0⟩ + sin({theta_half})e^(i{phi})|1⟩"
            print('Initial state:')
            print(expression)

    # Create interactive controls
    slider_theta = widgets.FloatSlider(min=0, max=2*np.pi, step=0.01, value=0, 
                                     description='θ:', continuous_update=False)
    slider_phi = widgets.FloatSlider(min=0, max=2*np.pi, step=0.01, value=0, 
                                   description='φ:', continuous_update=False)

    # Create output widgets
    output_bloch = widgets.Output()
    output_state = widgets.Output()

    def update_all(theta, phi):
        update_bloch_spheres(theta, phi)
        update_state_output(theta, phi)

    # Create interactive output
    interactive_plot = interactive_output(
        update_all, 
        {
            'theta': slider_theta, 
            'phi': slider_phi,
        }
    )

    # Layout
    title = widgets.HTML(value="<h3>Comparing T and S Gates on Quantum States</h3>")
    slider_box = HBox([slider_theta, slider_phi])

    # Create and return the widget
    widget = VBox([
        title,
        output_state,
        slider_box,
        output_bloch
    ])
    
    return widget

# When imported, this will create and display a new widget
if __name__ == '__main__':
    widget = create_t_and_s_widget()
    display(widget)
