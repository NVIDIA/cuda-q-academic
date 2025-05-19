# Generates an interactive visualization of the CNOT gate 
def create_CNOT_widget():
    # Clear any existing widgets
    import IPython.display
    IPython.display.clear_output()

    import cudaq
    import numpy as np
    import matplotlib.pyplot as plt
    from IPython.display import display, HTML, clear_output
    import ipywidgets as widgets
    from ipywidgets import interactive_output, HBox, VBox

    @cudaq.kernel
    def initialize(qubits: cudaq.qview, state: list[int]):
        """Kernel to initialize the state indicated by the given list
        0: |0>, 1: |1>, 2: |+>, 3: |->"""
        for idx in range(len(state)):
            if state[idx] == 1:
                x(qubits[idx])
            elif state[idx] == 2:  # |+>
                h(qubits[idx])
            elif state[idx] == 3:  # |->
                x(qubits[idx])
                h(qubits[idx])

    @cudaq.kernel
    def CNOT_example(state: list[int]):
        """Apply CNOT to the state given by the state numbers"""
        qubits = cudaq.qvector(2)
        # Initialize state
        initialize(qubits, state)
        # Apply CNOT
        x.ctrl(qubits[0], qubits[1])

    # Function to format complex number nicely
    def format_complex(c):
        if abs(c.imag) < 1e-10:  # Real number
            return f"{c.real:.3f}"
        elif abs(c.real) < 1e-10:  # Imaginary number
            if abs(c.imag - 1) < 1e-10:
                return "i"
            elif abs(c.imag + 1) < 1e-10:
                return "-i"
            else:
                return f"{c.imag:.3f}i"
        else:
            sign = "+" if c.imag >= 0 else "-"
            return f"{c.real:.3f}{sign}{abs(c.imag):.3f}i"

    # Function to update the circuit diagram
    def update_circuit(q0_state, q1_state):
        with output_circuit:
            clear_output(wait=True)
            print("Circuit:")
            state_list = [q0_state, q1_state]
            print(cudaq.draw(CNOT_example, state_list))

    # Function to update the probability distribution
    def update_prob_chart(q0_state, q1_state):
        with output_prob:
            clear_output(wait=True)
            
            # Get the state after circuit execution
            state_list = [q0_state, q1_state]
            state = cudaq.get_state(CNOT_example, state_list)
            
            # Calculate probabilities using Born's rule
            probs = np.abs(state)**2
            
            plt.figure(figsize=(6,4))
            plt.bar(['|00⟩', '|01⟩', '|10⟩', '|11⟩'], probs, color='#76b900')  # NVIDIA green
            plt.ylim(0, 1)
            plt.ylabel('Probability')
            plt.title('Measurement Probability Distribution')
            plt.show()

    # Function to update the final state display
    def update_final_state(q0_state, q1_state):
        with output_state:
            clear_output(wait=True)
            state_list = [q0_state, q1_state]
            state = cudaq.get_state(CNOT_example, state_list)
            
            print("Final State:")
            state_str = ""
            basis_states = ['|00⟩', '|01⟩', '|10⟩', '|11⟩']
            
            # Find first non-zero term
            first_term = True
            for i, (amplitude, basis) in enumerate(zip(state, basis_states)):
                if abs(amplitude) > 1e-10:  # Only show non-zero terms
                    if first_term:
                        state_str += f"({format_complex(amplitude)}){basis}"
                        first_term = False
                    else:
                        # Add explicit + or - sign
                        if amplitude.real < 0:
                            state_str += f"<span style='color: red'>-</span>({format_complex(abs(amplitude))}){basis}"
                        else:
                            state_str += f"+({format_complex(abs(amplitude))}){basis}"
            
            display(HTML(state_str))

    # Add titles
    main_title = widgets.HTML(value="<h3>Two-Qubit CNOT Gate Visualization</h3>")
    initial_state_title = widgets.HTML(value="<h4>Initial States:</h4>")

    # Create dropdowns for each qubit
    q0_dropdown = widgets.Dropdown(
        options=[('|0⟩', 0), ('|1⟩', 1), ('|+⟩', 2), ('|-⟩', 3)],
        value=0,
        description='Qubit 0:',
    )

    q1_dropdown = widgets.Dropdown(
        options=[('|0⟩', 0), ('|1⟩', 1), ('|+⟩', 2), ('|-⟩', 3)],
        value=0,
        description='Qubit 1:',
    )

    # Create output widgets
    output_circuit = widgets.Output()
    output_prob = widgets.Output()
    output_state = widgets.Output()

    def update_all(change):
        update_circuit(q0_dropdown.value, q1_dropdown.value)
        update_prob_chart(q0_dropdown.value, q1_dropdown.value)
        update_final_state(q0_dropdown.value, q1_dropdown.value)

    # Observe changes in dropdowns
    q0_dropdown.observe(update_all, names='value')
    q1_dropdown.observe(update_all, names='value')

    # Display everything
    display(VBox([
        main_title,
        initial_state_title,
        HBox([q0_dropdown, q1_dropdown]),
        output_circuit,
        output_state,
        output_prob
    ]))

    # Initial update
    update_circuit(q0_dropdown.value, q1_dropdown.value)
    update_prob_chart(q0_dropdown.value, q1_dropdown.value)
    update_final_state(q0_dropdown.value, q1_dropdown.value)

# When imported, this will create and display a new widget
if __name__ == '__main__':
    widget = create_CNOT_widget()
    display(widget)
