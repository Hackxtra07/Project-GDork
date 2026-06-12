import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import webbrowser
import json
import re
import pyperclip
from datetime import datetime
import threading
from urllib.parse import quote_plus
from tkinter import filedialog
import subprocess
import os
from PIL import Image, ImageTk
from dork_brain import DorkBrain
from extensions import ReportGenerator, GHDBUpdater, LiveValidator
from scraper_engine import EntityProfiler
from api_engine import ConfigManager, ShodanEngine, VirusTotalEngine
from advanced_modules import TORRouter, CaptchaSolver, NucleiScanner, SOCMINTEngine, GEOINTEngine
from graph_engine import GraphEngine
from person_engine import (
    PersonInvestigator, HIBPEngine, HoleheEngine, SherlockEngine,
    DehashedEngine, LeakCheckEngine, PimEyesEngine, FaceCheckEngine,
    VirusTotalExpanded
)
class ScrollableFrame(tk.Frame):
    """A reusable scrollable frame container using Canvas and Scrollbar"""
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        bg_color = '#1e1e1e'
        if hasattr(container, 'cget'):
            try:
                bg_color = container.cget('bg')
            except tk.TclError:
                try:
                    bg_color = container.cget('background')
                except tk.TclError:
                    pass
        
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, bg=bg_color)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=bg_color)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel only when mouse enters the canvas
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _bind_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        try:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except tk.TclError:
            pass

class AdvancedDorkGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("🔍 Advanced Google Dork Generator Pro")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1e1e1e')
        
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Color scheme
        self.colors = {
            'bg': '#1e1e1e',
            'fg': '#ffffff',
            'accent': '#4285f4',
            'secondary': '#34a853',
            'warning': '#ea4335',
            'highlight': '#fbbc05'
        }
        
        self.dork_patterns = self.load_dork_patterns()
        self.search_history = []
        self.favorite_dorks = []
        self.brain = DorkBrain()
        self.config_manager = ConfigManager()
        self.captcha_solver = CaptchaSolver()
        self.geoint = GEOINTEngine()
        self.geo_results = []
        self.socmint_hits = {'emails': [], 'ips': [], 'socials': []}
        self.validation_stats = {'hits': 0, 'misses': 0, 'captchas': 0}
        
        self.setup_ui()
        
    def load_dork_patterns(self):
        """Load expanded dork patterns"""
        patterns = {
            "file_type": {
                "PDF": "filetype:pdf",
                "Excel": "filetype:xls OR filetype:xlsx",
                "Word": "filetype:doc OR filetype:docx",
                "PowerPoint": "filetype:ppt OR filetype:pptx",
                "Text": "filetype:txt",
                "SQL": "filetype:sql",
                "Log": "filetype:log",
                "Config": "filetype:conf OR filetype:ini OR filetype:env",
                "Backup": "filetype:bak OR filetype:backup",
                "XML": "filetype:xml",
                "JSON": "filetype:json",
                "YAML": "filetype:yaml OR filetype:yml",
                "CSV": "filetype:csv"
            },
            "site_specific": {
                "Subdomain": "site:*.example.com",
                "Directory": "site:example.com inurl:admin",
                "Login Pages": "inurl:login OR inurl:signin",
                "Admin Panels": "intitle:\"admin\" OR \"admin login\"",
                "Dashboards": "intitle:\"dashboard\" -inurl:github",
                "GitHub": "site:github.com inurl:/",
                "GitLab": "site:gitlab.com inurl:/",
                "Bitbucket": "site:bitbucket.org inurl:/"
            },
            "content_type": {
                "API Keys": "\"api_key\" OR \"api key\"",
                "Passwords": "intext:password | inurl:passwd | filetype:env",
                "Tokens": "intext:token | inurl:token",
                "Emails": "intext:@gmail.com | intext:@yahoo.com | intext:@outlook.com",
                "Sensitive": "confidential | secret | private | restricted"
            },
            "vulnerability": {
                "SQL Injection": "inurl:\"id=\" | inurl:\"catid=\" | inurl:\"pageid=\"",
                "XSS": "inurl:\"q=\" | inurl:\"search=\" | inurl:\"query=\"",
                "Open Redirect": "inurl:\"redirect=\" | inurl:\"return=\" | inurl:\"url=\"",
                "LFI": "inurl:\"include=\" | inurl:\"page=\" | inurl:\"file=\"",
                "Debug Info": "\"phpinfo()\" | \"var_dump\" | \"print_r\""
            },
            "iot": {
                "Cameras": "intitle:\"webcam\" | \"camera\" inurl:view.shtml",
                "Routers": "intitle:\"router\" | \"gateway\" inurl:status",
                "Printers": "inurl:\"printer\" | \"prt\" intitle:status",
                "IoT Devices": "\"server: IoT\" | \"IoT device\" intext:configuration"
            },
            "operators": {
                "Cache": "cache:",
                "InURL": "inurl:",
                "InTitle": "intitle:",
                "InText": "intext:",
                "Ext": "ext:"
            },
            "intents": {
                "Vulnerability": "inurl:\"id=\" | intext:\"error\" | intitle:\"index of\"",
                "File Discovery": "intitle:\"index of\" | intext:\"parent directory\"",
                "Credentials": "intext:\"password\" | intext:\"username\" | intext:\"login\"",
                "Admin": "intitle:\"admin\" | inurl:\"admin\" | inurl:\"dashboard\"",
                "Database": "filetype:sql | filetype:db | filetype:sqlite | filetype:accdb"
            }
        }
        return patterns

    def generate_all_combinations(self, user_keywords, selected_patterns, max_limit=10000, safe_filter=True):
        """Generate a massive variety of dorks by mixing user inputs with ALL internal patterns.
        Focuses on high-precision variations by applying operators to user keywords.
        """
        import itertools
        combos = []
        
        # 1. Gather User Inputs
        target_list = selected_patterns.get('target', [])
        file_dorks = selected_patterns.get('filetypes', [])
        manual_patterns = selected_patterns.get('patterns', [])
        intent = selected_patterns.get('intent', "Information Gathering")
        
        # 2. Extract and Categorize Patterns
        pattern_data = self.load_dork_patterns()
        all_internal_patterns = []
        for cat_patterns in pattern_data.values():
            all_internal_patterns.extend(list(cat_patterns.values()))

        # 3. Precision Engineering: User Input Variations
        # For every keyword, create specific dork variants
        kw_variants = []
        for k in (user_keywords if user_keywords else []):
            kw_variants.extend([
                f'"{k}"',           # Exact match
                f'intitle:"{k}"',   # In title
                f'inurl:"{k}"',     # In URL
                f'intext:"{k}"',    # In text
                f'filetype:{k}' if len(k) < 5 else f'ext:{k}'
            ])
        
        # 4. Multi-Stage Specific Mixing (The High Output Engine)
        
        # A. Target + Specific Keyword Variants (High Precision)
        if target_list and kw_variants:
            for t in target_list:
                for kv in kw_variants:
                    combos.append(f"{t} {kv}")

        # B. Target + All Patterns (Discovery)
        if target_list:
            for t in target_list:
                for p in all_internal_patterns:
                    combos.append(f"{t} {p}")

        # C. Keyword Variants + All Patterns (The Multiplier)
        if kw_variants:
            for kv in kw_variants:
                # Pair each specific user keyword variant with every internal hack/leak pattern
                for p in all_internal_patterns:
                    combos.append(f"{kv} {p}")

        # D. Triple Mix: Target + Keyword Variant + Pattern (Deep Scan)
        if target_list and kw_variants:
            # We sample internal patterns to avoid astronomical lists while keeping it high-output
            for t in target_list:
                for kv in kw_variants:
                    # Specific mix for sensitive files or vulnerabilities
                    relevant_cats = ["vulnerability", "content_type", "intents"]
                    for cat in relevant_cats:
                        for p in pattern_data[cat].values():
                            combos.append(f"{t} {kv} {p}")

        # E. Filetype Expansion
        if file_dorks:
            stage_1_combos = list(combos)
            for f in file_dorks:
                # Apply filetypes to both simple and complex variations
                for bc in stage_1_combos[:1000]: # Spread across many base variations
                    combos.append(f"{bc} {f}")

        # 5. Manual Selections
        if manual_patterns:
            for mp in manual_patterns:
                for t in (target_list if target_list else [""]):
                    for kv in (kw_variants if kw_variants else [""]):
                        dork = f"{t} {kv} {mp}".replace("  ", " ").strip()
                        if dork: combos.append(dork)

        # 6. Cleanup & Final Polish
        # Remove duplicates while preserving some order, then shuffle for better UX
        seen = set()
        unique_combos = []
        for c in combos:
            if c not in seen:
                unique_combos.append(c)
                seen.add(c)
        
        import random
        random.shuffle(unique_combos)
        
        # Safety filter
        sensitive_tokens = ['password', 'passwd', 'secret', 'apikey', 'api_key', 'token']
        if safe_filter:
            unique_combos = [d for d in unique_combos if not any(tok in d.lower() for tok in sensitive_tokens)]

        return unique_combos[:max_limit]

    def show_combinations_window(self, combos):
        """Show a new window with all generated dork combinations and export/copy options"""
        win = tk.Toplevel(self.root)
        win.title("All Dork Combinations")
        win.geometry("900x600")
        text = scrolledtext.ScrolledText(win, wrap=tk.WORD, font=("Consolas", 11))
        text.pack(fill='both', expand=True, padx=10, pady=10)
        text.insert(tk.END, '\n'.join(combos))
        # Export and copy buttons
        btn_frame = tk.Frame(win)
        btn_frame.pack(fill='x', pady=5)

        def export_txt():
            filename = f"dork_combos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('\n'.join(combos))
            messagebox.showinfo("Exported", f"Saved to {filename}")

        def export_csv():
            import csv
            filename = f"dork_combos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['dork'])
                for c in combos:
                    writer.writerow([c])
            messagebox.showinfo("Exported", f"Saved to {filename}")

        def copy():
            pyperclip.copy('\n'.join(combos))
            messagebox.showinfo("Copied", "All combinations copied to clipboard!")
        
        def mark_useful():
            try:
                selected_text = text.selection_get()
                self.brain.register_success(selected_text)
                self.update_status("Marked selected dork as useful!")
                if hasattr(self, 'refresh_learning_tab'):
                    self.refresh_learning_tab()
            except:
                messagebox.showwarning("Warning", "Please highlight a dork first.")

        def generate_report():
            target = self.target_entry.get() if hasattr(self, 'target_entry') else "Unknown"
            dorks_with_scores = [(c, self.brain.get_weight(c.split()[0]) if c else 1.0) for c in combos]
            success, msg = ReportGenerator.generate_html_report(target, dorks_with_scores)
            if success:
                messagebox.showinfo("Report Generated", f"Report saved to {msg}")
            else:
                messagebox.showerror("Error", f"Failed to generate report: {msg}")

        tk.Button(btn_frame, text="Export TXT", command=export_txt, bg=self.colors['accent'], fg='white').pack(side='left', padx=8)
        tk.Button(btn_frame, text="Export CSV", command=export_csv, bg=self.colors['accent'], fg='white').pack(side='left', padx=8)
        tk.Button(btn_frame, text="Copy All", command=copy, bg=self.colors['secondary'], fg='white').pack(side='left', padx=8)
        tk.Button(btn_frame, text="Generate HTML Report", command=generate_report, bg=self.colors['secondary'], fg='white').pack(side='left', padx=8)
        tk.Button(btn_frame, text="👍 Mark Selected Useful", command=mark_useful, bg=self.colors['highlight'], fg='black').pack(side='left', padx=8)
        tk.Button(btn_frame, text="Close", command=win.destroy, bg=self.colors['warning'], fg='white').pack(side='right', padx=10)

    def generate_and_show_combinations(self):
        """Collect user input and selected patterns, generate all dork combos, and show them"""
        user_keywords = []
        if hasattr(self, 'keywords_entry'):
            kw = self.keywords_entry.get().strip()
            if kw:
                user_keywords = [k.strip() for k in re.split(r'[ ,;]+', kw) if k.strip()]

        # Collect selected patterns from the selected-patterns listbox
        selected_patterns_list = []
        if hasattr(self, 'selected_patterns_listbox'):
            selected_patterns_list = [s for s in self.selected_patterns_listbox.get(0, tk.END)]

        # Collect selected file types
        selected_files = [ft for ft, var in self.file_vars.items() if var.get()]
        file_type_map = {
            'PDF': 'filetype:pdf',
            'DOC/DOCX': 'filetype:doc OR filetype:docx',
            'XLS/XLSX': 'filetype:xls OR filetype:xlsx',
            'TXT': 'filetype:txt',
            'SQL': 'filetype:sql',
            'LOG': 'filetype:log',
            'JSON': 'filetype:json',
            'XML': 'filetype:xml'
        }
        file_dorks = [file_type_map[f] for f in selected_files if f in file_type_map]

        # Target
        target = self.target_entry.get().strip() if hasattr(self, 'target_entry') else ''
        target_list = []
        if target:
            if not target.startswith('http') and not target.startswith('site:'):
                target_list = [f'site:{target}']
            else:
                target_list = [target]

        # Intent
        selected_intent = self.intent_combo.get() if hasattr(self, 'intent_combo') else "Information Gathering"

        # Build selected_patterns dict (values are lists)
        selected_patterns = {
            'patterns': selected_patterns_list,
            'filetypes': file_dorks,
            'target': target_list,
            'intent': selected_intent
        }

        max_limit = getattr(self, 'max_combos_var', tk.IntVar(value=2000)).get()
        safe_filter = getattr(self, 'safe_filter_var', tk.BooleanVar(value=True)).get()

        combos = self.generate_all_combinations(user_keywords, selected_patterns, max_limit=max_limit, safe_filter=safe_filter)
        if not combos:
            messagebox.showinfo("No combos", "No combinations were generated (try lowering filters or increasing max limit).")
            return
        self.show_combinations_window(combos)

    def save_template(self, name=None):
        """Save current input as a template"""
        tmpl = {
            'target': self.target_entry.get().strip() if hasattr(self, 'target_entry') else '',
            'keywords': self.keywords_entry.get().strip() if hasattr(self, 'keywords_entry') else '',
            'time_range': self.time_var.get() if hasattr(self, 'time_var') else 'anytime'
        }
        if not name:
            name = f"template_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            with open(f"{name}.json", 'w', encoding='utf-8') as f:
                json.dump(tmpl, f)
            self.update_status(f"Template saved: {name}.json")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save template: {e}")

    def load_template(self):
        """Load a template file (simple implementation — loads first found template)"""
        import glob
        files = glob.glob('template_*.json')
        if not files:
            messagebox.showinfo("No templates", "No templates found (files named template_*.json)")
            return
        try:
            with open(files[0], 'r', encoding='utf-8') as f:
                tmpl = json.load(f)
            if hasattr(self, 'target_entry'):
                self.target_entry.delete(0, tk.END)
                self.target_entry.insert(0, tmpl.get('target', ''))
            if hasattr(self, 'keywords_entry'):
                self.keywords_entry.delete(0, tk.END)
                self.keywords_entry.insert(0, tmpl.get('keywords', ''))
            if hasattr(self, 'time_var'):
                self.time_var.set(tmpl.get('time_range', 'anytime'))
            self.update_status(f"Loaded template: {files[0]}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load template: {e}")

    def setup_ui(self):
        """Setup the main GUI interface with a grouped, minimal layout"""
        # Create main notebook for the 6 primary tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 1. Dorking Studio Tab
        dorking_frame = ttk.Frame(self.notebook)
        self.notebook.add(dorking_frame, text="🔍 Dorking Studio")
        self.dork_notebook = ttk.Notebook(dorking_frame)
        self.dork_notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 2. OSINT Hub Tab
        osint_frame = ttk.Frame(self.notebook)
        self.notebook.add(osint_frame, text="🕵️ OSINT Hub")
        self.osint_notebook = ttk.Notebook(osint_frame)
        self.osint_notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 3. Scan & API Tab
        scan_frame = ttk.Frame(self.notebook)
        self.notebook.add(scan_frame, text="🔬 Scan & API")
        self.scan_notebook = ttk.Notebook(scan_frame)
        self.scan_notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 4. Analytics & History Tab
        analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(analytics_frame, text="📊 Analytics & Saved")
        self.analytics_notebook = ttk.Notebook(analytics_frame)
        self.analytics_notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 5. Tools & Guides Tab
        tools_guides_frame = ttk.Frame(self.notebook)
        self.notebook.add(tools_guides_frame, text="🛠️ Tools & Guides")
        self.tools_notebook = ttk.Notebook(tools_guides_frame)
        self.tools_notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 6. Settings Tab
        settings_outer_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_outer_frame, text="⚙️ Settings")
        
        # Initialize sub-tabs in their respective nested notebooks
        self.setup_dork_generator_tab(self.dork_notebook)
        self.setup_advanced_search_tab(self.dork_notebook)
        self.setup_live_validation_tab(self.dork_notebook)
        self.setup_learning_tab(self.dork_notebook)
        
        self.setup_person_hub_tab(self.osint_notebook)
        self.setup_entity_profiler_tab(self.osint_notebook)
        self.setup_socmint_tab(self.osint_notebook)
        self.setup_geoint_tab(self.osint_notebook)
        
        self.setup_api_intelligence_tab(self.scan_notebook)
        self.setup_nuclei_tab(self.scan_notebook)
        
        self.setup_history_tab(self.analytics_notebook)
        self.setup_graphs_tab(self.analytics_notebook)
        
        self.setup_tools_suite_tab(self.tools_notebook)
        self.setup_people_finder_guides_tab(self.tools_notebook)
        
        self.setup_settings_tab(settings_outer_frame)
        
        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready", bg=self.colors['accent'], 
                                 fg='white', anchor='w', relief='sunken')
        self.status_bar.pack(side='bottom', fill='x')
    
    def setup_dork_generator_tab(self, notebook=None):
        """Setup the main dork generation tab"""
        parent = notebook if notebook is not None else self.notebook
        tab = ttk.Frame(parent)
        parent.add(tab, text="🧠 Dork Generator")
        
        # Main container with two columns
        main_container = tk.Frame(tab, bg=self.colors['bg'])
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Left panel - Input parameters
        left_panel = tk.Frame(main_container, bg=self.colors['bg'])
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Right panel - Output and preview
        right_panel = tk.Frame(main_container, bg=self.colors['bg'])
        right_panel.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Left panel content
        self.create_input_section(left_panel)
        
        # Right panel content
        self.create_output_section(right_panel)
        
    def create_input_section(self, parent):
        """Create input controls section"""
        tk.Label(parent, text="🔍 Target Information", bg=self.colors['bg'], 
                fg=self.colors['accent'], font=('Arial', 14, 'bold')).pack(anchor='w', pady=(0, 10))
        
        # Domain/URL
        tk.Label(parent, text="Target Domain/URL:", bg=self.colors['bg'], fg='white').pack(anchor='w')
        self.target_entry = tk.Entry(parent, bg='#2d2d2d', fg='white', insertbackground='white')
        self.target_entry.pack(fill='x', pady=(0, 10))
        
        # Keywords
        tk.Label(parent, text="Keywords (separate with commas):", bg=self.colors['bg'], fg='white').pack(anchor='w')
        self.keywords_entry = tk.Entry(parent, bg='#2d2d2d', fg='white', insertbackground='white')
        self.keywords_entry.pack(fill='x', pady=(0, 10))
        
        # Search Intent
        tk.Label(parent, text="Search Intent:", bg=self.colors['bg'], fg='white').pack(anchor='w')
        self.intent_combo = ttk.Combobox(parent, values=[
            "Information Gathering",
            "Vulnerability Discovery", 
            "File Discovery",
            "Credentials Discovery",
            "IoT Device Discovery",
            "API Discovery",
            "Config Files",
            "Backup Files",
            "Login Portals",
            "Admin Panels"
        ], state='readonly')
        self.intent_combo.pack(fill='x', pady=(0, 10))
        self.intent_combo.set("Information Gathering")
        
        # File Types
        tk.Label(parent, text="File Types:", bg=self.colors['bg'], fg='white').pack(anchor='w')
        file_frame = tk.Frame(parent, bg=self.colors['bg'])
        file_frame.pack(fill='x', pady=(0, 10))
        
        self.file_vars = {}
        file_types = ['PDF', 'DOC/DOCX', 'XLS/XLSX', 'TXT', 'SQL', 'LOG', 'JSON', 'XML']
        for i, ftype in enumerate(file_types):
            var = tk.BooleanVar()
            self.file_vars[ftype] = var
            cb = tk.Checkbutton(file_frame, text=ftype, variable=var, 
                              bg=self.colors['bg'], fg='white', selectcolor='#2d2d2d')
            cb.grid(row=i//4, column=i%4, sticky='w', padx=(0, 10))
        
        # Time Range
        tk.Label(parent, text="Time Range:", bg=self.colors['bg'], fg='white').pack(anchor='w')
        time_frame = tk.Frame(parent, bg=self.colors['bg'])
        time_frame.pack(fill='x', pady=(0, 10))
        
        self.time_var = tk.StringVar(value="anytime")
        times = [("Any time", "anytime"),
                ("Past 24 hours", "day"),
                ("Past week", "week"),
                ("Past month", "month"),
                ("Past year", "year")]
        
        for i, (text, value) in enumerate(times):
            rb = tk.Radiobutton(time_frame, text=text, variable=self.time_var, 
                              value=value, bg=self.colors['bg'], fg='white',
                              selectcolor='#2d2d2d')
            rb.grid(row=0, column=i, padx=(0, 10))
        
        # Advanced controls: max combos and safe-filter
        controls_frame = tk.Frame(parent, bg=self.colors['bg'])
        controls_frame.pack(fill='x', pady=(10, 0))
        tk.Label(controls_frame, text="Max combos:", bg=self.colors['bg'], fg='white').pack(side='left')
        self.max_combos_var = tk.IntVar(value=2000)
        tk.Spinbox(controls_frame, from_=100, to=20000, increment=100, textvariable=self.max_combos_var, width=8).pack(side='left', padx=(6, 12))
        self.safe_filter_var = tk.BooleanVar(value=True)
        tk.Checkbutton(controls_frame, text="Enable safe-filter", variable=self.safe_filter_var, bg=self.colors['bg'], fg='white', selectcolor='#2d2d2d').pack(side='left')
        # Template buttons
        tk.Button(controls_frame, text="Save Template", command=lambda: self.save_template(), bg=self.colors['accent'], fg='white').pack(side='right', padx=(6,0))
        tk.Button(controls_frame, text="Load Template", command=self.load_template, bg=self.colors['secondary'], fg='white').pack(side='right')

        # Generate button
        tk.Button(parent, text="🚀 Generate Advanced Dorks", 
                 command=self.generate_dorks, bg=self.colors['accent'], 
                 fg='white', font=('Arial', 10, 'bold')).pack(fill='x', pady=(12, 0))

        # Advanced: Generate all combos button
        tk.Button(parent, text="✨ Generate All Combos (Advanced)",
              command=self.generate_and_show_combinations, bg=self.colors['highlight'],
              fg='black', font=('Arial', 10, 'bold')).pack(fill='x', pady=(10, 0))
    
    def create_output_section(self, parent):
        """Create output display section"""
        tk.Label(parent, text="Generated Dorks", bg=self.colors['bg'], 
                fg=self.colors['accent'], font=('Arial', 14, 'bold')).pack(anchor='w')
        
        # Dorks display with scroll
        dork_frame = tk.Frame(parent, bg=self.colors['bg'])
        dork_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        self.dorks_text = scrolledtext.ScrolledText(dork_frame, bg='#2d2d2d', 
                                                   fg='white', height=15,
                                                   insertbackground='white')
        self.dorks_text.pack(fill='both', expand=True)
        
        # Action buttons
        btn_frame = tk.Frame(parent, bg=self.colors['bg'])
        btn_frame.pack(fill='x', pady=(10, 0))
        
        buttons = [
            ("📋 Copy All", self.copy_dorks),
            ("🌐 Open in Browser", self.open_in_browser),
            ("💾 Save to File", self.save_dorks),
            ("⭐ Add to Favorites", self.add_to_favorites),
            ("🔄 Test Dorks", self.test_dorks)
        ]
        
        for i, (text, command) in enumerate(buttons):
            btn = tk.Button(btn_frame, text=text, command=command, 
                           bg=self.colors['secondary'], fg='white', width=15)
            btn.grid(row=0, column=i, padx=(0, 10))
        
        # Preview frame
        tk.Label(parent, text="Preview & Statistics", bg=self.colors['bg'], 
                fg=self.colors['accent'], font=('Arial', 12, 'bold')).pack(anchor='w', pady=(20, 10))
        
        preview_frame = tk.Frame(parent, bg='#2d2d2d', relief='sunken', borderwidth=1)
        preview_frame.pack(fill='both', expand=True)
        
        self.preview_text = tk.Text(preview_frame, bg='#2d2d2d', fg='white', 
                                   height=5, wrap='word')
        self.preview_text.pack(fill='both', expand=True, padx=5, pady=5)
        
    def setup_advanced_search_tab(self, notebook=None):
        """Setup advanced search patterns tab"""
        parent = notebook if notebook is not None else self.notebook
        tab = ttk.Frame(parent)
        parent.add(tab, text="⚡ Advanced Patterns")
        
        container = tk.Frame(tab, bg=self.colors['bg'])
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Pattern categories
        categories = list(self.dork_patterns.keys())
        
        # Category selector
        tk.Label(container, text="Select Pattern Category:", bg=self.colors['bg'], 
                fg='white').pack(anchor='w')
        
        self.pattern_cat_combo = ttk.Combobox(container, values=categories, state='readonly')
        self.pattern_cat_combo.pack(fill='x', pady=(0, 10))
        self.pattern_cat_combo.set(categories[0])
        self.pattern_cat_combo.bind('<<ComboboxSelected>>', self.update_pattern_list)
        
        # Patterns listbox
        list_frame = tk.Frame(container, bg=self.colors['bg'])
        list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        self.patterns_listbox = tk.Listbox(list_frame, bg='#2d2d2d', fg='white', 
                          selectbackground=self.colors['accent'], selectmode=tk.MULTIPLE)
        self.patterns_listbox.pack(side='left', fill='both', expand=True)
        
        scrollbar = tk.Scrollbar(list_frame, command=self.patterns_listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.patterns_listbox.config(yscrollcommand=scrollbar.set)
        
        self.update_pattern_list()

        # Custom pattern input and selected-patterns list
        custom_frame = tk.Frame(container, bg=self.colors['bg'])
        custom_frame.pack(fill='x', pady=(10, 0))
        tk.Label(custom_frame, text="Custom pattern:", bg=self.colors['bg'], fg='white').pack(anchor='w')
        self.custom_pattern_entry = tk.Entry(custom_frame, bg='#2d2d2d', fg='white')
        self.custom_pattern_entry.pack(fill='x', pady=(4, 6))
        tk.Button(custom_frame, text="Add Custom Pattern", command=lambda: self.add_custom_pattern(), bg=self.colors['accent'], fg='white').pack(anchor='w')

        tk.Label(container, text="Selected Patterns (will be used for combos):", bg=self.colors['bg'], fg='white').pack(anchor='w', pady=(10,0))
        self.selected_patterns_listbox = tk.Listbox(container, bg='#2d2d2d', fg='white', height=6)
        self.selected_patterns_listbox.pack(fill='x', pady=(4,6))

        # Add to generator button (adds selected items from patterns listbox)
        tk.Button(container, text="➕ Add Selected to Patterns", 
             command=self.add_selected_patterns,
             bg=self.colors['accent'], fg='white').pack(fill='x', pady=(0,10))
             
        tk.Button(container, text="🔄 Update Patterns from GHDB", 
             command=self.update_ghdb,
             bg=self.colors['highlight'], fg='black').pack(fill='x')
    
    def setup_history_tab(self, notebook=None):
        """Setup search history tab"""
        parent = notebook if notebook is not None else self.notebook
        tab = ttk.Frame(parent)
        parent.add(tab, text="📚 History & Favorites")
        
        container = tk.Frame(tab, bg=self.colors['bg'])
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # History section
        tk.Label(container, text="Search History:", bg=self.colors['bg'], 
                fg=self.colors['accent'], font=('Arial', 12, 'bold')).pack(anchor='w')
        
        self.history_listbox = tk.Listbox(container, bg='#2d2d2d', fg='white',
                                         height=10, selectbackground=self.colors['accent'])
        self.history_listbox.pack(fill='x', pady=(0, 10))
        
        # Favorites section
        tk.Label(container, text="Favorite Dorks:", bg=self.colors['bg'], 
                fg=self.colors['accent'], font=('Arial', 12, 'bold')).pack(anchor='w')
        
        self.favorites_listbox = tk.Listbox(container, bg='#2d2d2d', fg='white',
                                           height=10, selectbackground=self.colors['highlight'])
        self.favorites_listbox.pack(fill='x', pady=(0, 10))
        
        # Action buttons
        btn_frame = tk.Frame(container, bg=self.colors['bg'])
        btn_frame.pack(fill='x')
        
        tk.Button(btn_frame, text="🗑️ Clear History", 
                 command=self.clear_history, bg=self.colors['warning'], 
                 fg='white').pack(side='left', padx=(0, 10))
        
        tk.Button(btn_frame, text="📋 Copy Selected", 
                 command=self.copy_selected_history,
                 bg=self.colors['secondary'], fg='white').pack(side='left', padx=(0, 10))
        
        tk.Button(btn_frame, text="🔍 Use Selected", 
                 command=self.use_selected_dork,
                 bg=self.colors['accent'], fg='white').pack(side='left')

    def setup_learning_tab(self, notebook=None):
        parent = notebook if notebook is not None else self.notebook
        tab = ttk.Frame(parent)
        parent.add(tab, text="🧠 Brain")
        container = tk.Frame(tab, bg=self.colors['bg'])
        container.pack(fill='both', expand=True, padx=20, pady=20)
        self.learning_stats_text = scrolledtext.ScrolledText(container, bg='#2d2d2d', fg='white')
        self.learning_stats_text.pack(fill='both', expand=True)

    def setup_live_validation_tab(self, notebook=None):
        parent = notebook if notebook is not None else self.notebook
        tab = ttk.Frame(parent)
        parent.add(tab, text="🌐 Live Validation")
        
        container = tk.Frame(tab, bg=self.colors['bg'])
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(container, text="Autonomous Dork Validator:", bg=self.colors['bg'], 
                fg=self.colors['accent'], font=('Arial', 14, 'bold')).pack(anchor='w', pady=(0, 10))
                
        tk.Label(container, text="Test your generated dorks against Google to find live results. Successful hits automatically train the DorkBrain.", 
                bg=self.colors['bg'], fg='white', wraplength=800).pack(anchor='w', pady=(0, 20))
                
        self.validator_log = scrolledtext.ScrolledText(container, bg='#2d2d2d', fg='white', height=20)
        self.validator_log.pack(fill='both', expand=True)
        
        btn_frame = tk.Frame(container, bg=self.colors['bg'])
        btn_frame.pack(fill='x', pady=10)
        
        self.validator = LiveValidator(self.brain, self.update_validator_log)
        
        tk.Button(btn_frame, text="▶️ Start Validation", command=self.start_validation, bg=self.colors['secondary'], fg='white').pack(side='left', padx=5)
        tk.Button(btn_frame, text="⏹️ Stop Validation", command=self.validator.stop, bg=self.colors['warning'], fg='white').pack(side='left', padx=5)

    def update_validator_log(self, msg):
        self.root.after(0, self._append_validator_log, msg)
        
    def _append_validator_log(self, msg):
        self.validator_log.insert(tk.END, msg + "\n")
        self.validator_log.see(tk.END)
        
    def start_validation(self):
        if self.validator.running:
            messagebox.showwarning("Warning", "Validator is already running.")
            return
            
        dorks = self.dorks_text.get(1.0, tk.END).strip().split('\n')
        dorks = [d.strip() for d in dorks if d.strip() and not d.startswith('---')]
        
        if not dorks:
            messagebox.showwarning("No Dorks", "Please generate some dorks in the Generator tab first.")
            return
            
        self.validator_log.delete(1.0, tk.END)
        self.validator_log.insert(tk.END, f"Starting validation for {len(dorks)} dorks...\n")
        
        dorks_to_test = dorks[:10]
        self.validator.validate_dorks(dorks_to_test)

    def setup_entity_profiler_tab(self, notebook=None):
        parent = notebook if notebook is not None else self.notebook
        tab = ttk.Frame(parent)
        parent.add(tab, text="🕵️ Entity Profiler")
        
        container = tk.Frame(tab, bg=self.colors['bg'])
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(container, text="Deep Scraping & Entity Dossier Generator", bg=self.colors['bg'], 
                fg=self.colors['accent'], font=('Arial', 14, 'bold')).pack(anchor='w', pady=(0, 10))
                
        input_frame = tk.Frame(container, bg=self.colors['bg'])
        input_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(input_frame, text="Target Full Name:", bg=self.colors['bg'], fg='white').grid(row=0, column=0, sticky='w', pady=2)
        self.ep_name_entry = tk.Entry(input_frame, bg='#2d2d2d', fg='white', width=30)
        self.ep_name_entry.grid(row=0, column=1, padx=10, pady=2)
        
        tk.Label(input_frame, text="Username (Optional):", bg=self.colors['bg'], fg='white').grid(row=1, column=0, sticky='w', pady=2)
        self.ep_user_entry = tk.Entry(input_frame, bg='#2d2d2d', fg='white', width=30)
        self.ep_user_entry.grid(row=1, column=1, padx=10, pady=2)
        
        tk.Label(input_frame, text="Company (Optional):", bg=self.colors['bg'], fg='white').grid(row=2, column=0, sticky='w', pady=2)
        self.ep_comp_entry = tk.Entry(input_frame, bg='#2d2d2d', fg='white', width=30)
        self.ep_comp_entry.grid(row=2, column=1, padx=10, pady=2)
        
        btn_frame = tk.Frame(container, bg=self.colors['bg'])
        btn_frame.pack(fill='x', pady=5)
        
        self.profiler = EntityProfiler(callback=self.update_profiler_log)
        
        tk.Button(btn_frame, text="🔍 Start Deep Scrape Profile", command=self.start_entity_profiler, bg=self.colors['highlight'], fg='black').pack(side='left', padx=5)
        tk.Button(btn_frame, text="⏹️ Stop", command=self.profiler.stop, bg=self.colors['warning'], fg='white').pack(side='left', padx=5)
        
        self.profiler_log = scrolledtext.ScrolledText(container, bg='#1a1a1a', fg='#00ff00', font=('Consolas', 10))
        self.profiler_log.pack(fill='both', expand=True, pady=10)

    def start_entity_profiler(self):
        name = self.ep_name_entry.get().strip()
        username = self.ep_user_entry.get().strip()
        company = self.ep_comp_entry.get().strip()
        
        if not name:
            messagebox.showwarning("Input Required", "Target Full Name is required to build a dossier.")
            return
            
        if self.profiler.running:
            messagebox.showwarning("Warning", "Profiler is already running.")
            return
            
        self.profiler_log.delete(1.0, tk.END)
        self.profiler.run_profiler(name, username, company)
        
    def update_profiler_log(self, msg):
        self.root.after(0, self._append_profiler_log, msg)
        
    def _append_profiler_log(self, msg):
        self.profiler_log.insert(tk.END, msg + "\n")
        self.profiler_log.see(tk.END)

    def setup_tools_suite_tab(self, notebook=None):
        parent = notebook if notebook is not None else self.notebook
        tab = ttk.Frame(parent)
        parent.add(tab, text="🛠️ OSINT Tool Suite")
        
        container = tk.Frame(tab, bg=self.colors['bg'])
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(container, text="External OSINT Tools Dashboard", bg=self.colors['bg'], 
                fg=self.colors['accent'], font=('Arial', 14, 'bold')).pack(anchor='w', pady=(0, 10))
                
        tk.Label(container, text="Launch standalone OSINT applications designed for specific tasks. Their output can be loaded directly into Project-GDork.", 
                bg=self.colors['bg'], fg='white', wraplength=800).pack(anchor='w', pady=(0, 20))
                
        # --- Advanced CWL Section ---
        cwl_frame = tk.Frame(container, bg='#2d2d2d', relief='sunken', borderwidth=1)
        cwl_frame.pack(fill='x', pady=10, padx=5)
        
        tk.Label(cwl_frame, text="Advanced Custom Wordlist Generator (CWL)", bg='#2d2d2d', 
                fg=self.colors['highlight'], font=('Arial', 12, 'bold')).pack(anchor='w', padx=10, pady=(10, 5))
                
        tk.Label(cwl_frame, text="Generates highly customized wordlists using personal target info. Great for password spraying or custom fuzzing.", 
                bg='#2d2d2d', fg='white').pack(anchor='w', padx=10)
                
        btn_frame = tk.Frame(cwl_frame, bg='#2d2d2d')
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(btn_frame, text="🚀 Launch CWL App", command=self.launch_cwl, bg=self.colors['accent'], fg='white').pack(side='left', padx=(0, 10))
        tk.Button(btn_frame, text="📥 Load Wordlist into Keywords", command=self.load_wordlist_to_keywords, bg=self.colors['secondary'], fg='white').pack(side='left', padx=10)
        
        # --- OSdb Section ---
        osdb_frame = tk.Frame(container, bg='#2d2d2d', relief='sunken', borderwidth=1)
        osdb_frame.pack(fill='x', pady=10, padx=5)
        
        tk.Label(osdb_frame, text="OSINT Project Management Database (OSdb)", bg='#2d2d2d', 
                fg=self.colors['highlight'], font=('Arial', 12, 'bold')).pack(anchor='w', padx=10, pady=(10, 5))
                
        tk.Label(osdb_frame, text="Manage, track, and organize your OSINT investigations in a centralized database.", 
                bg='#2d2d2d', fg='white').pack(anchor='w', padx=10)
                
        osdb_btn_frame = tk.Frame(osdb_frame, bg='#2d2d2d')
        osdb_btn_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(osdb_btn_frame, text="🚀 Launch OSdb Engine", command=self.launch_osdb, bg=self.colors['accent'], fg='white').pack(side='left', padx=(0, 10))
        
        # --- AllSeenEye Section ---
        ase_frame = tk.Frame(container, bg='#2d2d2d', relief='sunken', borderwidth=1)
        ase_frame.pack(fill='x', pady=10, padx=5)
        
        tk.Label(ase_frame, text="Advanced OSINT Investigator (AllSeenEye)", bg='#2d2d2d', 
                fg=self.colors['highlight'], font=('Arial', 12, 'bold')).pack(anchor='w', padx=10, pady=(10, 5))
                
        tk.Label(ase_frame, text="Perform deep, comprehensive social media and IP investigations.", 
                bg='#2d2d2d', fg='white').pack(anchor='w', padx=10)
                
        ase_btn_frame = tk.Frame(ase_frame, bg='#2d2d2d')
        ase_btn_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(ase_btn_frame, text="🚀 Launch AllSeenEye", command=self.launch_allseeneye, bg=self.colors['accent'], fg='white').pack(side='left', padx=(0, 10))
        
    def launch_cwl(self):
        cwl_path = os.path.join(os.path.dirname(__file__), 'tools', 'cwl', 'cwl_gui.py')
        if os.path.exists(cwl_path):
            self.update_status("Launching Advanced CWL Tool...")
            # Run detached so it doesn't block the UI
            subprocess.Popen(['python', cwl_path], creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
        else:
            messagebox.showerror("Error", f"Could not find CWL tool at:\n{cwl_path}")

    def launch_osdb(self):
        osdb_path = os.path.join(os.path.dirname(__file__), 'tools', 'osdb', 'main.py')
        osdb_dir = os.path.join(os.path.dirname(__file__), 'tools', 'osdb')
        if os.path.exists(osdb_path):
            self.update_status("Launching OSdb Engine...")
            subprocess.Popen(['python', osdb_path], cwd=osdb_dir, creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
        else:
            messagebox.showerror("Error", f"Could not find OSdb tool at:\n{osdb_path}")
            
    def launch_allseeneye(self):
        ase_path = os.path.join(os.path.dirname(__file__), 'tools', 'allseeneye', 'osint.py')
        ase_dir = os.path.join(os.path.dirname(__file__), 'tools', 'allseeneye')
        if os.path.exists(ase_path):
            self.update_status("Launching AllSeenEye...")
            subprocess.Popen(['python', ase_path], cwd=ase_dir, creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
        else:
            messagebox.showerror("Error", f"Could not find AllSeenEye tool at:\n{ase_path}")

    def setup_people_finder_guides_tab(self, notebook=None):
        parent = notebook if notebook is not None else self.notebook
        tab = ttk.Frame(parent)
        parent.add(tab, text="🔍 People Finder Guides")

        # Main layout: Left selection list, Right content panel
        main_container = tk.Frame(tab, bg=self.colors['bg'])
        main_container.pack(fill='both', expand=True)

        # Left selection list (takes 1/4 of width)
        left_frame = tk.Frame(main_container, bg='#1a1a1a', width=280)
        left_frame.pack(side='left', fill='y', padx=(5, 2), pady=5)
        left_frame.pack_propagate(False)

        tk.Label(left_frame, text="OSINT Search Vectors", bg='#1a1a1a', fg=self.colors['accent'],
                 font=('Arial', 12, 'bold')).pack(anchor='w', padx=10, pady=10)

        # Listbox for categories
        self.guide_categories = [
            "📧 Email Search OSINT",
            "👤 Username OSINT",
            "📱 Phone Number Lookup",
            "📸 Facial Recognition & Image",
            "🗄️ Public Records & Registries",
            "🛡️ Privacy Opt-Out & Safety",
            "📖 GDork Suite Usage Manual"
        ]
        
        self.guide_listbox = tk.Listbox(left_frame, bg='#2d2d2d', fg='white',
                                       selectbackground=self.colors['accent'],
                                       font=('Arial', 10), bd=0, highlightthickness=0)
        for cat in self.guide_categories:
            self.guide_listbox.insert(tk.END, cat)
        self.guide_listbox.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        self.guide_listbox.bind('<<ListboxSelect>>', self.on_guide_select)

        # Right content panel (wrapped in ScrollableFrame)
        self.right_scroll = ScrollableFrame(main_container)
        self.right_scroll.pack(side='right', fill='both', expand=True, padx=(2, 5), pady=5)

        self.guide_content_frame = tk.Frame(self.right_scroll.scrollable_frame, bg=self.colors['bg'])
        self.guide_content_frame.pack(fill='both', expand=True, padx=15, pady=10)

        # Initialize to first guide
        self.guide_listbox.selection_set(0)
        self.on_guide_select(None)

    def on_guide_select(self, event):
        # Clear existing content in right pane
        for widget in self.guide_content_frame.winfo_children():
            widget.destroy()

        selection = self.guide_listbox.curselection()
        if not selection:
            return
        idx = selection[0]
        category = self.guide_categories[idx]

        # Detailed Guide Data
        guides_data = {
            0: {
                "title": "📧 Email Search OSINT",
                "desc": "Email addresses are powerful pivot points in OSINT investigations. A single email can uncover registered social media accounts, real names, and profile pictures.",
                "tools": [
                    {"name": "Epieos", "url": "https://epieos.com", "desc": "Excellent tool for reverse email lookup. Uncovers linked Google accounts (giving real name, profile photo, Google Maps reviews) and Microsoft accounts without alerting the target."},
                    {"name": "Holehe", "url": "https://github.com/megadose/holehe", "desc": "A Python tool checking registered accounts on 120+ platforms (like Twitter, Instagram, LinkedIn). Integrated directly under the GDork Person Hub!"},
                    {"name": "Hunter.io", "url": "https://hunter.io", "desc": "Finds professional email addresses, formats, and references for target domains."}
                ],
                "manual": """STEP-BY-STEP EMAIL SCANNING MANUAL:
1. Google Account Mapping: Submit the target email to Epieos. If it belongs to a Google account, retrieve the gaia ID, profile photo, Google Maps contributions, and calendar links.
2. Platform Registrations: Launch GDork's Person Hub and enter the email. The integrated Holehe engine will sweep 120+ sites to tell you exactly where the target has accounts.
3. Breach History Verification: Use HaveIBeenPwned or Dehashed (via GDork Settings keys) to find historical data breaches containing the target email. This reveals associated credentials, passwords, and addresses.
4. Username Extraction: Extract the prefix of the email (e.g., if target is john.doe44@gmail.com, extract 'john.doe44') and use it in the Username Search vector."""
            },
            1: {
                "title": "👤 Username OSINT",
                "desc": "Targets often reuse usernames across multiple social, technical, and gaming forums. Finding these accounts helps map their hobbies, alias histories, and online contacts.",
                "tools": [
                    {"name": "Sherlock", "url": "https://sherlock-project.github.io", "desc": "High-speed username scanner querying 400+ platforms. Output profiles are listed directly in the GDork Person Hub!"},
                    {"name": "WhatsMyName.app", "url": "https://whatsmyname.app", "desc": "Web-based lookup tool checking usernames against hundreds of sites with a clean, exportable list."},
                    {"name": "Namechk", "url": "https://namechk.com", "desc": "Checks username availability on dozens of major social and domain extensions."}
                ],
                "manual": """STEP-BY-STEP USERNAME SCANNING MANUAL:
1. Multi-Platform Scan: Run the target username through Sherlock inside GDork (OSINT Hub -> Person Hub) to locate accounts.
2. Secondary Search: Cross-reference findings on WhatsMyName.app to find gaming profiles or forums not checked by Sherlock.
3. Verification: Review the linked bios, profile pictures, and timestamps of found accounts to verify that they belong to the same target rather than different users with the same alias.
4. Passive Dorking: Use Google Dorks to find cached references to the username (e.g., 'intext:\"username\" -site:github.com')."""
            },
            2: {
                "title": "📱 Phone Number Lookup",
                "desc": "Phone numbers represent unique identifiers linked to real-world identity, financial records, and physical locations.",
                "tools": [
                    {"name": "Truecaller", "url": "https://www.truecaller.com", "desc": "Global reverse caller ID directory used to identify the registered name of a phone number."},
                    {"name": "NumLookup", "url": "https://www.numlookup.com", "desc": "Free reverse phone lookup service for US and international numbers."},
                    {"name": "Sync.me", "url": "https://sync.me", "desc": "Identifies caller name and correlates their phone number with active social media accounts."}
                ],
                "manual": """STEP-BY-STEP PHONE LOOKUP MANUAL:
1. Reverse Directory Query: Search the number on Truecaller or NumLookup to get the primary name and carrier information.
2. Messaging Application Check: Save the phone number on a test device or VM. Launch messaging apps (WhatsApp, Signal, Telegram) to see if they display a profile picture, name, or status.
3. Breach Lookup: Query the number in Dehashed (e.g. phone:15551234567) to see if it is associated with leaked database entries or compromised credentials.
4. Social Media Recovery Pages: Start a password recovery flow on Google or Facebook using the number. Analyze the masked return details (e.g., 'j*****@g****.com') to map secondary email addresses."""
            },
            3: {
                "title": "📸 Facial Recognition & Image OSINT",
                "desc": "Facial recognition tools search the public web to locate matching profiles, news articles, and personal blogs containing the target's face.",
                "tools": [
                    {"name": "FaceCheck.id", "url": "https://facecheck.id", "desc": "Face search engine targeting social media profiles, blogs, and public records. GDork has built-in API integration!"},
                    {"name": "PimEyes", "url": "https://pimeyes.com", "desc": "Powerful facial recognition search engine finding matching images across the public web."},
                    {"name": "TinEye", "url": "https://tineye.com", "desc": "Reverse image search focusing on finding duplicates or modifications of a specific image file."},
                    {"name": "Google Lens", "url": "https://lens.google", "desc": "Excellent for general visual search, matching items, finding original source websites, and cropped face searches."}
                ],
                "manual": """STEP-BY-STEP FACIAL SEARCH MANUAL:
1. Preparation: Crop the target's face from a profile photo. Ensure it is high resolution, front-facing, and contains no filters, hats, or dark glasses.
2. Face Match Search: Upload the image to FaceCheck.id or PimEyes (GDork Person Hub does this automatically if keys are set in Settings).
3. Result Analysis: Review match scores and visit the pages where matches were found. These frequently lead to personal portfolios, secondary platforms, or school registers.
4. Provenance Search: Upload the full profile picture to Google Lens or TinEye to locate the earliest upload date and original source context."""
            },
            4: {
                "title": "🗄️ Public Records & Registries",
                "desc": "Public records and directories are crucial for finding locations, phone numbers, family associations, and legal filings of US/international targets.",
                "tools": [
                    {"name": "OSINT Framework", "url": "https://osintframework.com", "desc": "A detailed web directory linking free OSINT resources for any category imaginable."},
                    {"name": "ThatThem", "url": "https://thatthem.com", "desc": "Free search engine providing addresses, emails, phone numbers, and demographics for US individuals."},
                    {"name": "FastPeopleSearch", "url": "https://www.fastpeoplesearch.com", "desc": "One of the most comprehensive free US directories for finding relative names, addresses, and history."}
                ],
                "manual": """STEP-BY-STEP PUBLIC RECORDS MANUAL:
1. General Directory Query: For US targets, use FastPeopleSearch or ThatThem to find full names, phone records, and email addresses.
2. Associate Mapping: Note down names of relatives and associates. Investigating associates often leads to the primary target when they maintain private settings.
3. Property & Voter Records: Search local county tax assessors and voter registrations to locate official property deeds and voter history.
4. Corporate filings: Search OpenCorporates to see if the target has registered any companies or LLCs in their name."""
            },
            5: {
                "title": "🛡️ Privacy Opt-Out & Safety",
                "desc": "Personal security and privacy are paramount. Knowing how to find someone also means knowing how to remove your own data from data brokers and registries.",
                "tools": [
                    {"name": "IntelTechniques Data Removal", "url": "https://inteltechniques.com/workout.html", "desc": "Free opt-out guides and templates created by OSINT expert Michael Bazzell."},
                    {"name": "Kanary", "url": "https://www.neokanary.com", "desc": "Service to monitor, detect, and request deletion of your data from public brokers."},
                    {"name": "DeleteMe", "url": "https://joindeleteme.com", "desc": "Premium subscription service that handles data opt-outs on data brokers automatically."}
                ],
                "manual": """STEP-BY-STEP DATA REMOVAL MANUAL:
1. Audit Exposure: Search your own name and phone number on public databases like FastPeopleSearch, Spokeo, Radaris, and Whitepages.
2. Locate Opt-Out Forms: Scroll to the footer of each broker site and click links like 'Opt-Out', 'Do Not Sell My Info', or 'Privacy Control'.
3. Submit Removal Requests: Fill out the broker forms. Always use a burner email address and a temporary number (like Voip) when submitting requests to avoid giving brokers your real email.
4. Continuous Monitoring: Review your exposure every 3 to 6 months, as data brokers frequently scraping the web will recreate deleted records."""
            },
            6: {
                "title": "📖 GDork Suite Usage Manual",
                "desc": "A complete manual on how to maximize Project-GDork's built-in modules to gather intelligence, profiles, and scan targets.",
                "tools": [],
                "manual": """GDORK PRO OSINT MANUAL & DOCUMENTATION:

1. DORK GENERATOR STUDIO:
   - Target Domain: Enter target domain (e.g. 'company.com').
   - Keywords: Enter terms (e.g. 'password, config, admin').
   - Search Intent: Select a preset. Presets modify search dorks to target specific exposures (Credentials, Vulns, IoT).
   - Generate Combos: Click 'Generate All Combos' to run the combinatorial generator. It mixes keywords with hundreds of advanced patterns.
   - Live Validation: Click 'Start Validation' in the Live Validation tab to autonomously test if Google has results.

2. OSINT HUB:
   - Person Hub: Enter known parameters (Name, Email, Username, Phone, Photo). The tool runs HaveIBeenPwned, Dehashed, LeakCheck, Sherlock, Holehe, PimEyes, and FaceCheck in parallel and generates a styled HTML report.
   - Entity Profiler: Builds a complete target profile. It generates customized search dorks, retrieves URLs from Google search, visits those links, and extracts emails, phone numbers, social media links, BTC wallets, and IPs.
   - SOCMINT: Sweeps Twitter, Reddit, GitHub, and Pastebin simultaneously.
   - GEOINT: Resolves bulk IP addresses to coordinates, timezone, organization, and displays the first result on Google Maps.

3. SCAN & API:
   - API Intelligence: Queries Shodan and VirusTotal for host details, open ports, and file hash threat intelligence.
   - Nuclei: Performs vulnerability scanning using ProjectDiscovery templates. Requires Nuclei in path.

4. SETTINGS & SAFETY:
   - Route traffic through TOR: Enable the TOR checkbox in settings (requires TOR running on port 9050) to query Google without being blocked by captchas or disclosing your IP address.
   - API Keys: Always load your credentials for Dehashed, Shodan, and VT to enable advanced Person Hub features."""
            }
        }

        data = guides_data[idx]

        # UI Construction in right pane
        tk.Label(self.guide_content_frame, text=data["title"], bg=self.colors['bg'],
                 fg=self.colors['accent'], font=('Arial', 16, 'bold')).pack(anchor='w', pady=(0, 5))

        tk.Label(self.guide_content_frame, text=data["desc"], bg=self.colors['bg'],
                 fg='white', wraplength=550, justify='left', font=('Arial', 10)).pack(anchor='w', pady=(0, 15))

        if data["tools"]:
            tk.Label(self.guide_content_frame, text="Curated Platforms & Tools", bg=self.colors['bg'],
                     fg=self.colors['highlight'], font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0, 10))

            for t in data["tools"]:
                t_frame = tk.Frame(self.guide_content_frame, bg='#2d2d2d', relief='flat', bd=1)
                t_frame.pack(fill='x', pady=4)

                # Title and description layout
                info_frame = tk.Frame(t_frame, bg='#2d2d2d')
                info_frame.pack(side='left', fill='both', expand=True, padx=10, pady=5)

                tk.Label(info_frame, text=t["name"], bg='#2d2d2d', fg=self.colors['accent'],
                         font=('Arial', 10, 'bold')).pack(anchor='w')
                tk.Label(info_frame, text=t["desc"], bg='#2d2d2d', fg='#e0e0e0',
                         wraplength=400, justify='left', font=('Arial', 9)).pack(anchor='w')

                # Launch button
                btn = tk.Button(t_frame, text="🌐 Visit Site", bg=self.colors['secondary'], fg='white',
                                font=('Arial', 9), command=lambda url=t["url"]: webbrowser.open(url))
                btn.pack(side='right', padx=10, pady=5)

        # Methodology Manual section
        tk.Label(self.guide_content_frame, text="Methodology & Usage Manual", bg=self.colors['bg'],
                 fg=self.colors['highlight'], font=('Arial', 12, 'bold')).pack(anchor='w', pady=(15, 5))

        manual_text = scrolledtext.ScrolledText(self.guide_content_frame, bg='#1a1a1a', fg='#00ff00',
                                               font=('Consolas', 10), height=15, wrap=tk.WORD)
        manual_text.pack(fill='both', expand=True, pady=5)
        manual_text.insert(tk.END, data["manual"])
        manual_text.config(state='disabled')

    def load_wordlist_to_keywords(self):
        file_path = filedialog.askopenfilename(title="Select Wordlist", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    words = [line.strip() for line in f if line.strip()]
                if not words:
                    messagebox.showwarning("Empty File", "The selected wordlist is empty.")
                    return
                
                # Ask user if they want to load into standard keywords or entity profiler
                choice = messagebox.askyesno("Load Destination", "Click YES to append to standard Generator Keywords.\nClick NO to replace Entity Profiler username.")
                
                if choice:
                    current = self.keywords_entry.get().strip()
                    new_keywords = current + (", " if current else "") + ", ".join(words[:20]) # Load first 20 to avoid crashing UI
                    if len(words) > 20:
                        new_keywords += f" (+{len(words)-20} more...)"
                    self.keywords_entry.delete(0, tk.END)
                    self.keywords_entry.insert(0, new_keywords)
                    self.update_status(f"Loaded {len(words)} keywords from list.")
                else:
                    self.ep_user_entry.delete(0, tk.END)
                    self.ep_user_entry.insert(0, words[0]) # Use the first major entry
                    self.update_status(f"Loaded {words[0]} into Profiler.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load wordlist:\n{e}")


    def setup_socmint_tab(self, notebook=None):
        parent = notebook if notebook is not None else self.notebook
        tab = ttk.Frame(parent)
        parent.add(tab, text="👥 SOCMINT")
        container = tk.Frame(tab, bg=self.colors['bg'])
        container.pack(fill='both', expand=True, padx=20, pady=20)

        tk.Label(container, text="Social Media Intelligence Engine", bg=self.colors['bg'],
                fg=self.colors['accent'], font=('Arial', 14, 'bold')).pack(anchor='w', pady=(0, 5))
        tk.Label(container, text="Simultaneously search Reddit, GitHub, Pastebin & Twitter/X for target mentions.",
                bg=self.colors['bg'], fg='white').pack(anchor='w', pady=(0, 15))

        inp = tk.Frame(container, bg=self.colors['bg'])
        inp.pack(fill='x', pady=5)
        tk.Label(inp, text="Target Query:", bg=self.colors['bg'], fg='white').pack(side='left')
        self.socmint_query = tk.Entry(inp, bg='#2d2d2d', fg='white', width=40)
        self.socmint_query.pack(side='left', padx=10)

        btn = tk.Frame(container, bg=self.colors['bg'])
        btn.pack(fill='x', pady=8)
        self.socmint_engine = SOCMINTEngine(callback=self.update_socmint_log)
        tk.Button(btn, text="🔍 Start SOCMINT Sweep", command=self.start_socmint,
                 bg=self.colors['highlight'], fg='black').pack(side='left', padx=5)
        tk.Button(btn, text="⏹️ Stop", command=self.socmint_engine.stop,
                 bg=self.colors['warning'], fg='white').pack(side='left', padx=5)

        self.socmint_log = scrolledtext.ScrolledText(container, bg='#1a1a1a', fg='#00ff00', font=('Consolas', 10))
        self.socmint_log.pack(fill='both', expand=True, pady=10)

    def start_socmint(self):
        q = self.socmint_query.get().strip()
        if not q:
            messagebox.showwarning("Input Required", "Enter a target query to sweep.")
            return
        keys = self.config_manager.load_keys()
        self.socmint_engine.github_token = keys.get('github', '')
        self.socmint_engine.twitter_bearer = keys.get('twitter', '')
        self.socmint_log.delete(1.0, tk.END)
        self.socmint_log.insert(tk.END, f"🚀 SOCMINT sweep started for: {q}\n" + "="*50 + "\n")
        self.socmint_engine.run(q)

    def update_socmint_log(self, msg):
        self.root.after(0, lambda: (self.socmint_log.insert(tk.END, msg + "\n"), self.socmint_log.see(tk.END)))

    def setup_geoint_tab(self, notebook=None):
        parent = notebook if notebook is not None else self.notebook
        tab = ttk.Frame(parent)
        parent.add(tab, text="🌍 GEOINT")
        container = tk.Frame(tab, bg=self.colors['bg'])
        container.pack(fill='both', expand=True, padx=20, pady=20)

        tk.Label(container, text="Geospatial Intelligence Engine", bg=self.colors['bg'],
                fg=self.colors['accent'], font=('Arial', 14, 'bold')).pack(anchor='w', pady=(0, 5))

        inp = tk.Frame(container, bg=self.colors['bg'])
        inp.pack(fill='x', pady=5)
        tk.Label(inp, text="IP Addresses (comma separated):", bg=self.colors['bg'], fg='white').pack(side='left')
        self.geoint_entry = tk.Entry(inp, bg='#2d2d2d', fg='white', width=50)
        self.geoint_entry.pack(side='left', padx=10)
        self.geoint_entry.insert(0, "8.8.8.8, 1.1.1.1")

        btn = tk.Frame(container, bg=self.colors['bg'])
        btn.pack(fill='x', pady=8)
        tk.Button(btn, text="📍 Geolocate IPs", command=self.run_geoint,
                 bg=self.colors['highlight'], fg='black').pack(side='left', padx=5)
        tk.Button(btn, text="🗺️ Show on Map (First Result)", command=self.open_map,
                 bg=self.colors['secondary'], fg='white').pack(side='left', padx=5)

        # Table
        cols = ('IP', 'City', 'Country', 'Org / ASN', 'Lat', 'Lon', 'Timezone')
        self.geo_tree = ttk.Treeview(container, columns=cols, show='headings', height=8)
        for c in cols:
            self.geo_tree.heading(c, text=c)
            self.geo_tree.column(c, width=130)
        self.geo_tree.pack(fill='x', pady=5)

        self.geoint_log = scrolledtext.ScrolledText(container, bg='#1a1a1a', fg='#00ff00',
                                                     font=('Consolas', 9), height=8)
        self.geoint_log.pack(fill='both', expand=True)

    def run_geoint(self):
        raw = self.geoint_entry.get().strip()
        ips = [ip.strip() for ip in raw.split(',') if ip.strip()]
        if not ips:
            messagebox.showwarning("Input Required", "Enter at least one IP address.")
            return
        self.geo_tree.delete(*self.geo_tree.get_children())
        self.geoint_log.delete(1.0, tk.END)
        self.geoint_log.insert(tk.END, f"🌍 Starting geolocation for {len(ips)} IPs...\n")

        def worker():
            results = self.geoint.geolocate_bulk(ips, progress_callback=self.update_geoint_log)
            self.geo_results = results
            for r in results:
                if 'error' not in r:
                    # Use a lambda to avoid passing keyword arguments directly to root.after
                    vals = (
                        r['ip'], r['city'], f"{r['country_code']} {r['country']}",
                        r.get('org', '')[:25], r.get('lat'), r.get('lon'), r.get('timezone')
                    )
                    self.root.after(0, lambda v=vals: self.geo_tree.insert('', 'end', values=v))
            self.root.after(0, self.update_geoint_log, "\n✅ Geolocation complete.")
        threading.Thread(target=worker, daemon=True).start()

    def update_geoint_log(self, msg):
        self.root.after(0, lambda: (self.geoint_log.insert(tk.END, msg + "\n"), self.geoint_log.see(tk.END)))

    def open_map(self):
        valid = [r for r in self.geo_results if r.get('lat') and r.get('lon')]
        if valid:
            import webbrowser
            url = self.geoint.get_map_url(valid[0]['lat'], valid[0]['lon'])
            webbrowser.open(url)
        else:
            messagebox.showwarning("No Data", "Run Geolocation first.")

    def setup_nuclei_tab(self, notebook=None):
        parent = notebook if notebook is not None else self.notebook
        tab = ttk.Frame(parent)
        parent.add(tab, text="🔬 Nuclei")
        
        scroll_container = ScrollableFrame(tab)
        scroll_container.pack(fill='both', expand=True)
        
        container = tk.Frame(scroll_container.scrollable_frame, bg=self.colors['bg'])
        container.pack(fill='both', expand=True, padx=20, pady=20)

        tk.Label(container, text="Nuclei Vulnerability Scanner", bg=self.colors['bg'],
                fg=self.colors['accent'], font=('Arial', 14, 'bold')).pack(anchor='w', pady=(0, 5))
        tk.Label(container, text="Runs ProjectDiscovery Nuclei CVE/misconfiguration scanning. Nuclei must be installed in PATH.",
                bg=self.colors['bg'], fg='white', wraplength=800).pack(anchor='w', pady=(0, 10))

        # Check binary installation and warn user
        self.nuclei_scanner = NucleiScanner(callback=self.update_nuclei_log)
        if not self.nuclei_scanner.is_installed():
            warn_frame = tk.Frame(container, bg='#3a1a1a', relief='solid', bd=1)
            warn_frame.pack(fill='x', pady=(0, 10))
            tk.Label(warn_frame, text="⚠️ [WARNING] Nuclei binary is not detected in your system PATH.\nDownload it from: https://github.com/projectdiscovery/nuclei/releases",
                     bg='#3a1a1a', fg=self.colors['warning'], font=('Arial', 10, 'bold')).pack(padx=10, pady=8)

        inp = tk.Frame(container, bg=self.colors['bg'])
        inp.pack(fill='x', pady=5)
        tk.Label(inp, text="Target URL:", bg=self.colors['bg'], fg='white').pack(side='left')
        self.nuclei_target = tk.Entry(inp, bg='#2d2d2d', fg='white', width=40)
        self.nuclei_target.pack(side='left', padx=10)
        self.nuclei_target.insert(0, "https://example.com")

        # Custom templates path
        custom_tpl_frame = tk.Frame(container, bg=self.colors['bg'])
        custom_tpl_frame.pack(fill='x', pady=5)
        tk.Label(custom_tpl_frame, text="Custom Templates Path/Dir:", bg=self.colors['bg'], fg='white').pack(side='left')
        self.nuclei_custom_templates = tk.Entry(custom_tpl_frame, bg='#2d2d2d', fg='white', width=40)
        self.nuclei_custom_templates.pack(side='left', padx=10)

        # Template checkboxes
        tpl_frame = tk.Frame(container, bg=self.colors['bg'])
        tpl_frame.pack(fill='x', pady=5)
        tk.Label(tpl_frame, text="Templates:", bg=self.colors['bg'], fg='white').pack(side='left', padx=5)
        self.nuclei_tpls = {}
        
        # Grid layout for checkboxes
        grid_frame = tk.Frame(tpl_frame, bg=self.colors['bg'])
        grid_frame.pack(side='left', padx=10)
        categories = ['cves', 'exposures', 'misconfigs', 'takeovers', 'technologies', 'vulnerabilities', 'ssl', 'dns', 'network', 'file', 'default-logins']
        for idx, cat in enumerate(categories):
            var = tk.BooleanVar(value=(cat in ['cves', 'exposures']))
            cb = tk.Checkbutton(grid_frame, text=cat, variable=var,
                               bg=self.colors['bg'], fg='white', selectcolor='#2d2d2d')
            cb.grid(row=idx//4, column=idx%4, sticky='w', padx=5, pady=2)
            self.nuclei_tpls[cat] = var

        sev_frame = tk.Frame(container, bg=self.colors['bg'])
        sev_frame.pack(fill='x', pady=5)
        tk.Label(sev_frame, text="Min Severity:", bg=self.colors['bg'], fg='white').pack(side='left', padx=5)
        self.nuclei_severity = ttk.Combobox(sev_frame, values=['low,medium,high,critical', 'medium,high,critical', 'high,critical', 'critical'], width=25)
        self.nuclei_severity.set('medium,high,critical')
        self.nuclei_severity.pack(side='left', padx=5)

        # Concurrency & Rate Limit
        limits_frame = tk.Frame(container, bg=self.colors['bg'])
        limits_frame.pack(fill='x', pady=5)
        tk.Label(limits_frame, text="Concurrency (-c):", bg=self.colors['bg'], fg='white').pack(side='left', padx=5)
        self.nuclei_concurrency = tk.Spinbox(limits_frame, from_=1, to=200, width=5)
        self.nuclei_concurrency.pack(side='left', padx=5)
        self.nuclei_concurrency.delete(0, 'end')
        self.nuclei_concurrency.insert(0, '25')

        tk.Label(limits_frame, text="Rate Limit (-rl):", bg=self.colors['bg'], fg='white').pack(side='left', padx=15)
        self.nuclei_rate_limit = tk.Spinbox(limits_frame, from_=1, to=1000, width=5)
        self.nuclei_rate_limit.pack(side='left', padx=5)
        self.nuclei_rate_limit.delete(0, 'end')
        self.nuclei_rate_limit.insert(0, '150')

        # Proxy and headers
        options_frame = tk.Frame(container, bg=self.colors['bg'])
        options_frame.pack(fill='x', pady=5)
        tk.Label(options_frame, text="HTTP Proxy URL:", bg=self.colors['bg'], fg='white').pack(side='left', padx=5)
        self.nuclei_proxy = tk.Entry(options_frame, bg='#2d2d2d', fg='white', width=20)
        self.nuclei_proxy.pack(side='left', padx=5)

        tk.Label(options_frame, text="Custom Header (Key:Val):", bg=self.colors['bg'], fg='white').pack(side='left', padx=15)
        self.nuclei_headers = tk.Entry(options_frame, bg='#2d2d2d', fg='white', width=25)
        self.nuclei_headers.pack(side='left', padx=5)

        # Scanning mode checkboxes
        modes_frame = tk.Frame(container, bg=self.colors['bg'])
        modes_frame.pack(fill='x', pady=5)
        self.nuclei_headless = tk.BooleanVar(value=False)
        tk.Checkbutton(modes_frame, text="Headless Scan (-headless)", variable=self.nuclei_headless,
                       bg=self.colors['bg'], fg='white', selectcolor='#2d2d2d').pack(side='left', padx=5)

        self.nuclei_scan_all_ips = tk.BooleanVar(value=False)
        tk.Checkbutton(modes_frame, text="Scan All IPs (-scan-all-ips)", variable=self.nuclei_scan_all_ips,
                       bg=self.colors['bg'], fg='white', selectcolor='#2d2d2d').pack(side='left', padx=15)

        self.nuclei_silent = tk.BooleanVar(value=False)
        tk.Checkbutton(modes_frame, text="Silent Mode (-silent)", variable=self.nuclei_silent,
                       bg=self.colors['bg'], fg='white', selectcolor='#2d2d2d').pack(side='left', padx=15)

        # Buttons
        btn = tk.Frame(container, bg=self.colors['bg'])
        btn.pack(fill='x', pady=8)
        
        tk.Button(btn, text="▶️ Start Nuclei Scan", command=self.start_nuclei,
                 bg=self.colors['highlight'], fg='black', font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        tk.Button(btn, text="⏹️ Stop Scan", command=self.nuclei_scanner.stop,
                 bg=self.colors['warning'], fg='white').pack(side='left', padx=5)
                 
        tk.Button(btn, text="🔄 Update Templates (-ut)", command=self.update_nuclei_templates,
                 bg=self.colors['accent'], fg='white').pack(side='left', padx=15)
        tk.Button(btn, text="🚀 Update Engine (-up)", command=self.update_nuclei_engine,
                 bg=self.colors['secondary'], fg='white').pack(side='left', padx=5)

        self.nuclei_log = scrolledtext.ScrolledText(container, bg='#1a1a1a', fg='#00ff00', font=('Consolas', 10), height=15)
        self.nuclei_log.pack(fill='both', expand=True, pady=10)

    def start_nuclei(self):
        target = self.nuclei_target.get().strip()
        if not target:
            messagebox.showwarning("Input Required", "Enter a target URL.")
            return
            
        templates = [cat for cat, var in self.nuclei_tpls.items() if var.get()]
        custom_tpl = self.nuclei_custom_templates.get().strip()
        severity = self.nuclei_severity.get()
        
        try:
            concurrency = int(self.nuclei_concurrency.get())
        except ValueError:
            concurrency = None
            
        try:
            rate_limit = int(self.nuclei_rate_limit.get())
        except ValueError:
            rate_limit = None
            
        proxy = self.nuclei_proxy.get().strip() or None
        
        headers_raw = self.nuclei_headers.get().strip()
        headers = [headers_raw] if headers_raw else None
        
        headless = self.nuclei_headless.get()
        scan_all_ips = self.nuclei_scan_all_ips.get()
        silent = self.nuclei_silent.get()
        
        self.nuclei_log.delete(1.0, tk.END)
        self.nuclei_scanner.scan(
            target=target,
            templates=templates if templates else None,
            custom_template_path=custom_tpl if custom_tpl else None,
            severity=severity,
            concurrency=concurrency,
            rate_limit=rate_limit,
            headers=headers,
            proxy=proxy,
            headless=headless,
            scan_all_ips=scan_all_ips,
            silent=silent
        )

    def update_nuclei_templates(self):
        self.nuclei_log.delete(1.0, tk.END)
        self.nuclei_log.insert(tk.END, "[*] Running: nuclei -update-templates (-ut)...\n")
        def worker():
            try:
                proc = subprocess.Popen(['nuclei', '-ut'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                for line in iter(proc.stdout.readline, ''):
                    self.root.after(0, lambda l=line: (self.nuclei_log.insert(tk.END, l), self.nuclei_log.see(tk.END)))
                proc.wait()
                self.root.after(0, lambda: self.nuclei_log.insert(tk.END, "\n[+] Templates updated successfully.\n"))
            except Exception as e:
                self.root.after(0, lambda err=e: self.nuclei_log.insert(tk.END, f"\n[ERROR] Update failed: {err}\n"))
        threading.Thread(target=worker, daemon=True).start()

    def update_nuclei_engine(self):
        self.nuclei_log.delete(1.0, tk.END)
        self.nuclei_log.insert(tk.END, "[*] Running: nuclei -update (-up)...\n")
        def worker():
            try:
                proc = subprocess.Popen(['nuclei', '-up'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                for line in iter(proc.stdout.readline, ''):
                    self.root.after(0, lambda l=line: (self.nuclei_log.insert(tk.END, l), self.nuclei_log.see(tk.END)))
                proc.wait()
                self.root.after(0, lambda: self.nuclei_log.insert(tk.END, "\n[+] Engine update complete.\n"))
            except Exception as e:
                self.root.after(0, lambda err=e: self.nuclei_log.insert(tk.END, f"\n[ERROR] Update failed: {err}\n"))
        threading.Thread(target=worker, daemon=True).start()

    def update_nuclei_log(self, msg):
        self.root.after(0, lambda: (self.nuclei_log.insert(tk.END, msg + "\n"), self.nuclei_log.see(tk.END)))

    def setup_graphs_tab(self, notebook=None):
        parent = notebook if notebook is not None else self.notebook
        tab = ttk.Frame(parent)
        parent.add(tab, text="📊 Graphs")
        container = tk.Frame(tab, bg=self.colors['bg'])
        container.pack(fill='both', expand=True, padx=10, pady=10)

        tk.Label(container, text="Intelligence Visualization", bg=self.colors['bg'],
                fg=self.colors['accent'], font=('Arial', 14, 'bold')).pack(anchor='w', pady=(0, 5))

        btn_row = tk.Frame(container, bg=self.colors['bg'])
        btn_row.pack(fill='x', pady=5)

        self.graph_canvas_frame = tk.Frame(container, bg='#2d2d2d')
        self.graph_canvas_frame.pack(fill='both', expand=True)

        btn_defs = [
            ("🧠 Dork Brain Performance", lambda: GraphEngine.dork_performance_chart(self.graph_canvas_frame, self.brain.knowledge)),
            ("📊 Validation Stats Pie", lambda: GraphEngine.validation_pie_chart(self.graph_canvas_frame, **self.validation_stats)),
            ("🌍 GEOINT Map", lambda: GraphEngine.geoint_map_chart(self.graph_canvas_frame, self.geo_results)),
            ("🕸️ Entity Network", lambda: GraphEngine.entity_network_graph(
                self.graph_canvas_frame,
                emails=self.socmint_hits.get('emails', []),
                ips=self.socmint_hits.get('ips', []),
                socials=self.socmint_hits.get('socials', [])
            )),
        ]
        for label, cmd in btn_defs:
            tk.Button(btn_row, text=label, command=cmd,
                     bg=self.colors['secondary'], fg='white',
                     padx=8, pady=4).pack(side='left', padx=6)

    def setup_person_hub_tab(self, notebook=None):
        parent = notebook if notebook is not None else self.notebook
        tab = ttk.Frame(parent)
        parent.add(tab, text="🎯 Person Hub")
        
        container = tk.Frame(tab, bg=self.colors['bg'])
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(container, text="🎯 Person Intelligence Hub", bg=self.colors['bg'], 
                 fg=self.colors['accent'], font=('Arial', 14, 'bold')).pack(anchor='w', pady=(0, 10))
        
        # Two columns for inputs and photo preview
        input_preview_frame = tk.Frame(container, bg=self.colors['bg'])
        input_preview_frame.pack(fill='x', pady=5)
        
        # Left: input fields
        inputs_frame = tk.Frame(input_preview_frame, bg=self.colors['bg'])
        inputs_frame.pack(side='left', fill='both', expand=True)
        
        tk.Label(inputs_frame, text="Full Name:", bg=self.colors['bg'], fg='white').grid(row=0, column=0, sticky='w', pady=4)
        self.person_name_entry = tk.Entry(inputs_frame, bg='#2d2d2d', fg='white', width=30)
        self.person_name_entry.grid(row=0, column=1, padx=10, pady=4, sticky='w')
        
        tk.Label(inputs_frame, text="Email Address:", bg=self.colors['bg'], fg='white').grid(row=1, column=0, sticky='w', pady=4)
        self.person_email_entry = tk.Entry(inputs_frame, bg='#2d2d2d', fg='white', width=30)
        self.person_email_entry.grid(row=1, column=1, padx=10, pady=4, sticky='w')
        
        tk.Label(inputs_frame, text="Username:", bg=self.colors['bg'], fg='white').grid(row=2, column=0, sticky='w', pady=4)
        self.person_username_entry = tk.Entry(inputs_frame, bg='#2d2d2d', fg='white', width=30)
        self.person_username_entry.grid(row=2, column=1, padx=10, pady=4, sticky='w')
        
        tk.Label(inputs_frame, text="Phone Number:", bg=self.colors['bg'], fg='white').grid(row=3, column=0, sticky='w', pady=4)
        self.person_phone_entry = tk.Entry(inputs_frame, bg='#2d2d2d', fg='white', width=30)
        self.person_phone_entry.grid(row=3, column=1, padx=10, pady=4, sticky='w')
        
        tk.Label(inputs_frame, text="Face Photo:", bg=self.colors['bg'], fg='white').grid(row=4, column=0, sticky='w', pady=4)
        photo_select_frame = tk.Frame(inputs_frame, bg=self.colors['bg'])
        photo_select_frame.grid(row=4, column=1, padx=10, pady=4, sticky='w')
        
        self.person_image_path_var = tk.StringVar()
        self.person_image_path_entry = tk.Entry(photo_select_frame, textvariable=self.person_image_path_var, bg='#2d2d2d', fg='white', width=20, state='readonly')
        self.person_image_path_entry.pack(side='left', padx=(0, 5))
        tk.Button(photo_select_frame, text="Browse...", command=self.browse_person_image, bg=self.colors['accent'], fg='white').pack(side='left')
        
        # Right: photo preview
        self.preview_frame = tk.LabelFrame(input_preview_frame, text="Face Photo Preview", bg=self.colors['bg'], fg=self.colors['accent'], width=150, height=150)
        self.preview_frame.pack(side='right', padx=(20, 0), fill='both', expand=False)
        self.preview_frame.pack_propagate(False)
        
        self.person_image_preview_label = tk.Label(self.preview_frame, text="No Image", bg='#1a1a1a', fg='gray')
        self.person_image_preview_label.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Progress & Status Frame
        progress_frame = tk.Frame(container, bg=self.colors['bg'])
        progress_frame.pack(fill='x', pady=10)
        
        self.person_progress_label = tk.Label(progress_frame, text="Waiting to launch investigation...", bg=self.colors['bg'], fg='white')
        self.person_progress_label.pack(anchor='w')
        
        self.person_progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.person_progress.pack(fill='x', pady=(4, 0))
        
        # Control Buttons
        btn_frame = tk.Frame(container, bg=self.colors['bg'])
        btn_frame.pack(fill='x', pady=5)
        
        tk.Button(btn_frame, text="🚀 Launch Investigation", command=self.start_person_investigation, bg=self.colors['secondary'], fg='white', font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        tk.Button(btn_frame, text="⏹️ Stop", command=self.stop_person_investigation, bg=self.colors['warning'], fg='white').pack(side='left', padx=5)
        tk.Button(btn_frame, text="📄 Generate HTML Dossier", command=self.generate_person_dossier, bg=self.colors['highlight'], fg='black').pack(side='left', padx=5)
        
        # Log Output Console
        self.person_log = scrolledtext.ScrolledText(container, bg='#1a1a1a', fg='#00ff00', font=('Consolas', 10))
        self.person_log.pack(fill='both', expand=True, pady=10)

    def browse_person_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Face Photo",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.webp *.bmp"), ("All Files", "*.*")]
        )
        if file_path:
            self.person_image_path_var.set(file_path)
            try:
                img = Image.open(file_path)
                img.thumbnail((140, 140))
                self.person_photo = ImageTk.PhotoImage(img)
                self.person_image_preview_label.config(image=self.person_photo, text="")
            except Exception as e:
                self.person_image_preview_label.config(image="", text="Preview Error")
                self.update_status(f"Error loading preview: {e}")

    def start_person_investigation(self):
        name = self.person_name_entry.get().strip()
        email = self.person_email_entry.get().strip()
        username = self.person_username_entry.get().strip()
        phone = self.person_phone_entry.get().strip()
        image_path = self.person_image_path_var.get().strip()
        
        if not (name or email or username or phone or image_path):
            messagebox.showwarning("Input Required", "Please fill in at least one field (Name, Email, Username, Phone, or Face Photo).")
            return
            
        keys = self.config_manager.load_keys()
        self.person_investigator = PersonInvestigator(
            keys=keys,
            callback=self.update_person_log,
            progress_callback=self.update_person_progress
        )
        
        if self.person_investigator.running:
            messagebox.showwarning("Warning", "An investigation is already running.")
            return
            
        self.person_log.delete(1.0, tk.END)
        self.person_progress['value'] = 0
        self.person_investigator.investigate(
            name=name,
            email=email,
            username=username,
            phone=phone,
            image_path=image_path
        )

    def stop_person_investigation(self):
        if hasattr(self, 'person_investigator'):
            self.person_investigator.stop()
            self.update_person_log("\n⏹️ Investigation stopped by user.")
            self.update_person_progress(0, 1, "Stopped.")

    def update_person_log(self, msg):
        self.root.after(0, self._append_person_log, msg)

    def _append_person_log(self, msg):
        self.person_log.insert(tk.END, msg + "\n")
        self.person_log.see(tk.END)

    def update_person_progress(self, step, total, label):
        self.root.after(0, self._set_person_progress, step, total, label)

    def _set_person_progress(self, step, total, label):
        pct = (step / total) * 100 if total > 0 else 0
        self.person_progress['value'] = pct
        self.person_progress_label.config(text=f"Step {step}/{total}: {label} ({pct:.1f}%)")

    def generate_person_dossier(self):
        if not hasattr(self, 'person_investigator') or not self.person_investigator.results:
            messagebox.showwarning("No Data", "Please run an investigation first to gather intelligence.")
            return
        try:
            name = self.person_name_entry.get().strip() or "Unknown Target"
            email = self.person_email_entry.get().strip() or "N/A"
            path = self.person_investigator.generate_html_dossier(name, email)
            messagebox.showinfo("Success", f"Dossier successfully generated at:\n{path}")
            webbrowser.open(path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate dossier:\n{e}")

    def setup_api_intelligence_tab(self, notebook=None):
        parent = notebook if notebook is not None else self.notebook
        tab = ttk.Frame(parent)
        parent.add(tab, text="🌐 API Intelligence")
        
        container = tk.Frame(tab, bg=self.colors['bg'])
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(container, text="Global API Intelligence Search", bg=self.colors['bg'], 
                fg=self.colors['accent'], font=('Arial', 14, 'bold')).pack(anchor='w', pady=(0, 10))
                
        input_frame = tk.Frame(container, bg=self.colors['bg'])
        input_frame.pack(fill='x', pady=10)
        
        tk.Label(input_frame, text="Target IP Address:", bg=self.colors['bg'], fg='white').pack(side='left')
        self.api_ip_entry = tk.Entry(input_frame, bg='#2d2d2d', fg='white', width=30)
        self.api_ip_entry.pack(side='left', padx=10)
        
        tk.Button(input_frame, text="🔍 Query Shodan & VT", command=self.run_api_queries, bg=self.colors['highlight'], fg='black').pack(side='left')
        
        # VirusTotal Expanded Section
        vt_frame = tk.Frame(container, bg=self.colors['bg'])
        vt_frame.pack(fill='x', pady=5)
        
        tk.Label(vt_frame, text="Scan URL / Domain / Hash:", bg=self.colors['bg'], fg='white').pack(side='left')
        self.vt_target_entry = tk.Entry(vt_frame, bg='#2d2d2d', fg='white', width=30)
        self.vt_target_entry.pack(side='left', padx=10)
        
        tk.Button(vt_frame, text="🌐 Scan URL", command=lambda: self.run_vt_expanded_scan('URL'), bg=self.colors['accent'], fg='white').pack(side='left', padx=5)
        tk.Button(vt_frame, text="🏠 Scan Domain", command=lambda: self.run_vt_expanded_scan('Domain'), bg=self.colors['accent'], fg='white').pack(side='left', padx=5)
        tk.Button(vt_frame, text="🔑 Scan Hash", command=lambda: self.run_vt_expanded_scan('Hash'), bg=self.colors['accent'], fg='white').pack(side='left', padx=5)
        tk.Button(vt_frame, text="🌐 DNS Lookup", command=self.run_dns_query, bg=self.colors['secondary'], fg='white').pack(side='left', padx=5)
        tk.Button(vt_frame, text="🔍 WHOIS Lookup", command=self.run_whois_query, bg=self.colors['secondary'], fg='white').pack(side='left', padx=5)
        
        self.api_log = scrolledtext.ScrolledText(container, bg='#1a1a1a', fg='#00ff00', font=('Consolas', 10))
        self.api_log.pack(fill='both', expand=True, pady=10)

    def run_api_queries(self):
        ip = self.api_ip_entry.get().strip()
        if not ip:
            messagebox.showwarning("Input Required", "Please enter an IP address.")
            return
            
        keys = self.config_manager.load_keys()
        shodan = ShodanEngine(keys.get('shodan', ''))
        vt = VirusTotalEngine(keys.get('virustotal', ''))
        
        self.api_log.delete(1.0, tk.END)
        self.api_log.insert(tk.END, f"--- Querying Intelligence for IP: {ip} ---\n\n")
        
        # Shodan
        self.api_log.insert(tk.END, "[*] Querying Shodan...\n")
        shodan_results = shodan.scan_ip(ip)
        if "error" in shodan_results:
            self.api_log.insert(tk.END, f"  -> Shodan Error: {shodan_results['error']}\n")
        else:
            self.api_log.insert(tk.END, f"  -> Org: {shodan_results.get('org')}\n")
            self.api_log.insert(tk.END, f"  -> OS: {shodan_results.get('os')}\n")
            self.api_log.insert(tk.END, f"  -> Open Ports: {shodan_results.get('ports')}\n")
            self.api_log.insert(tk.END, f"  -> Vulnerabilities: {shodan_results.get('vulns')}\n")
            
        # VirusTotal
        self.api_log.insert(tk.END, "\n[*] Querying VirusTotal...\n")
        vt_results = vt.scan_ip(ip)
        if "error" in vt_results:
            self.api_log.insert(tk.END, f"  -> VT Error: {vt_results['error']}\n")
        else:
            self.api_log.insert(tk.END, f"  -> Malicious: {vt_results.get('malicious')} flags\n")
            self.api_log.insert(tk.END, f"  -> Suspicious: {vt_results.get('suspicious')} flags\n")
            self.api_log.insert(tk.END, f"  -> Harmless: {vt_results.get('harmless')} flags\n")

    def _log_dns_answers(self, typ, ans):
        self.api_log.insert(tk.END, f"[{typ} Records]:\n")
        for r in ans:
            self.api_log.insert(tk.END, f"  -> {r.get('data')}\n")
        self.api_log.insert(tk.END, "\n")
        self.api_log.see(tk.END)

    def run_dns_query(self):
        domain = self.vt_target_entry.get().strip() or self.api_ip_entry.get().strip()
        if not domain:
            messagebox.showwarning("Input Required", "Enter a domain/IP in the Scan Target entry.")
            return
        domain = re.sub(r'https?://', '', domain).split('/')[0]
        self.api_log.delete(1.0, tk.END)
        self.api_log.insert(tk.END, f"--- DNS Resolution for {domain} (via Google DNS-over-HTTPS) ---\n\n")
        
        types = ['A', 'AAAA', 'MX', 'TXT', 'NS', 'CNAME']
        def worker():
            for t in types:
                try:
                    r = requests.get(f"https://dns.google/resolve?name={domain}&type={t}", timeout=10)
                    if r.status_code == 200:
                        data = r.json()
                        answers = data.get('Answer', [])
                        if answers:
                            self.root.after(0, lambda typ=t, ans=answers: self._log_dns_answers(typ, ans))
                        else:
                            self.root.after(0, lambda typ=t: self.api_log.insert(tk.END, f"[{typ}] No records found.\n"))
                except Exception as e:
                    self.root.after(0, lambda typ=t, err=e: self.api_log.insert(tk.END, f"[{typ}] Error: {err}\n"))
        threading.Thread(target=worker, daemon=True).start()

    def run_whois_query(self):
        domain = self.vt_target_entry.get().strip() or self.api_ip_entry.get().strip()
        if not domain:
            messagebox.showwarning("Input Required", "Enter a domain in the Scan Target entry.")
            return
        domain = re.sub(r'https?://', '', domain).split('/')[0]
        self.api_log.delete(1.0, tk.END)
        self.api_log.insert(tk.END, f"--- WHOIS Domain Query for {domain} (via RDAP keyless API) ---\n\n")
        
        def worker():
            try:
                r = requests.get(f"https://rdap.org/domain/{domain}", timeout=10)
                if r.status_code == 200:
                    data = r.json()
                    events = data.get('events', [])
                    created = "N/A"
                    updated = "N/A"
                    expires = "N/A"
                    for e in events:
                        action = e.get('eventAction', '')
                        date = e.get('eventDate', '')
                        if 'registration' in action: created = date
                        elif 'last update' in action: updated = date
                        elif 'expiration' in action: expires = date
                    
                    entities = data.get('entities', [])
                    registrar = "Unknown"
                    for ent in entities:
                        roles = ent.get('roles', [])
                        if 'registrar' in roles:
                            vcard = ent.get('vcardArray', [])
                            if len(vcard) > 1:
                                for attr in vcard[1]:
                                    if attr[0] == 'fn':
                                        registrar = attr[3]
                    
                    res_text = f"""
Domain Name: {domain.upper()}
Registrar: {registrar}
Created At: {created}
Updated At: {updated}
Expires At: {expires}
Status: {', '.join(data.get('status', ['Unknown']))}
"""
                    self.root.after(0, lambda txt=res_text: (self.api_log.insert(tk.END, txt + "\n"), self.api_log.see(tk.END)))
                elif r.status_code == 404:
                    self.root.after(0, lambda: self.api_log.insert(tk.END, "Domain not found in RDAP registry.\n"))
                else:
                    self.root.after(0, lambda sc=r.status_code: self.api_log.insert(tk.END, f"RDAP Query Error: {sc}\n"))
            except Exception as e:
                self.root.after(0, lambda err=e: self.api_log.insert(tk.END, f"WHOIS Query Error: {err}\n"))
        threading.Thread(target=worker, daemon=True).start()

    def run_vt_expanded_scan(self, scan_type):
        target = self.vt_target_entry.get().strip()
        if not target:
            messagebox.showwarning("Input Required", f"Please enter a target {scan_type} to scan.")
            return
            
        keys = self.config_manager.load_keys()
        vt_expanded = VirusTotalExpanded(keys.get('virustotal', ''))
        
        self.api_log.delete(1.0, tk.END)
        self.api_log.insert(tk.END, f"--- VirusTotal Expanded scan for {scan_type}: {target} ---\n\n")
        
        def run_thread():
            if scan_type == 'URL':
                # Check database first
                self.api_log.insert(tk.END, "[*] Checking database for URL...\n")
                results = vt_expanded.scan_url(target)
                if "error" in results and "Not found" in results["error"]:
                    self.api_log.insert(tk.END, "  [!] Not found in database. Submitting for fresh analysis...\n")
                    sub_res = vt_expanded.submit_url_for_analysis(target)
                    if sub_res.get("submitted"):
                        self.api_log.insert(tk.END, "  [+] Submitted successfully. Waiting 10s for analysis...\n")
                        import time
                        time.sleep(10)
                        results = vt_expanded.scan_url(target)
                
            elif scan_type == 'Domain':
                self.api_log.insert(tk.END, "[*] Scanning Domain...\n")
                results = vt_expanded.scan_domain(target)
            elif scan_type == 'Hash':
                self.api_log.insert(tk.END, "[*] Scanning File Hash...\n")
                results = vt_expanded.scan_hash(target)
            else:
                results = {"error": "Invalid scan type"}

            # Log results in the UI thread
            def update_ui():
                if "error" in results:
                    self.api_log.insert(tk.END, f"  -> Error: {results['error']}\n")
                else:
                    self.api_log.insert(tk.END, f"  -> Malicious: {results.get('malicious')} flags\n")
                    self.api_log.insert(tk.END, f"  -> Suspicious: {results.get('suspicious')} flags\n")
                    self.api_log.insert(tk.END, f"  -> Harmless: {results.get('harmless')} flags\n")
                    self.api_log.insert(tk.END, f"  -> Undetected: {results.get('undetected')} flags\n")
                    self.api_log.insert(tk.END, f"  -> Reputation Score: {results.get('reputation')}\n")
                    categories = results.get('categories', {})
                    if categories:
                        self.api_log.insert(tk.END, f"  -> Categories: {', '.join(set(categories.values()))}\n")
                    tags = results.get('tags', [])
                    if tags:
                        self.api_log.insert(tk.END, f"  -> Tags: {', '.join(tags)}\n")
            self.root.after(0, update_ui)
            
        threading.Thread(target=run_thread, daemon=True).start()

    def setup_settings_tab(self, parent_frame=None):
        """Setup settings tab"""
        parent = parent_frame if parent_frame is not None else self.notebook
        
        scroll_container = ScrollableFrame(parent)
        scroll_container.pack(fill='both', expand=True)
        
        container = tk.Frame(scroll_container.scrollable_frame, bg=self.colors['bg'])
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(container, text="API Key Configuration", bg=self.colors['bg'], 
                fg=self.colors['accent'], font=('Arial', 14, 'bold')).pack(anchor='w', pady=(0, 10))
                
        tk.Label(container, text="Shodan API Key:", bg=self.colors['bg'], fg='white').pack(anchor='w', pady=(10, 2))
        self.shodan_key_entry = tk.Entry(container, bg='#2d2d2d', fg='white', width=50, show="*")
        self.shodan_key_entry.pack(anchor='w')
        
        tk.Label(container, text="VirusTotal API Key:", bg=self.colors['bg'], fg='white').pack(anchor='w', pady=(10, 2))
        self.vt_key_entry = tk.Entry(container, bg='#2d2d2d', fg='white', width=50, show="*")
        self.vt_key_entry.pack(anchor='w')

        tk.Label(container, text="GitHub Personal Access Token (SOCMINT):", bg=self.colors['bg'], fg='white').pack(anchor='w', pady=(10, 2))
        self.github_key_entry = tk.Entry(container, bg='#2d2d2d', fg='white', width=50, show="*")
        self.github_key_entry.pack(anchor='w')

        tk.Label(container, text="Twitter/X Bearer Token (SOCMINT):", bg=self.colors['bg'], fg='white').pack(anchor='w', pady=(10, 2))
        self.twitter_key_entry = tk.Entry(container, bg='#2d2d2d', fg='white', width=50, show="*")
        self.twitter_key_entry.pack(anchor='w')

        tk.Label(container, text="2Captcha API Key (CAPTCHA Solver):", bg=self.colors['bg'], fg='white').pack(anchor='w', pady=(10, 2))
        self.captcha_key_entry = tk.Entry(container, bg='#2d2d2d', fg='white', width=50, show="*")
        self.captcha_key_entry.pack(anchor='w')

        tk.Label(container, text="HaveIBeenPwned (HIBP) API Key:", bg=self.colors['bg'], fg='white').pack(anchor='w', pady=(10, 2))
        self.hibp_key_entry = tk.Entry(container, bg='#2d2d2d', fg='white', width=50, show="*")
        self.hibp_key_entry.pack(anchor='w')

        tk.Label(container, text="Dehashed Account Email:", bg=self.colors['bg'], fg='white').pack(anchor='w', pady=(10, 2))
        self.dehashed_email_entry = tk.Entry(container, bg='#2d2d2d', fg='white', width=50)
        self.dehashed_email_entry.pack(anchor='w')

        tk.Label(container, text="Dehashed API Key:", bg=self.colors['bg'], fg='white').pack(anchor='w', pady=(10, 2))
        self.dehashed_key_entry = tk.Entry(container, bg='#2d2d2d', fg='white', width=50, show="*")
        self.dehashed_key_entry.pack(anchor='w')

        tk.Label(container, text="LeakCheck API Key:", bg=self.colors['bg'], fg='white').pack(anchor='w', pady=(10, 2))
        self.leakcheck_key_entry = tk.Entry(container, bg='#2d2d2d', fg='white', width=50, show="*")
        self.leakcheck_key_entry.pack(anchor='w')

        tk.Label(container, text="PimEyes API Key:", bg=self.colors['bg'], fg='white').pack(anchor='w', pady=(10, 2))
        self.pimeyes_key_entry = tk.Entry(container, bg='#2d2d2d', fg='white', width=50, show="*")
        self.pimeyes_key_entry.pack(anchor='w')

        tk.Label(container, text="FaceCheck.id API Token:", bg=self.colors['bg'], fg='white').pack(anchor='w', pady=(10, 2))
        self.facecheck_key_entry = tk.Entry(container, bg='#2d2d2d', fg='white', width=50, show="*")
        self.facecheck_key_entry.pack(anchor='w')
        
        # Load existing keys
        keys = self.config_manager.load_keys()
        if 'shodan' in keys: self.shodan_key_entry.insert(0, keys['shodan'])
        if 'virustotal' in keys: self.vt_key_entry.insert(0, keys['virustotal'])
        if 'github' in keys: self.github_key_entry.insert(0, keys['github'])
        if 'twitter' in keys: self.twitter_key_entry.insert(0, keys['twitter'])
        if '2captcha' in keys: self.captcha_key_entry.insert(0, keys['2captcha'])
        if 'hibp' in keys: self.hibp_key_entry.insert(0, keys['hibp'])
        if 'dehashed_email' in keys: self.dehashed_email_entry.insert(0, keys['dehashed_email'])
        if 'dehashed' in keys: self.dehashed_key_entry.insert(0, keys['dehashed'])
        if 'leakcheck' in keys: self.leakcheck_key_entry.insert(0, keys['leakcheck'])
        if 'pimeyes' in keys: self.pimeyes_key_entry.insert(0, keys['pimeyes'])
        if 'facecheck' in keys: self.facecheck_key_entry.insert(0, keys['facecheck'])
        
        tk.Button(container, text="💾 Save All API Keys", command=self.save_api_keys, bg=self.colors['highlight'], fg='black').pack(anchor='w', pady=(15, 0))

        # TOR Toggle
        tk.Label(container, text="🌐 Network Settings", bg=self.colors['bg'],
                fg=self.colors['accent'], font=('Arial', 12, 'bold')).pack(anchor='w', pady=(20, 5))
        self.tor_var = tk.BooleanVar(value=False)
        tor_cb = tk.Checkbutton(container, text="Route all traffic through TOR (requires TOR service on port 9050)",
                               variable=self.tor_var, command=self.toggle_tor,
                               bg=self.colors['bg'], fg=self.colors['highlight'], selectcolor='#2d2d2d',
                               font=('Arial', 10))
        tor_cb.pack(anchor='w')
        self.tor_status_label = tk.Label(container, text="TOR: Disabled", bg=self.colors['bg'], fg='gray')
        self.tor_status_label.pack(anchor='w', padx=20)
        tk.Button(container, text="🔄 Test TOR Connection", command=self.test_tor,
                 bg=self.colors['secondary'], fg='white').pack(anchor='w', padx=20, pady=5)

        # Settings options
        tk.Label(container, text="Application Settings", bg=self.colors['bg'], 
                fg=self.colors['accent'], font=('Arial', 14, 'bold')).pack(anchor='w', pady=(20, 20))
        
        # Auto-save
        self.auto_save_var = tk.BooleanVar(value=True)
        tk.Checkbutton(container, text="Auto-save generated dorks", 
                      variable=self.auto_save_var, bg=self.colors['bg'], 
                      fg='white', selectcolor='#2d2d2d').pack(anchor='w', pady=(0, 10))
        
        # Enable advanced operators
        self.advanced_ops_var = tk.BooleanVar(value=True)
        tk.Checkbutton(container, text="Enable advanced operators (intext, intitle, etc.)", 
                      variable=self.advanced_ops_var, bg=self.colors['bg'], 
                      fg='white', selectcolor='#2d2d2d').pack(anchor='w', pady=(0, 10))
        
        # Enable time filters
        self.time_filters_var = tk.BooleanVar(value=True)
        tk.Checkbutton(container, text="Enable time-based filtering", 
                      variable=self.time_filters_var, bg=self.colors['bg'], 
                      fg='white', selectcolor='#2d2d2d').pack(anchor='w', pady=(0, 10))
        
        # Enable safety warnings
        self.safety_warnings_var = tk.BooleanVar(value=True)
        tk.Checkbutton(container, text="Show safety warnings", 
                      variable=self.safety_warnings_var, bg=self.colors['bg'], 
                      fg='white', selectcolor='#2d2d2d').pack(anchor='w', pady=(0, 10))
        
        # Export settings
        tk.Label(container, text="Export Format:", bg=self.colors['bg'], 
                fg='white').pack(anchor='w', pady=(20, 5))
        
        self.export_format = tk.StringVar(value="txt")
        formats = [("Plain Text (.txt)", "txt"),
                  ("JSON (.json)", "json"),
                  ("CSV (.csv)", "csv"),
                  ("Markdown (.md)", "md")]
        
        for text, value in formats:
            rb = tk.Radiobutton(container, text=text, variable=self.export_format, 
                              value=value, bg=self.colors['bg'], fg='white',
                              selectcolor='#2d2d2d')
            rb.pack(anchor='w')
        
        # Save button
        tk.Button(container, text="💾 Save Settings", 
                 command=self.save_settings,
                 bg=self.colors['accent'], fg='white').pack(anchor='w', pady=(20, 0))

    def save_api_keys(self):
        keys = {
            'shodan': self.shodan_key_entry.get().strip(),
            'virustotal': self.vt_key_entry.get().strip(),
            'github': self.github_key_entry.get().strip(),
            'twitter': self.twitter_key_entry.get().strip(),
            '2captcha': self.captcha_key_entry.get().strip(),
            'hibp': self.hibp_key_entry.get().strip(),
            'dehashed_email': self.dehashed_email_entry.get().strip(),
            'dehashed': self.dehashed_key_entry.get().strip(),
            'leakcheck': self.leakcheck_key_entry.get().strip(),
            'pimeyes': self.pimeyes_key_entry.get().strip(),
            'facecheck': self.facecheck_key_entry.get().strip(),
        }
        import json
        config_file = os.path.join(os.path.dirname(__file__), 'api_config.json')
        with open(config_file, 'w') as f:
            json.dump(keys, f, indent=4)
        # Update captcha solver key
        self.captcha_solver.two_captcha_key = keys.get('2captcha', '')
        messagebox.showinfo("Success", "All API Keys have been saved locally.")
        self.update_status("API Keys updated.")

    def toggle_tor(self):
        if self.tor_var.get():
            TORRouter.enable()
            self.tor_status_label.config(text="TOR: ENABLED ✅", fg=self.colors['highlight'])
            self.update_status("TOR routing ENABLED.")
        else:
            TORRouter.disable()
            self.tor_status_label.config(text="TOR: Disabled", fg='gray')
            self.update_status("TOR routing disabled.")

    def test_tor(self):
        def _test():
            self.tor_status_label.config(text="TOR: Testing...", fg='white')
            is_tor, ip = TORRouter.check_tor()
            if is_tor:
                self.root.after(0, self.tor_status_label.config, {'text': f"TOR: Active ✅ | Exit IP: {ip}", 'fg': self.colors['highlight']})
            else:
                self.root.after(0, self.tor_status_label.config, {'text': f"TOR: FAILED ❌ ({ip})", 'fg': self.colors['warning']})
        threading.Thread(target=_test, daemon=True).start()

    def generate_dorks(self):
        """Generate dorks based on input parameters"""
        target = self.target_entry.get().strip()
        keywords = [k.strip() for k in self.keywords_entry.get().split(',') if k.strip()]
        intent = self.intent_combo.get()
        
        if not target and not keywords:
            messagebox.showwarning("Input Required", "Please enter target domain or keywords")
            return
        
        dorks = []
        
        # Base dork with target
        if target:
            if not target.startswith('http'):
                target = f'site:{target}'
            dorks.append(f'{target}')
        
        # Add keywords
        if keywords:
            keyword_dork = ' OR '.join([f'intext:"{k}"' for k in keywords])
            if target:
                dorks[-1] = f'{dorks[-1]} ({keyword_dork})'
            else:
                dorks.append(keyword_dork)
        
        # Add file types
        selected_files = [ft for ft, var in self.file_vars.items() if var.get()]
        if selected_files:
            file_type_map = {
                'PDF': 'filetype:pdf',
                'DOC/DOCX': 'filetype:doc OR filetype:docx',
                'XLS/XLSX': 'filetype:xls OR filetype:xlsx',
                'TXT': 'filetype:txt',
                'SQL': 'filetype:sql',
                'LOG': 'filetype:log',
                'JSON': 'filetype:json',
                'XML': 'filetype:xml'
            }
            file_dorks = [file_type_map[ft] for ft in selected_files]
            dorks.append(f'({" OR ".join(file_dorks)})')
        
        # Add time range
        time_map = {
            'day': 'daterange:2459580-2459581',
            'week': 'daterange:2459573-2459581',
            'month': 'daterange:2459550-2459581',
            'year': 'daterange:2459215-2459581'
        }
        time_range = self.time_var.get()
        if time_range != 'anytime' and time_range in time_map:
            dorks.append(time_map[time_range])
        
        # Add intent-specific patterns
        intent_patterns = {
            "Vulnerability Discovery": ['inurl:"id="', 'intext:"error"', 'intitle:"index of"'],
            "File Discovery": ['intitle:"index of"', 'intext:"parent directory"'],
            "Credentials Discovery": ['intext:"password"', 'intext:"username"', 'intext:"login"'],
            "Admin Panels": ['intitle:"admin"', 'inurl:"admin"', 'inurl:"dashboard"']
        }
        
        if intent in intent_patterns:
            dorks.extend(intent_patterns[intent])
        
        # Combine all dorks
        final_dork = ' '.join(dorks)
        
        # Display results
        self.dorks_text.delete(1.0, tk.END)
        self.dorks_text.insert(tk.END, final_dork)
        
        # Generate variations
        variations = self.generate_variations(final_dork)
        self.learning_stats_text.insert(tk.END, "\n--- Most Successful Dork Templates ---\n")
        for s in self.brain.knowledge.get('successful_combinations', [])[-10:]:
            self.learning_stats_text.insert(tk.END, f"{s['template']}\n")
        
        # Update preview
        self.update_preview(final_dork, variations)
        
        # Add to history
        self.add_to_history(final_dork, target, intent)
        
        self.update_status("Dorks generated successfully!")
    
    def generate_variations(self, base_dork):
        """Generate multiple dork variations"""
        variations = []
        
        # Variation 1: More specific
        variations.append(base_dork + ' -inurl:github -inurl:stackoverflow')
        
        # Variation 2: Different operator
        if 'intext:' in base_dork:
            variations.append(base_dork.replace('intext:', 'intitle:'))
        
        # Variation 3: Add cache operator
        variations.append('cache:' + base_dork.replace('site:', '').split()[0] if 'site:' in base_dork else base_dork)
        
        # Variation 4: With filetype variations
        if 'filetype:' not in base_dork:
            variations.append(base_dork + ' filetype:pdf OR filetype:doc')
        
        # Variation 5: With location restriction
        variations.append(base_dork + ' location:US')
        
        return variations
    
    def update_preview(self, dork, variations):
        """Update preview window with statistics"""
        word_count = len(dork.split())
        char_count = len(dork)
        variation_count = len(variations)
        
        preview_text = f"""
🔍 Generated Dork Preview:
{'-'*40}
📏 Length: {char_count} characters, {word_count} words
🔄 Variations: {variation_count}
🎯 Precision: {'High' if 'site:' in dork else 'Medium'}
📊 Estimated Results: {'100-1,000' if 'filetype:' in dork else '1,000-10,000'}

💡 Tips:
1. Start with the main dork first
2. Use variations for broader/narrower results
3. Add more keywords to narrow down
4. Use time filters for recent content
"""
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(tk.END, preview_text)
    
    def add_to_history(self, dork, target, intent):
        """Add search to history"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] {intent}: {dork[:50]}..."
        self.search_history.append((timestamp, dork, target, intent))
        self.history_listbox.insert(tk.END, entry)
    
    def update_pattern_list(self, event=None):
        """Update patterns list based on selected category"""
        category = self.pattern_cat_combo.get()
        self.patterns_listbox.delete(0, tk.END)
        
        if category in self.dork_patterns:
            for name, pattern in self.dork_patterns[category].items():
                self.patterns_listbox.insert(tk.END, f"{name}: {pattern}")
    
    def add_pattern_to_generator(self):
        """(Deprecated) kept for compatibility - use add_selected_patterns instead"""
        self.update_status("Use 'Add Selected to Patterns' button instead")

    def add_selected_patterns(self):
        """Add selected items from the patterns listbox into the selected-patterns listbox"""
        selections = self.patterns_listbox.curselection()
        if not selections:
            return
        for idx in selections:
            pattern_text = self.patterns_listbox.get(idx)
            # extract pattern after ': '
            parts = pattern_text.split(": ", 1)
            pattern = parts[1] if len(parts) > 1 else pattern_text
            # avoid duplicates
            existing = self.selected_patterns_listbox.get(0, tk.END)
            if pattern not in existing:
                self.selected_patterns_listbox.insert(tk.END, pattern)
        self.update_status("Selected patterns added")

    def add_custom_pattern(self):
        """Add a custom pattern string into the selected-patterns listbox"""
        pat = self.custom_pattern_entry.get().strip()
        if not pat:
            return
        existing = self.selected_patterns_listbox.get(0, tk.END)
        if pat not in existing:
            self.selected_patterns_listbox.insert(tk.END, pat)
        self.custom_pattern_entry.delete(0, tk.END)
        self.update_status("Custom pattern added")
    
    def generate_bulk_dorks(self):
        """Generate dorks for multiple domains"""
        domains_text = self.bulk_domains_text.get(1.0, tk.END).strip()
        template = self.template_entry.get().strip()
        
        if not domains_text:
            messagebox.showwarning("Input Required", "Please enter domains")
            return
        
        domains = [d.strip() for d in domains_text.split('\n') if d.strip()]
        
        self.bulk_results_text.delete(1.0, tk.END)
        
        for domain in domains:
            dork = template.replace('{domain}', domain)
            self.bulk_results_text.insert(tk.END, f"{dork}\n")
        
        self.update_status(f"Generated {len(domains)} bulk dorks")
    
    def copy_dorks(self):
        """Copy generated dorks to clipboard"""
        dorks = self.dorks_text.get(1.0, tk.END).strip()
        if dorks:
            pyperclip.copy(dorks)
            self.update_status("Dorks copied to clipboard!")
    
    def open_in_browser(self):
        """Open generated dorks in browser"""
        dorks = self.dorks_text.get(1.0, tk.END).strip()
        if not dorks:
            return
        
        # Take only the first dork (main one)
        main_dork = dorks.split('\n')[0].strip()
        if main_dork:
            encoded_dork = quote_plus(main_dork)
            url = f"https://www.google.com/search?q={encoded_dork}"
            webbrowser.open(url)
            self.update_status("Opened in browser")
    
    def save_dorks(self):
        """Save dorks to file"""
        dorks = self.dorks_text.get(1.0, tk.END).strip()
        if not dorks:
            return
        
        filename = f"dorks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(dorks)
        
        self.update_status(f"Dorks saved to {filename}")
    
    def add_to_favorites(self):
        """Add current dork to favorites"""
        dorks = self.dorks_text.get(1.0, tk.END).strip()
        if not dorks:
            return
        
        main_dork = dorks.split('\n')[0].strip()
        if main_dork:
            self.favorites_listbox.insert(tk.END, main_dork[:100])
            self.favorite_dorks.append(main_dork)
            self.update_status("Added to favorites")
    
    def test_dorks(self):
        """Test dorks in background thread"""
        self.update_status("Testing dorks...")
        threading.Thread(target=self._test_dorks_thread, daemon=True).start()
    
    def _test_dorks_thread(self):
        """Background thread to test dorks"""
        # This would contain actual testing logic
        # For now, just simulate
        import time
        time.sleep(2)
        self.root.after(0, lambda: self.update_status("Dork test completed (simulated)"))
    
    def clear_history(self):
        """Clear search history"""
        if messagebox.askyesno("Confirm", "Clear all history?"):
            self.history_listbox.delete(0, tk.END)
            self.search_history = []
            self.update_status("History cleared")
    
    def copy_selected_history(self):
        """Copy selected history item to clipboard"""
        selection = self.history_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.search_history):
                _, dork, _, _ = self.search_history[index]
                pyperclip.copy(dork)
                self.update_status("History item copied")
    
    def use_selected_dork(self):
        """Use selected history/favorite dork"""
        # Try history first
        selection = self.history_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.search_history):
                _, dork, _, _ = self.search_history[index]
                self.dorks_text.delete(1.0, tk.END)
                self.dorks_text.insert(tk.END, dork)
                self.update_status("History dork loaded")
                return
        
        # Try favorites
        selection = self.favorites_listbox.curselection()
        if selection:
            dork = self.favorites_listbox.get(selection[0])
            self.dorks_text.delete(1.0, tk.END)
            self.dorks_text.insert(tk.END, dork)
            self.update_status("Favorite dork loaded")
    
    def save_settings(self):
        """Save application settings"""
        settings = {
            'auto_save': self.auto_save_var.get(),
            'advanced_ops': self.advanced_ops_var.get(),
            'time_filters': self.time_filters_var.get(),
            'safety_warnings': self.safety_warnings_var.get(),
            'export_format': self.export_format.get()
        }
        
        with open('dork_generator_settings.json', 'w') as f:
            json.dump(settings, f)
        
        self.update_status("Settings saved")
    
    def update_ghdb(self):
        """Fetch latest GHDB patterns from remote repo in background thread."""
        self.update_status("Fetching GHDB patterns...")
        def _worker():
            try:
                count = GHDBUpdater.update_patterns(self.brain)
                self.root.after(0, lambda: (
                    self.update_status(f"GHDB Updated: {count} new patterns added."),
                    messagebox.showinfo("GHDB Updated", f"Successfully imported {count} new dork patterns from GHDB.")
                ))
            except Exception as e:
                self.root.after(0, lambda: (
                    self.update_status(f"GHDB update failed: {e}"),
                    messagebox.showerror("GHDB Error", f"Failed to fetch GHDB patterns:\n{e}")
                ))
        threading.Thread(target=_worker, daemon=True).start()

    def refresh_learning_tab(self):
        """Refresh the Brain tab with latest knowledge stats."""
        if not hasattr(self, 'learning_stats_text'):
            return
        self.learning_stats_text.delete(1.0, tk.END)
        weights = self.brain.knowledge.get('pattern_weights', {})
        combos = self.brain.knowledge.get('successful_combinations', [])
        self.learning_stats_text.insert(tk.END, f"📊 DorkBrain Status\n{'='*40}\n")
        self.learning_stats_text.insert(tk.END, f"  Learned patterns: {len(weights)}\n")
        self.learning_stats_text.insert(tk.END, f"  Successful dorks: {len(combos)}\n\n")
        if weights:
            top = sorted(weights.items(), key=lambda x: x[1], reverse=True)[:20]
            self.learning_stats_text.insert(tk.END, "🏆 Top Weighted Patterns:\n")
            for pattern, score in top:
                self.learning_stats_text.insert(tk.END, f"  [{score:.2f}] {pattern}\n")
        if combos:
            self.learning_stats_text.insert(tk.END, "\n--- Most Successful Dork Templates ---\n")
            for s in combos[-10:]:
                dork = s.get('dork', s.get('template', ''))
                self.learning_stats_text.insert(tk.END, f"  {dork}\n")

    def update_status(self, message):
        """Update status bar"""
        self.status_bar.config(text=f"Status: {message}")
        self.root.after(3000, lambda: self.status_bar.config(text="Ready"))

def main():
    root = tk.Tk()
    app = AdvancedDorkGenerator(root)
    # Center window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    # Set window icon (if available)
    try:
        root.iconbitmap('icon.ico')
    except Exception:
        pass
    root.mainloop()

if __name__ == "__main__":
    main()