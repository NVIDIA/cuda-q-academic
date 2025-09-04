def create_borns_rule_widget():
    # Clear any existing widgets
    import IPython.display
    IPython.display.clear_output()
    # Widget to visualize Born's Rule for the state |ψ⟩ = cos(θ/2)|0⟩ + sin(θ/2)e^{iφ}|1⟩ along with its Bloch sphere representation
    import cudaq
    import ipywidgets as widgets
    from ipywidgets import interactive_output, HBox, VBox
    from IPython.display import display, clear_output
    import numpy as np
    import matplotlib.pyplot as plt

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

    # Function to update the probability amplitude bar chart
    def update_prob_chart(theta, phi):
        with output_prob:
            clear_output(wait=True)  # Clear previous output
            alpha_squared = np.cos(theta/2)**2
            beta_squared = np.sin(theta/2)**2
            
            plt.figure(figsize=(4,4))  # Make the figure square and smaller
            plt.bar(['0', '1'], [alpha_squared, beta_squared], color=['#76b900', '#76b900'])  # NVIDIA green
            plt.ylim(0, 1)
            plt.ylabel('Probability')
            plt.title('Measurement Probability Distribution')
            plt.show()

    # Function to display the state in plain text with rounded angles
    def update_state_output(theta, phi):
        with output_state:
            clear_output(wait=True)  # Clear previous output
            theta_half = round(theta / 2, 3)
            phi = round(phi, 3)
            expression = f"|ψ⟩ = cos({theta_half})|0⟩ + sin({theta_half})e^(i{phi})|1⟩"
            print('|ψ⟩ = cos(θ/2)|0⟩ + sin(θ/2)e^(iφ)|1⟩ = α|0⟩ + β|1⟩')
            print(expression)
            alpha = np.cos(theta_half)
            beta = np.sin(theta_half) * np.exp(1j * phi)
            alpha_squared = np.abs(alpha)**2
            beta_squared = np.abs(beta)**2
            print(f"|α|^2: {alpha_squared:.3f}")
            print(f"|β|^2: {beta_squared:.3f}")

    # Create interactive sliders for angles
    slider_theta = widgets.FloatSlider(min=0, max=2*np.pi, step=0.01, value=0, description='θ:', continuous_update=False)
    slider_phi = widgets.FloatSlider(min=0, max=2*np.pi, step=0.01, value=0, description='φ:', continuous_update=False)

    # Add a new title to the widget
    title = widgets.HTML(value="<h3>Visualize Born's Rule for the State |ψ⟩ with Varying Angles θ and φ (in radians)</h3>")

    # Create output widgets
    output_bloch = widgets.Output()
    output_prob = widgets.Output()
    output_state = widgets.Output()

    def update_all(theta, phi):
        update_bloch_sphere(theta, phi)
        update_prob_chart(theta, phi)
        update_state_output(theta, phi)

    # Create the interactive output and immediately call update_all with initial values
    interactive_plot = interactive_output(update_all, {'theta': slider_theta, 'phi': slider_phi})

    # Arrange sliders horizontally
    slider_box = HBox([slider_theta, slider_phi])

    # Single display statement for the entire widget
    display(VBox([
        title,
        output_state,
        slider_box,
        HBox([output_bloch, output_prob])
    ]))
    
# When imported, this will create and display a new widget
if __name__ == '__main__':
    widget = create_borns_rule_widget()
    display(widget)