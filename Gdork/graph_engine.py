"""
Graph Visualization Engine for Project-GDork
Embeds matplotlib charts inside Tkinter frames.
"""
import tkinter as tk
from tkinter import ttk
import threading

try:
    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    import matplotlib.animation as animation
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class GraphEngine:
    """Generates embedded matplotlib charts inside a Tkinter parent frame."""

    DARK_BG = '#1e1e1e'
    DARK_FG = '#ffffff'
    ACCENT = '#4285f4'
    SUCCESS = '#34a853'
    WARNING = '#fbbc05'
    DANGER = '#ea4335'
    COLORS = ['#4285f4', '#34a853', '#fbbc05', '#ea4335', '#a142f4', '#00bcd4', '#ff7043', '#66bb6a']

    @staticmethod
    def check_available():
        return MATPLOTLIB_AVAILABLE

    @staticmethod
    def apply_dark_style(ax, fig):
        fig.patch.set_facecolor(GraphEngine.DARK_BG)
        ax.set_facecolor('#2d2d2d')
        ax.tick_params(colors=GraphEngine.DARK_FG)
        ax.xaxis.label.set_color(GraphEngine.DARK_FG)
        ax.yaxis.label.set_color(GraphEngine.DARK_FG)
        ax.title.set_color(GraphEngine.DARK_FG)
        for spine in ax.spines.values():
            spine.set_edgecolor('#444444')

    @classmethod
    def embed_chart(cls, parent_frame, fig):
        """Embed a matplotlib figure into a tkinter frame."""
        for widget in parent_frame.winfo_children():
            widget.destroy()
        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        return canvas

    @classmethod
    def dork_performance_chart(cls, parent_frame, brain_knowledge):
        """Bar chart of top dork pattern weights from DorkBrain."""
        if not MATPLOTLIB_AVAILABLE:
            tk.Label(parent_frame, text="matplotlib not installed", fg='red').pack()
            return

        weights = brain_knowledge.get('pattern_weights', {})
        if not weights:
            tk.Label(parent_frame, text="No brain data yet. Generate and mark dorks as useful first.", 
                    fg='white', bg='#1e1e1e').pack(pady=20)
            return

        # Sort and take top 15
        sorted_w = sorted(weights.items(), key=lambda x: x[1], reverse=True)[:15]
        labels = [k[:30] + '...' if len(k) > 30 else k for k, v in sorted_w]
        values = [v for k, v in sorted_w]

        fig = Figure(figsize=(10, 5), dpi=90)
        ax = fig.add_subplot(111)
        bars = ax.barh(labels, values, color=cls.COLORS[:len(labels)])
        ax.set_xlabel('Brain Weight Score')
        ax.set_title('🧠 Top Dork Patterns by Brain Weight')
        ax.invert_yaxis()
        cls.apply_dark_style(ax, fig)
        fig.tight_layout()
        cls.embed_chart(parent_frame, fig)

    @classmethod
    def validation_pie_chart(cls, parent_frame, hits=0, misses=0, captchas=0):
        """Pie chart of validation results."""
        if not MATPLOTLIB_AVAILABLE:
            return
        if hits + misses + captchas == 0:
            tk.Label(parent_frame, text="No validation data yet.", 
                    fg='white', bg='#1e1e1e').pack(pady=20)
            return

        fig = Figure(figsize=(5, 4), dpi=90)
        ax = fig.add_subplot(111)
        sizes = [hits, misses, captchas]
        labels = [f'Hits ({hits})', f'Misses ({misses})', f'CAPTCHAs ({captchas})']
        colors = [cls.SUCCESS, cls.DANGER, cls.WARNING]
        non_zero = [(s, l, c) for s, l, c in zip(sizes, labels, colors) if s > 0]
        if not non_zero:
            return
        s, l, c = zip(*non_zero)
        ax.pie(s, labels=l, colors=c, autopct='%1.1f%%', startangle=140,
               textprops={'color': cls.DARK_FG})
        ax.set_title('📊 Live Validation Results')
        cls.apply_dark_style(ax, fig)
        fig.tight_layout()
        cls.embed_chart(parent_frame, fig)

    @classmethod
    def geoint_map_chart(cls, parent_frame, geo_results):
        """Scatter plot of IP geolocations on a basic lat/lon chart."""
        if not MATPLOTLIB_AVAILABLE:
            return
        valid = [r for r in geo_results if r.get('lat') and r.get('lon')]
        if not valid:
            tk.Label(parent_frame, text="No GEOINT data yet.", 
                    fg='white', bg='#1e1e1e').pack(pady=20)
            return

        fig = Figure(figsize=(10, 5), dpi=90)
        ax = fig.add_subplot(111)
        lats = [r['lat'] for r in valid]
        lons = [r['lon'] for r in valid]
        labels = [f"{r['ip']}\n{r.get('city','')}" for r in valid]

        ax.scatter(lons, lats, c=cls.ACCENT, s=100, zorder=5, alpha=0.9)
        for i, label in enumerate(labels):
            ax.annotate(label, (lons[i], lats[i]), fontsize=7, color=cls.DARK_FG,
                       xytext=(5, 5), textcoords='offset points')
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.set_title('🌍 IP Geolocation Map (Lat/Lon)')
        ax.set_xlim(-180, 180)
        ax.set_ylim(-90, 90)
        cls.apply_dark_style(ax, fig)
        fig.tight_layout()
        cls.embed_chart(parent_frame, fig)

    @classmethod
    def entity_network_graph(cls, parent_frame, emails=None, ips=None, socials=None):
        """Network-style node graph of discovered entities."""
        if not MATPLOTLIB_AVAILABLE:
            return
        emails = emails or []
        ips = ips or []
        socials = socials or []

        all_nodes = (
            [('email', e) for e in emails[:8]] + 
            [('ip', ip) for ip in ips[:8]] + 
            [('social', s) for s in socials[:8]]
        )

        if not all_nodes:
            tk.Label(parent_frame, text="No entity data yet. Run Entity Profiler first.", 
                    fg='white', bg='#1e1e1e').pack(pady=20)
            return

        import math
        fig = Figure(figsize=(10, 6), dpi=90)
        ax = fig.add_subplot(111)

        # Place nodes in a circle
        n = len(all_nodes)
        node_colors = {'email': cls.SUCCESS, 'ip': cls.ACCENT, 'social': cls.WARNING}
        for i, (ntype, nlabel) in enumerate(all_nodes):
            angle = 2 * math.pi * i / n
            x, y = math.cos(angle) * 3, math.sin(angle) * 3
            color = node_colors.get(ntype, cls.ACCENT)
            ax.scatter(x, y, s=400, c=color, zorder=5)
            ax.annotate(nlabel[:20], (x, y), fontsize=7, color=cls.DARK_FG,
                       ha='center', va='bottom', xytext=(0, 10), textcoords='offset points')
            # Draw line to center
            ax.plot([0, x], [0, y], color='#444444', linewidth=0.8, zorder=1)

        # Center node (target)
        ax.scatter(0, 0, s=600, c='#ff6b6b', zorder=6, marker='*')
        ax.annotate('TARGET', (0, 0), fontsize=9, color='#ff6b6b', ha='center',
                   xytext=(0, -15), textcoords='offset points', fontweight='bold')

        # Legend
        patches = [
            mpatches.Patch(color=cls.SUCCESS, label='Emails'),
            mpatches.Patch(color=cls.ACCENT, label='IPs'),
            mpatches.Patch(color=cls.WARNING, label='Socials'),
        ]
        ax.legend(handles=patches, facecolor='#2d2d2d', labelcolor=cls.DARK_FG, loc='upper right')
        ax.set_xlim(-5, 5)
        ax.set_ylim(-5, 5)
        ax.set_title('🕸️ Entity Relationship Network')
        ax.axis('off')
        cls.apply_dark_style(ax, fig)
        fig.tight_layout()
        cls.embed_chart(parent_frame, fig)
