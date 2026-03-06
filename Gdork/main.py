import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import webbrowser
import json
import re
import pyperclip
from datetime import datetime
import threading
from urllib.parse import quote_plus

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

        tk.Button(btn_frame, text="Export TXT", command=export_txt, bg=self.colors['accent'], fg='white').pack(side='left', padx=8)
        tk.Button(btn_frame, text="Export CSV", command=export_csv, bg=self.colors['accent'], fg='white').pack(side='left', padx=8)
        tk.Button(btn_frame, text="Copy All", command=copy, bg=self.colors['secondary'], fg='white').pack(side='left', padx=8)
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
        """Setup the main GUI interface"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.setup_dork_generator_tab()
        self.setup_advanced_search_tab()
        self.setup_automation_tab()
        self.setup_history_tab()
        self.setup_settings_tab()
        
        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready", bg=self.colors['accent'], 
                                 fg='white', anchor='w', relief='sunken')
        self.status_bar.pack(side='bottom', fill='x')
    
    def setup_dork_generator_tab(self):
        """Setup the main dork generation tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🧠 Dork Generator")
        
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
        
    def setup_advanced_search_tab(self):
        """Setup advanced search patterns tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="⚡ Advanced Patterns")
        
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
             bg=self.colors['accent'], fg='white').pack(fill='x')
    
    def setup_automation_tab(self):
        """Setup automation and bulk search tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🤖 Automation")
        
        container = tk.Frame(tab, bg=self.colors['bg'])
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Bulk domain input
        tk.Label(container, text="Bulk Domains (one per line):", 
                bg=self.colors['bg'], fg='white').pack(anchor='w')
        
        self.bulk_domains_text = scrolledtext.ScrolledText(container, height=8, 
                                                          bg='#2d2d2d', fg='white')
        self.bulk_domains_text.pack(fill='x', pady=(0, 10))
        
        # Dork template
        tk.Label(container, text="Dork Template (use {domain} for domain placeholder):", 
                bg=self.colors['bg'], fg='white').pack(anchor='w')
        
        self.template_entry = tk.Entry(container, bg='#2d2d2d', fg='white')
        self.template_entry.pack(fill='x', pady=(0, 10))
        self.template_entry.insert(0, 'site:{domain} inurl:admin')
        
        # Generate bulk button
        tk.Button(container, text="🔧 Generate Bulk Dorks", 
                 command=self.generate_bulk_dorks,
                 bg=self.colors['accent'], fg='white').pack(fill='x', pady=(0, 10))
        
        # Results area
        tk.Label(container, text="Generated Bulk Dorks:", 
                bg=self.colors['bg'], fg='white').pack(anchor='w')
        
        self.bulk_results_text = scrolledtext.ScrolledText(container, height=10, 
                                                          bg='#2d2d2d', fg='white')
        self.bulk_results_text.pack(fill='both', expand=True)
    
    def setup_history_tab(self):
        """Setup search history tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📚 History & Favorites")
        
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
    
    def setup_settings_tab(self):
        """Setup settings tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="⚙️ Settings")
        
        container = tk.Frame(tab, bg=self.colors['bg'])
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Settings options
        tk.Label(container, text="Application Settings", bg=self.colors['bg'], 
                fg=self.colors['accent'], font=('Arial', 14, 'bold')).pack(anchor='w', pady=(0, 20))
        
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
        self.dorks_text.insert(tk.END, "\n\n--- Variations ---\n")
        for i, var in enumerate(variations[:5], 1):
            self.dorks_text.insert(tk.END, f"\n{i}. {var}")
        
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
    
    def update_status(self, message):
        """Update status bar"""
        self.status_bar.config(text=f"Status: {message}")
        self.root.after(3000, lambda: self.status_bar.config(text="Ready"))

def main():
    print("[DEBUG] Before creating Tk window")
    root = tk.Tk()
    print("[DEBUG] Tk window created")
    app = AdvancedDorkGenerator(root)
    print("[DEBUG] AdvancedDorkGenerator initialized")
    # Center window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    print("[DEBUG] Window geometry set")
    # Set window icon (if available)
    try:
        root.iconbitmap('icon.ico')
    except Exception as e:
        print(f"[DEBUG] Icon error: {e}")
    print("[DEBUG] Entering mainloop")
    root.mainloop()
    print("[DEBUG] mainloop exited")

if __name__ == "__main__":
    main()