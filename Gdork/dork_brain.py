import json
import os
from collections import defaultdict

class DorkBrain:
    def __init__(self, db_path='dork_brain.json'):
        self.db_path = db_path
        self.knowledge = {
            'pattern_weights': defaultdict(lambda: 1.0),
            'operator_weights': defaultdict(lambda: 1.0),
            'successful_combinations': []
        }
        self.load_brain()

    def load_brain(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Update pattern weights
                    p_weights = data.get('pattern_weights', {})
                    for k, v in p_weights.items():
                        self.knowledge['pattern_weights'][k] = float(v)
                        
                    # Update operator weights
                    o_weights = data.get('operator_weights', {})
                    for k, v in o_weights.items():
                        self.knowledge['operator_weights'][k] = float(v)
                        
                    # Update successful combinations
                    self.knowledge['successful_combinations'] = data.get('successful_combinations', [])
            except Exception as e:
                print(f"Error loading brain: {e}")

    def save_brain(self):
        try:
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'pattern_weights': dict(self.knowledge['pattern_weights']),
                    'operator_weights': dict(self.knowledge['operator_weights']),
                    'successful_combinations': self.knowledge['successful_combinations']
                }, f, indent=4)
        except Exception as e:
            print(f"Error saving brain: {e}")

    def register_success(self, dork, target=None, intent=None, components=None):
        """Increase the weight of patterns and components in a successful dork"""
        # Add to successful combinations list
        entry = {
            'dork': dork,
            'target': target,
            'intent': intent,
            'timestamp': os.environ.get('CURRENT_TIME', '')
        }
        self.knowledge['successful_combinations'].append(entry)

        # If components used to generate this dork are passed, weight them directly
        if components:
            for comp in components:
                self.knowledge['pattern_weights'][comp] += 0.5
        else:
            # Extract operators and patterns heuristically
            operators = ['inurl:', 'intitle:', 'intext:', 'ext:', 'filetype:', 'site:']
            words = dork.split()
            for w in words:
                found_op = False
                for op in operators:
                    if w.lower().startswith(op):
                        self.knowledge['operator_weights'][op] += 0.2
                        self.knowledge['pattern_weights'][w] += 0.5
                        found_op = True
                        break
                if not found_op:
                    # Generic keyword
                    self.knowledge['pattern_weights'][w] += 0.1
        
        self.save_brain()

    def get_weight(self, pattern):
        """Get the weight of a pattern, defaulting to 1.0"""
        return self.knowledge['pattern_weights'].get(pattern, 1.0)

    def register_failure(self, dork):
        """Slightly decrease the weight of patterns in a failed dork."""
        words = dork.split()
        operators = ['inurl:', 'intitle:', 'intext:', 'ext:', 'filetype:', 'site:']
        for w in words:
            for op in operators:
                if w.lower().startswith(op):
                    # Decrease weight but never below 0.1
                    current = self.knowledge['pattern_weights'].get(w, 1.0)
                    self.knowledge['pattern_weights'][w] = max(0.1, current - 0.1)
                    break
        self.save_brain()