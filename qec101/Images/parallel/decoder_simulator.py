import numpy as np
import matplotlib.pyplot as plt
import math

# NVIDIA-inspired color palette
NVIDIA_GREEN = '#76B900'
NVIDIA_BLACK = '#000000'
NVIDIA_DARK_GREY = '#1A1A1A'
NVIDIA_LIGHT_GREY = '#E0E0E0'
NVIDIA_ALERT = '#FFD700' 

plt.rcParams['figure.facecolor'] = NVIDIA_BLACK
plt.rcParams['axes.facecolor'] = NVIDIA_DARK_GREY
plt.rcParams['axes.edgecolor'] = NVIDIA_GREEN
plt.rcParams['axes.labelcolor'] = NVIDIA_LIGHT_GREY
plt.rcParams['xtick.color'] = NVIDIA_LIGHT_GREY
plt.rcParams['ytick.color'] = NVIDIA_LIGHT_GREY
plt.rcParams['text.color'] = NVIDIA_LIGHT_GREY
plt.rcParams['grid.color'] = '#333333'

class QECSimulator:
    def __init__(self,
                 syndrome_time_us=1.0,
                 min_batch_size=10,
                 decode_func=lambda x: x, 
                 max_batches_to_run=50,
                 n_processors=1):
        
        self.syndrome_time = syndrome_time_us
        self.min_batch_size = min_batch_size
        self.decode_func = decode_func
        self.max_batches = max_batches_to_run
        self.n_processors = n_processors
        self.safety_time_limit_us = 100000 

        self.time_points = []
        self.backlog_history = [] 
        self.completed_history = []
        self.batch_durations = [] 

        self.timed_out = False
        self.final_queue_at_timeout = 0
        self.final_completed_at_timeout = 0

    def calculate_decode_time(self, batch_size):
        if self.n_processors == 1:
            return self.decode_func(batch_size)
        else:
            chunk_size = math.ceil(batch_size / self.n_processors)
            base_time = self.decode_func(chunk_size)
            return base_time * 2.0

    def run(self):
        t = 0.0
        dt = 0.5 
        backlog = 0
        batches_completed = 0
        current_decoding_batch = 0 
        decoder_busy_until = 0.0
        next_syndrome_arrival = self.syndrome_time

        self.time_points = []
        self.backlog_history = []
        self.completed_history = []
        self.batch_durations = []
        self.timed_out = False

        while batches_completed < self.max_batches and t < self.safety_time_limit_us:
            # 1. Syndrome Generation
            while t >= next_syndrome_arrival:
                backlog += 1
                next_syndrome_arrival += self.syndrome_time

            # 2. Check Decoder Status
            if t >= decoder_busy_until:
                if current_decoding_batch > 0:
                    batches_completed += 1
                    current_decoding_batch = 0
                
                if batches_completed < self.max_batches:
                    if backlog >= self.min_batch_size:
                        batch_size = backlog
                        backlog = 0
                        duration = self.calculate_decode_time(batch_size)
                        
                        decoder_busy_until = t + duration
                        current_decoding_batch = batch_size
                        
                        # Only plot if it finishes before timeout
                        if (t + duration) <= self.safety_time_limit_us:
                            self.batch_durations.append((t, duration))

            # 3. Record State
            self.time_points.append(t)
            self.backlog_history.append(backlog + current_decoding_batch)
            self.completed_history.append(batches_completed)
            t += dt

        if t >= self.safety_time_limit_us:
            self.timed_out = True
            self.final_queue_at_timeout = backlog + current_decoding_batch
            self.final_completed_at_timeout = batches_completed

    def plot_results(self, title):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)

        # Plot 1: Backlog
        ax1.plot(self.time_points, self.backlog_history, color='white', linewidth=2, label='Total Sys Load')
        ax1.fill_between(self.time_points, self.backlog_history, color='white', alpha=0.1)
        ax1.set_ylabel('Syndrome Count')
        ax1.set_title(title, color=NVIDIA_GREEN, fontsize=14, weight='bold')
        ax1.grid(True, linestyle='--', alpha=0.3)
        ax1.legend(facecolor=NVIDIA_DARK_GREY, edgecolor=NVIDIA_GREEN)

        if self.timed_out:
            info_text = (
                f"⚠️ SIMULATION TIMEOUT ({self.safety_time_limit_us} µs)\n"
                f"--------------------------------\n"
                f"Total System Load: {self.final_queue_at_timeout}\n"
                f"Completed Rounds:  {self.final_completed_at_timeout}"
            )
            ax1.text(0.5, 0.5, info_text, transform=ax1.transAxes, fontsize=12, fontweight='bold',
                     color=NVIDIA_ALERT, ha='center', va='center',
                     bbox=dict(boxstyle="round,pad=0.5", facecolor=NVIDIA_BLACK, edgecolor=NVIDIA_ALERT, alpha=0.9))

        # Plot 2: Duration Bars with ROTATED Values
        if self.batch_durations:
            times, durations = zip(*self.batch_durations)
            total_sim_time = self.time_points[-1] if self.time_points else 1.0
            visual_width = total_sim_time / 50.0 
            
            bars = ax2.bar(times, durations, width=visual_width, color=NVIDIA_GREEN, 
                           align='edge', label='Batch Decode Time', edgecolor=NVIDIA_BLACK, linewidth=0.5)
            
            y_max = max(durations) if durations else 1
            y_offset = y_max * 0.02

            for bar, duration in zip(bars, durations):
                ax2.text(
                    bar.get_x() + bar.get_width() / 2, 
                    bar.get_height() + y_offset,       
                    f'{duration:.0f}',                 
                    ha='center',                       
                    va='bottom',                       # Anchor at bottom of text
                    rotation=90,                       # <--- FIXED: Rotate text vertical
                    fontsize=8,                        # Slightly smaller font
                    color='white',
                    fontweight='bold'
                )
        
        # FIXED: Use raw strings (r'...') to avoid warnings
        ax2.set_ylabel(r'Decode Time ($\mu s$)')
        ax2.set_xlabel(r'Wall Clock Time ($\mu s$)')
        ax2.grid(True, linestyle='--', alpha=0.3)
        ax2.legend(facecolor=NVIDIA_DARK_GREY, edgecolor=NVIDIA_GREEN)
        
        plt.tight_layout()
        plt.show()