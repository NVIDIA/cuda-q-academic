import numpy as np
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display

def run_simulations(num_sims, num_syndromes, mean_decode, sd_decode):
    """
    Returns an array of shape (num_sims, num_syndromes),
    where each row is the cumulative decode time for all syndromes.
    """
    simulations = []
    for _ in range(num_sims):
        decode_times = np.random.normal(mean_decode, sd_decode, num_syndromes)
        # Avoid negative times
        decode_times = np.maximum(decode_times, 0)
        cumulative_times = np.cumsum(decode_times)
        simulations.append(cumulative_times)
    return np.array(simulations)

def plot_simulations(num_sims=50, num_syndromes=50, mean_decode=1.0, sd_decode=0.2, decoding_window=100.0):
    """
    Run 'num_sims' Monte Carlo simulations and plot each cumulative trajectory.
    Color the trajectory green if its final time is below decoding_window,
    otherwise red. Show the percentage of failed runs (red lines).
    """
    results = run_simulations(num_sims, num_syndromes, mean_decode, sd_decode)
    final_times = results[:, -1]  # final time for each simulation
    count_failed = np.sum(final_times > decoding_window)
    percent_failed = (count_failed / num_sims) * 100

    plt.figure(figsize=(8,5))
    for i in range(num_sims):
        color = 'green' if results[i, -1] < decoding_window else 'red'
        plt.plot(results[i], color=color, alpha=0.6)

    # Horizontal decoding window line
    plt.axhline(y=decoding_window, color='blue', linestyle='--', label='Decoding Window')
    plt.xlabel('Syndrome Index')
    plt.ylabel('Total round Decoding Time')

    plt.title(
        f"Monte Carlo Simulations of Decoding Times\n"
        f"{percent_failed:.1f}% failed (red lines)"
    )
    plt.legend()
    plt.show()

def create_decoding_widgets():
    """
    Create and return the widgets UI (sliders) and the interactive output connected to plot_simulations.
    """
    slider_layout = widgets.Layout(width='700px')
    slider_style = {'description_width': '250px'}

    num_sims_slider = widgets.IntSlider(
        value=50, min=10, max=200, step=10, description='Number of Simulations:', layout=slider_layout, style=slider_style
    )
    mean_decode_slider = widgets.FloatSlider(
        value=1.0, min=0.1, max=3.0, step=0.1, description='Mean Syndrome Decoding Time:', layout=slider_layout, style=slider_style
    )
    sd_decode_slider = widgets.FloatSlider(
        value=1.0, min=0.01, max=3.0, step=0.01, description='SD of Syndrome Decoding Time:', layout=slider_layout, style=slider_style
    )
    decoding_window_slider = widgets.FloatSlider(
        value=70.0, min=20.0, max=120.0, step=10.0, description='Decoding Window:', layout=slider_layout, style=slider_style
    )

    ui = widgets.VBox([
        num_sims_slider,
        mean_decode_slider,
        sd_decode_slider,
        decoding_window_slider
    ])

    out = widgets.interactive_output(
        plot_simulations,
        {
            'num_sims': num_sims_slider,
            'mean_decode': mean_decode_slider,
            'sd_decode': sd_decode_slider,
            'decoding_window': decoding_window_slider
        }
    )

    return ui, out

def display_widget():
    """
    A convenient function to display the widget in your notebook.
    """
    ui, out = create_decoding_widgets()
    display(ui, out)


