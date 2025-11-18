"""
Bandwidth Chart Widget - Real-time bandwidth visualization for OctopusFTP
"""

import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from typing import List, Tuple
import time


class BandwidthChart(ctk.CTkFrame):
    """Real-time bandwidth chart widget using matplotlib"""

    def __init__(self, master, **kwargs):
        """
        Initialize bandwidth chart

        Args:
            master: Parent widget
            **kwargs: Additional arguments for CTkFrame
        """
        super().__init__(master, **kwargs)

        # Chart configuration
        self.chart_width = kwargs.get('width', 300)
        self.chart_height = kwargs.get('height', 120)

        # Create matplotlib figure with dark theme
        plt.style.use('dark_background')
        self.figure = Figure(figsize=(self.chart_width / 100, self.chart_height / 100), dpi=100)
        self.figure.patch.set_facecolor('#2B2B2B')

        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#1E1E1E')

        # Configure axes
        self.ax.set_xlabel('Time (seconds ago)', fontsize=8, color='#CCCCCC')
        self.ax.set_ylabel('Speed (MB/s)', fontsize=8, color='#CCCCCC')
        self.ax.grid(True, alpha=0.2, linestyle='--', linewidth=0.5)
        self.ax.tick_params(labelsize=7, colors='#CCCCCC')

        # Tight layout to maximize chart area
        self.figure.tight_layout(pad=0.5)

        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Initialize line plot
        self.line, = self.ax.plot([], [], color='#4CAF50', linewidth=2, marker='o',
                                  markersize=2, markerfacecolor='#4CAF50')

        # Stats text
        self.stats_text = self.ax.text(0.02, 0.98, '', transform=self.ax.transAxes,
                                       fontsize=7, verticalalignment='top',
                                       bbox=dict(boxstyle='round', facecolor='#2B2B2B',
                                               alpha=0.8, edgecolor='#4CAF50'),
                                       color='#4CAF50')

    def update(self, speed_history: List[Tuple[float, float]]):
        """
        Update chart with new speed history

        Args:
            speed_history: List of (timestamp, speed_mbps) tuples
        """
        if not speed_history:
            # No data - show empty chart
            self.line.set_data([], [])
            self.stats_text.set_text('No data yet')
            self.ax.set_xlim(0, 60)
            self.ax.set_ylim(0, 1)
            self.canvas.draw_idle()
            return

        # Convert timestamps to seconds ago
        current_time = time.time()
        times_ago = [current_time - t for t, s in speed_history]
        speeds = [s for t, s in speed_history]

        # Reverse so most recent is on the right
        times_ago.reverse()
        speeds.reverse()

        # Convert to positive seconds ago (0 = now, 60 = 60 seconds ago)
        times_display = times_ago

        # Update line data
        self.line.set_data(times_display, speeds)

        # Auto-scale axes
        if times_display:
            max_time = max(times_display) if times_display else 60
            self.ax.set_xlim(max(max_time, 60), 0)  # Reverse X axis (newer on right)

        if speeds:
            max_speed = max(speeds) if speeds else 1
            min_speed = min(speeds) if speeds else 0
            # Add 10% padding
            padding = (max_speed - min_speed) * 0.1 if max_speed > 0 else 0.5
            self.ax.set_ylim(max(0, min_speed - padding), max_speed + padding)
        else:
            self.ax.set_ylim(0, 1)

        # Calculate and display stats
        if speeds:
            current_speed = speeds[-1]
            avg_speed = sum(speeds) / len(speeds)
            max_speed_val = max(speeds)
            min_speed_val = min(speeds)

            stats_text = (
                f"Now: {current_speed:.2f} MB/s\n"
                f"Avg: {avg_speed:.2f} MB/s\n"
                f"Max: {max_speed_val:.2f} MB/s"
            )
            self.stats_text.set_text(stats_text)

        # Redraw canvas
        self.canvas.draw_idle()

    def clear(self):
        """Clear the chart"""
        self.line.set_data([], [])
        self.stats_text.set_text('')
        self.canvas.draw_idle()


class CompactBandwidthChart(ctk.CTkFrame):
    """Compact bandwidth chart for embedding in download cards"""

    def __init__(self, master, width=280, height=100, **kwargs):
        """
        Initialize compact bandwidth chart

        Args:
            master: Parent widget
            width: Chart width in pixels
            height: Chart height in pixels
            **kwargs: Additional arguments for CTkFrame
        """
        super().__init__(master, **kwargs)

        # Create matplotlib figure with dark theme
        plt.style.use('dark_background')
        self.figure = Figure(figsize=(width / 100, height / 100), dpi=100)
        self.figure.patch.set_facecolor('transparent')

        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#1E1E1E')

        # Minimal axes configuration
        self.ax.set_xlabel('', fontsize=6)
        self.ax.set_ylabel('MB/s', fontsize=6, color='#888888')
        self.ax.grid(True, alpha=0.15, linestyle=':', linewidth=0.5)
        self.ax.tick_params(labelsize=6, colors='#888888')
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['bottom'].set_color('#444444')
        self.ax.spines['left'].set_color('#444444')

        # Remove x-axis labels for compact view
        self.ax.set_xticks([])

        # Tight layout
        self.figure.subplots_adjust(left=0.12, right=0.98, top=0.95, bottom=0.05)

        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Initialize area plot (filled)
        self.line, = self.ax.plot([], [], color='#4CAF50', linewidth=1.5)
        self.fill = None

    def update(self, speed_history: List[Tuple[float, float]]):
        """
        Update chart with new speed history

        Args:
            speed_history: List of (timestamp, speed_mbps) tuples
        """
        if not speed_history:
            # No data
            self.line.set_data([], [])
            if self.fill:
                self.fill.remove()
                self.fill = None
            self.ax.set_xlim(0, 60)
            self.ax.set_ylim(0, 1)
            self.canvas.draw_idle()
            return

        # Convert timestamps to seconds ago
        current_time = time.time()
        times_ago = [current_time - t for t, s in speed_history]
        speeds = [s for t, s in speed_history]

        # Keep only last 60 seconds for compact view
        if times_ago:
            max_time_ago = max(times_ago)
            if max_time_ago > 60:
                # Filter to last 60 seconds
                filtered_data = [(t, s) for (t, s) in zip(times_ago, speeds) if t <= 60]
                if filtered_data:
                    times_ago, speeds = zip(*filtered_data)
                    times_ago = list(times_ago)
                    speeds = list(speeds)

        # Reverse so most recent is on the right
        times_ago.reverse()
        speeds.reverse()

        # Update line data
        self.line.set_data(times_ago, speeds)

        # Remove old fill and create new one
        if self.fill:
            self.fill.remove()

        if times_ago and speeds:
            self.fill = self.ax.fill_between(times_ago, 0, speeds,
                                            alpha=0.3, color='#4CAF50')

        # Auto-scale axes
        if times_ago:
            self.ax.set_xlim(min(60, max(times_ago)), 0)  # Reverse X axis

        if speeds:
            max_speed = max(speeds)
            # Add 10% padding to top
            self.ax.set_ylim(0, max_speed * 1.1 if max_speed > 0 else 1)
        else:
            self.ax.set_ylim(0, 1)

        # Redraw canvas
        self.canvas.draw_idle()

    def clear(self):
        """Clear the chart"""
        self.line.set_data([], [])
        if self.fill:
            self.fill.remove()
            self.fill = None
        self.canvas.draw_idle()
