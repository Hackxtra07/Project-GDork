#!/usr/bin/env python3
"""
SMART HUMAN PASSWORD GENERATOR - GUI Version
Generates realistic password patterns that humans would actually create
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import sys
from datetime import datetime
import os
import re
import itertools
import random
from typing import Set, Dict, List, Tuple
from collections import defaultdict
import threading

class SmartHumanPasswordGenerator:
    def __init__(self):
        # Common human password patterns - these are patterns REAL people use
        self.human_patterns = [
            # EXTENSIVE HUMAN PASSWORD PATTERNS - Name & Date Combinations
            # ==================== BASIC NAME + DATE COMBINATIONS ====================
            "{first}{last}",
            "{last}{first}",
            "{first}{year}",
            "{last}{year}",
            "{first}{year_short}",
            "{last}{year_short}",
            "{first}{day}{month}",
            "{last}{day}{month}",
            "{first}{month}{year}",
            "{last}{month}{year}",
            "{first}{day}{month}{year}",
            "{last}{day}{month}{year}",
            "{first}{month}{day}{year}",
            "{last}{month}{day}{year}",
            "{first}{year}{month}{day}",
            "{last}{year}{month}{day}",
            "{first}{last}{year}",
            "{last}{first}{year}",
            "{first}{last}{year_short}",
            "{last}{first}{year_short}",
            "{first}{last}{day}{month}",
            "{last}{first}{day}{month}",
            "{first}{last}{month}{year}",
            "{last}{first}{month}{year}",
            "{first}{last}{day}{month}{year}",
            "{last}{first}{day}{month}{year}",
            "{first}{last}{month}{day}{year}",
            "{last}{first}{month}{day}{year}",
            "{first}{last}{year}{month}{day}",
            "{last}{first}{year}{month}{day}",
    
            # ==================== WITH INITIALS ====================
            "{first_initial}{last}{year}",
            "{first}{last_initial}{year}",
            "{first_initial}{last_initial}{year}",
            "{first_initial}{last}{year_short}",
            "{first}{last_initial}{year_short}",
            "{first_initial}{last_initial}{year_short}",
            "{first_initial}{last}{day}{month}",
            "{first}{last_initial}{day}{month}",
            "{first_initial}{last_initial}{day}{month}",
            "{first_initial}{last}{month}{year}",
            "{first}{last_initial}{month}{year}",
            "{first_initial}{last_initial}{month}{year}",
            "{first_initial}{last}{day}{month}{year}",
            "{first}{last_initial}{day}{month}{year}",
            "{first_initial}{last_initial}{day}{month}{year}",
    
            # ==================== REVERSED DATE PATTERNS ====================
            "{first}{last}{day}{month}{year_short}",
            "{last}{first}{day}{month}{year_short}",
            "{first}{last}{month}{day}{year_short}",
            "{last}{first}{month}{day}{year_short}",
            "{first}{last}{year_short}{day}{month}",
            "{last}{first}{year_short}{day}{month}",
            "{first}{last}{year_short}{month}{day}",
            "{last}{first}{year_short}{month}{day}",
            "{first}{last}{day}{year_short}",
            "{last}{first}{day}{year_short}",
            "{first}{last}{month}{year_short}",
            "{last}{first}{month}{year_short}",
    
            # ==================== DAY-FOCUSED ====================
            "{first}{last}{day}",
            "{last}{first}{day}",
            "{first}{last}{day}{day}",  # Double day
            "{last}{first}{day}{day}",
            "{first}{last}{birth_day}",
            "{last}{first}{birth_day}",
            "{first}{last}{birth_day}{birth_day}",
            "{last}{first}{birth_day}{birth_day}",
            "{first}{day}{last}",
            "{last}{day}{first}",
            "{day}{first}{last}",
            "{day}{last}{first}",
            "{first}{last}{day}123",
            "{last}{first}{day}123",
    
            # ==================== MONTH-FOCUSED ====================
            "{first}{last}{month}",
            "{last}{first}{month}",
            "{first}{last}{birth_month}",
            "{last}{first}{birth_month}",
            "{first}{last}{month}{month}",  # Double month
            "{last}{first}{month}{month}",
            "{first}{month}{last}",
            "{last}{month}{first}",
            "{month}{first}{last}",
            "{month}{last}{first}",
            "{first}{last}{month_name}",
            "{last}{first}{month_name}",
            "{first}{last}{month_name_short}",
            "{last}{first}{month_name_short}",
    
            # ==================== YEAR-FOCUSED ====================
            "{first}{last}{year}",
            "{last}{first}{year}",
            "{first}{last}{year_short}",
            "{last}{first}{year_short}",
            "{first}{last}{birth_year}",
            "{last}{first}{birth_year}",
            "{first}{last}{year}{year}",  # Double year
            "{last}{first}{year}{year}",
            "{first}{year}{last}",
            "{last}{year}{first}",
            "{year}{first}{last}",
            "{year}{last}{first}",
            "{first}{year_short}{last}",
            "{last}{year_short}{first}",
            "{year_short}{first}{last}",
            "{year_short}{last}{first}",
    
            # ==================== SPECIAL DATE COMBOS ====================
            "{first}{last}{day}{month}{year_short}",
            "{last}{first}{day}{month}{year_short}",
            "{first}{last}{month}{day}{year_short}",
            "{last}{first}{month}{day}{year_short}",
            "{first}{last}{year_short}{month}{day}",
            "{last}{first}{year_short}{month}{day}",
            "{first}{last}{year_short}{day}{month}",
            "{last}{first}{year_short}{day}{month}",
    
            # ==================== WITH COMMON NUMBERS ====================
            "{first}{last}{year}123",
            "{last}{first}{year}123",
            "{first}{last}{year_short}123",
            "{last}{first}{year_short}123",
            "{first}{last}{day}123",
            "{last}{first}{day}123",
            "{first}{last}{month}123",
            "{last}{first}{month}123",
            "{first}{last}{year}007",
            "{last}{first}{year}007",
            "{first}{last}{year}111",
            "{last}{first}{year}111",
            "{first}{last}{year}999",
            "{last}{first}{year}999",
    
            # ==================== WITH SEPARATORS ====================
            "{first}.{last}{year}",
            "{first}_{last}{year}",
            "{first}-{last}{year}",
            "{first}@{last}{year}",
            "{first}.{last}{year_short}",
            "{first}_{last}{year_short}",
            "{first}-{last}{year_short}",
            "{first}@{last}{year_short}",
            "{first}.{last}{day}{month}",
            "{first}_{last}{day}{month}",
            "{first}-{last}{day}{month}",
            "{first}@{last}{day}{month}",
            "{first}.{last}{month}{year}",
            "{first}_{last}{month}{year}",
            "{first}-{last}{month}{year}",
            "{first}@{last}{month}{year}",
    
            # ==================== SPECIAL CHARACTER INSIDE ====================
            "{first}{special}{last}{year}",
            "{last}{special}{first}{year}",
            "{first}{special}{last}{year_short}",
            "{last}{special}{first}{year_short}",
            "{first}{special}{last}{day}{month}",
            "{last}{special}{first}{day}{month}",
            "{first}{special}{last}{month}{year}",
            "{last}{special}{first}{month}{year}",
            "{first}{last}{special}{year}",
            "{last}{first}{special}{year}",
            "{first}{last}{special}{year_short}",
            "{last}{first}{special}{year_short}",
    
            # ==================== SPECIAL CHARACTER AT ENDS ====================
            "{special}{first}{last}{year}",
            "{special}{last}{first}{year}",
            "{first}{last}{year}{special}",
            "{last}{first}{year}{special}",
            "{special}{first}{last}{year_short}",
            "{special}{last}{first}{year_short}",
            "{first}{last}{year_short}{special}",
            "{last}{first}{year_short}{special}",
            "{special}{first}{last}{special}{year}",
            "{special}{last}{first}{special}{year}",
    
            # ==================== NICKNAME + DATE ====================
            "{nick}{year}",
            "{nick}{year_short}",
            "{nick}{day}",
            "{nick}{month}",
            "{nick}{day}{month}",
            "{nick}{month}{day}",
            "{nick}{day}{month}{year}",
            "{nick}{month}{day}{year}",
            "{nick}{year}{day}{month}",
            "{nick}{year}{month}{day}",
            "{nick}{birth_day}",
            "{nick}{birth_month}",
            "{nick}{birth_year}",
            "{nick}{birth_day}{birth_month}",
            "{nick}{birth_month}{birth_year}",
            "{nick}{birth_day}{birth_year}",
    
            # ==================== FIRST NAME ONLY + DATE ====================
            "{first}{year}",
            "{first}{year_short}",
            "{first}{day}",
            "{first}{month}",
            "{first}{day}{month}",
            "{first}{month}{day}",
            "{first}{day}{month}{year}",
            "{first}{month}{day}{year}",
            "{first}{year}{day}{month}",
            "{first}{year}{month}{day}",
            "{first}{birth_day}",
            "{first}{birth_month}",
            "{first}{birth_year}",
            "{first}{birth_day}{birth_month}",
            "{first}{birth_month}{birth_year}",
            "{first}{birth_day}{birth_year}",
    
            # ==================== LAST NAME ONLY + DATE ====================
            "{last}{year}",
            "{last}{year_short}",
            "{last}{day}",
            "{last}{month}",
            "{last}{day}{month}",
            "{last}{month}{day}",
            "{last}{day}{month}{year}",
            "{last}{month}{day}{year}",
            "{last}{year}{day}{month}",
            "{last}{year}{month}{day}",
            "{last}{birth_day}",
            "{last}{birth_month}",
            "{last}{birth_year}",
            "{last}{birth_day}{birth_month}",
            "{last}{birth_month}{birth_year}",
            "{last}{birth_day}{birth_year}",
    
            # ==================== INITIALS + DATE ====================
            "{first_initial}{last}{year}",
            "{first}{last_initial}{year}",
            "{first_initial}{last_initial}{year}",
            "{first_initial}{last}{year_short}",
            "{first}{last_initial}{year_short}",
            "{first_initial}{last_initial}{year_short}",
            "{first_initial}{last}{day}{month}",
            "{first}{last_initial}{day}{month}",
            "{first_initial}{last_initial}{day}{month}",
            "{first_initial}{last}{month}{year}",
            "{first}{last_initial}{month}{year}",
            "{first_initial}{last_initial}{month}{year}",
    
            # ==================== DATE FIRST, NAME SECOND ====================
            "{year}{first}{last}",
            "{year}{last}{first}",
            "{year_short}{first}{last}",
            "{year_short}{last}{first}",
            "{day}{month}{first}{last}",
            "{day}{month}{last}{first}",
            "{month}{day}{first}{last}",
            "{month}{day}{last}{first}",
            "{year}{month}{first}{last}",
            "{year}{month}{last}{first}",
            "{month}{year}{first}{last}",
            "{month}{year}{last}{first}",
            "{day}{year}{first}{last}",
            "{day}{year}{last}{first}",
    
            # ==================== MIXED ORDER ====================
            "{first}{year}{last}",
            "{last}{year}{first}",
            "{first}{year_short}{last}",
            "{last}{year_short}{first}",
            "{first}{day}{last}{month}",
            "{last}{month}{first}{day}",
            "{first}{month}{last}{day}",
            "{last}{day}{first}{month}",
            "{first}{year}{last}{day}",
            "{last}{year}{first}{month}",
    
            # ==================== WITH ZERO-PADDED DATES ====================
            "{first}{last}{day_padded}{month_padded}",
            "{last}{first}{day_padded}{month_padded}",
            "{first}{last}{month_padded}{day_padded}",
            "{last}{first}{month_padded}{day_padded}",
            "{first}{last}{day_padded}{month_padded}{year}",
            "{last}{first}{day_padded}{month_padded}{year}",
            "{first}{last}{month_padded}{day_padded}{year}",
            "{last}{first}{month_padded}{day_padded}{year}",
    
            # ==================== WITH DATE FORMAT VARIATIONS ====================
            "{first}{last}{month}/{day}/{year_short}",
            "{last}{first}{month}/{day}/{year_short}",
            "{first}{last}{day}-{month}-{year}",
            "{last}{first}{day}-{month}-{year}",
            "{first}{last}{year}-{month}-{day}",
            "{last}{first}{year}-{month}-{day}",
            "{first}{last}{month}.{day}.{year}",
            "{last}{first}{month}.{day}.{year}",
    
            # ==================== DOUBLE/TRIPLE DATE ELEMENTS ====================
            "{first}{last}{day}{day}",
            "{last}{first}{day}{day}",
            "{first}{last}{month}{month}",
            "{last}{first}{month}{month}",
            "{first}{last}{year}{year}",
            "{last}{first}{year}{year}",
            "{first}{last}{day}{day}{month}",
            "{last}{first}{day}{day}{month}",
            "{first}{last}{month}{month}{year}",
            "{last}{first}{month}{month}{year}",
            "{first}{last}{year}{year}{day}",
            "{last}{first}{year}{year}{day}",
    
            # ==================== WITH MONTH NAMES ====================
            "{first}{last}{month_name}{year}",
            "{last}{first}{month_name}{year}",
            "{first}{last}{month_name_short}{year}",
            "{last}{first}{month_name_short}{year}",
            "{first}{last}{month_name}{year_short}",
            "{last}{first}{month_name}{year_short}",
            "{first}{last}{month_name_short}{year_short}",
            "{last}{first}{month_name_short}{year_short}",
            "{first}{last}{day}{month_name}",
            "{last}{first}{day}{month_name}",
            "{first}{last}{day}{month_name_short}",
            "{last}{first}{day}{month_name_short}",
    
            # ==================== PARENTHESIS/BRACKET STYLE ====================
            "{first}{last}({year})",
            "{last}{first}({year})",
            "{first}{last}[{year}]",
            "{last}{first}[{year}]",
            "{first}{last}{{{year}}}",
            "{last}{first}{{{year}}}",
            "{first}{last}({year_short})",
            "{last}{first}({year_short})",
            "{first}{last}[{year_short}]",
            "{last}{first}[{year_short}]",
    
            # ==================== WITH SUFFIXES ====================
            "{first}{last}{year}1",
            "{last}{first}{year}1",
            "{first}{last}{year}01",
            "{last}{first}{year}01",
            "{first}{last}{year}001",
            "{last}{first}{year}001",
            "{first}{last}{year}!",
            "{last}{first}{year}!",
            "{first}{last}{year}@",
            "{last}{first}{year}@",
            "{first}{last}{year}#",
            "{last}{first}{year}#",
    
            # ==================== SIMPLE VARIATIONS ====================
            "{first}{last}",
            "{last}{first}",
            "{first}{year}{last}",
            "{year}{first}{last}",
    
            # ==================== REPEATED ELEMENTS ====================
            "{first}{last}{first}{year}",
            "{last}{first}{last}{year}",
            "{first}{first}{last}{year}",
            "{last}{last}{first}{year}",
    
            # ==================== FAMILY DATE COMBINATIONS ====================
            "{first}{spouse_initial}{year}",
            "{spouse_initial}{first}{year}",
            "{first}{child_initial}{year}",
            "{child_initial}{first}{year}",
            "{first}{pet_initial}{year}",
            "{pet_initial}{first}{year}",
    
            # ==================== REPEATED ELEMENTS ====================
            "{first}{last}{first}{year}",
            "{last}{first}{last}{year}",
            "{first}{first}{last}{year}",
            "{last}{last}{first}{year}",
            "{first}{last}{last}{year}",
            "{last}{first}{first}{year}",
            "{first}{last}{first}{year_short}",
            "{last}{first}{last}{year_short}",
            "{first}{first}{last}{year_short}",
            "{last}{last}{first}{year_short}",
    
            # ==================== FAMILY DATE COMBINATIONS ====================
            "{first}{spouse_initial}{year}",
            "{spouse_initial}{first}{year}",
            "{first}{child_initial}{year}",
            "{child_initial}{first}{year}",
            "{first}{pet_initial}{year}",
            "{pet_initial}{first}{year}",
            "{first}{father_initial}{year}",
            "{father_initial}{first}{year}",
            "{first}{mother_initial}{year}",
            "{mother_initial}{first}{year}",
    
            
            # Nickname patterns
            "{nick}{year}",
            "{nick}{birth_day}",
            "{nick}{birth_month}",
            "{nick}{birth_day}{birth_month}",
            
            # Reversed patterns
            "{last}{first}{year_short}",
            "{year}{first}{last}",
            
            # With special characters
            "{first}.{last}{year_short}",
            "{first}_{last}{year}",
            "{first}{special}{last}{year}",
            "{first}{last}{special}{year}",
            
            # Common number patterns humans use
            "{first}{last}123",
            "{first}{last}1234",
            "{first}{last}12345",
            "{first}{last}!",
            "{first}{last}!!",
            "{first}{last}?",
            
            # Family combinations
            "{first}{spouse_initial}{year}",
            "{child_name}{year}",
            "{pet_name}{year}",
            
            # Simple patterns
            "{first}{birth_day}",
            "{last}{birth_month}",
            "{first_initial}{last_initial}{year}",
            
            # Mixed patterns
            "{first}{year}{last}",
            "{year}{first}{year_short}",
            
            # ==================== INTEREST-BASED PATTERNS ====================
            # Movie/Entertainment patterns
            "{movie}",
            "{movie}{year}",
            "{movie}{year_short}",
            "{first}{movie}",
            "{movie}{first}",
            "{first}{movie}{year}",
            "{movie}{first}{year}",
            
            # Music/Artist patterns
            "{music}",
            "{music}{year}",
            "{music}{year_short}",
            "{first}{music}",
            "{music}{first}",
            "{first}{music}{year}",
            "{music}{first}{year}",
            
            # Game/Character patterns
            "{game}",
            "{game}{year}",
            "{game}{year_short}",
            "{first}{game}",
            "{game}{first}",
            "{first}{game}{year}",
            "{game}{first}{year}",
            
            # Book/Author patterns
            "{book}",
            "{book}{year}",
            "{book}{year_short}",
            "{first}{book}",
            "{book}{first}",
            "{first}{book}{year}",
            "{book}{first}{year}",
            
            # Sport/Team patterns
            "{sport}",
            "{sport}{year}",
            "{team}",
            "{team}{year}",
            "{first}{sport}",
            "{sport}{first}",
            "{first}{team}",
            "{team}{first}",
            "{sport}{year_short}",
            "{team}{year_short}",
            
            # Celebrity patterns
            "{celebrity}",
            "{celebrity}{year}",
            "{first}{celebrity}",
            "{celebrity}{first}",
            
            # Place/Travel patterns
            "{place}",
            "{place}{year}",
            "{first}{place}",
            "{place}{first}",
            
            # Hobby patterns
            "{hobby}",
            "{hobby}{year}",
            "{first}{hobby}",
            "{hobby}{first}",
            
            # Combined interest patterns
            "{first}{movie}{year_short}",
            "{first}{sport}{year_short}",
            "{first}{game}{year_short}",
            "{movie}{year}{first}",
            "{sport}{year}{first}",
            "{game}{year}{first}",
            "{first}{music}{day}{month}",
            "{first}{game}{day}{month}",
            "{music}{day}{month}{year}",
            "{game}{day}{month}{year}",
            
            # Interest with special characters
            "{first}{special}{movie}",
            "{first}{special}{sport}",
            "{movie}{special}{year}",
            "{sport}{special}{year}",
            
            # Interest with numbers
            "{movie}123",
            "{sport}123",
            "{game}123",
            "{music}123",
            "{book}123",
            "{celebrity}123",
            "{place}123",
            "{hobby}123",
            ]
        
        # Common special characters humans actually use
        self.common_specials = ['!', '@', '#', '$', '%', '&', '*', '_', '.', '-']
        
        # Common number patterns (not random - what people actually use)
        self.common_numbers = [
            '123', '1234', '12345', '123456',
            '321', '4321', '54321',
            '111', '222', '333', '444', '555',
            '666', '777', '888', '999',
            '007', '100', '200', '300',
            '69', '420', '777', '888',
            '01', '02', '03', '04', '05',
            '10', '20', '30', '40', '50',
            '99', '88', '77', '66',
            '1111', '2222', '3333', '4444',
            '0000', '11111', '22222'
        ]
        
        # Common years (people use these more than random years)
        self.common_years = [
            '2024', '2023', '2022', '2021', '2020',
            '2019', '2018', '2017', '2016', '2015',
            '2010', '2005', '2000', '1995', '1990',
            '1985', '1980', '1975', '1970',
            '24', '23', '22', '21', '20',
            '19', '18', '17', '16', '15'
        ]
        
        # Simple leet substitutions that people actually use
        self.leet_map = {
            'a': ['4', '@'],
            'e': ['3'],
            'i': ['1', '!'],
            'o': ['0'],
            's': ['5', '$'],
            't': ['7']
        }
        
    def parse_human_date(self, date_str: str) -> Dict:
        """Parse date in human formats"""
        date_info = {}
        
        if not date_str:
            return date_info
        
        # Remove any separators
        clean_date = re.sub(r'[^\d]', '', date_str)
        
        # Try to parse based on length
        if len(clean_date) == 8:  # DDMMYYYY
            date_info['day'] = clean_date[0:2]
            date_info['month'] = clean_date[2:4]
            date_info['year'] = clean_date[4:8]
            date_info['year_short'] = clean_date[6:8]
        elif len(clean_date) == 6:  # DDMMYY
            date_info['day'] = clean_date[0:2]
            date_info['month'] = clean_date[2:4]
            date_info['year'] = '20' + clean_date[4:6]
            date_info['year_short'] = clean_date[4:6]
        elif len(clean_date) == 4:  # DDMM or MMDD
            date_info['day'] = clean_date[0:2]
            date_info['month'] = clean_date[2:4]
        
        # Also add cleaned date itself
        date_info['full'] = clean_date
        
        return date_info
    
    def generate_smart_combinations(self, data: Dict) -> Set[str]:
        """Generate smart, human-like combinations"""
        passwords = set()
        
        # Extract base information
        first_name = data.get('first_name', '').lower()
        last_name = data.get('last_name', '').lower()
        nickname = data.get('nickname', '').lower()
        birth_date = data.get('birth_date', '')
        
        # Parse date
        date_info = self.parse_human_date(birth_date)
        
        # Prepare variables for pattern generation
        vars_dict = {
            'first': first_name,
            'first_initial': first_name[0] if first_name else '',
            'last': last_name,
            'last_initial': last_name[0] if last_name else '',
            'nick': nickname,
            'year': date_info.get('year', ''),
            'year_short': date_info.get('year_short', ''),
            'birth_day': date_info.get('day', ''),
            'birth_month': date_info.get('month', ''),
            'day': date_info.get('day', ''),
            'month': date_info.get('month', ''),
            'special': random.choice(self.common_specials) if data.get('use_specials') else '',
        }
        
        # Add family info if available
        if 'spouse_name' in data:
            spouse = data['spouse_name'].lower()
            vars_dict['spouse_initial'] = spouse[0] if spouse else ''
        
        if 'child_name' in data:
            vars_dict['child_name'] = data['child_name'].lower()
        
        if 'pet_name' in data:
            vars_dict['pet_name'] = data['pet_name'].lower()
        
        # Add interest info if available
        if 'sport' in data:
            vars_dict['sport'] = data['sport'].lower()
        
        if 'team' in data:
            vars_dict['team'] = data['team'].lower()
        
        if 'movie' in data:
            vars_dict['movie'] = data['movie'].lower()
        
        if 'music' in data:
            vars_dict['music'] = data['music'].lower()
        
        if 'book' in data:
            vars_dict['book'] = data['book'].lower()
        
        if 'game' in data:
            vars_dict['game'] = data['game'].lower()
        
        if 'celebrity' in data:
            vars_dict['celebrity'] = data['celebrity'].lower()
        
        if 'place' in data:
            vars_dict['place'] = data['place'].lower()
        
        if 'hobby' in data:
            vars_dict['hobby'] = data['hobby'].lower()
        
        if 'lucky_num' in data:
            vars_dict['lucky_num'] = data['lucky_num'].lower()
        
        # Generate base patterns
        print("\n[*] Generating smart human patterns...")
        
        # Apply each pattern template
        for pattern in self.human_patterns:
            try:
                password = pattern.format(**vars_dict)
                if 6 <= len(password) <= 20:  # Reasonable length
                    passwords.add(password)
                    
                    # Add capitalized versions
                    passwords.add(password.title())
                    passwords.add(password.capitalize())
                    
                    # Add with common numbers
                    if data.get('add_numbers', True):
                        for num in self.common_numbers[:10]:  # First 10 common numbers
                            # Add number at end
                            passwords.add(password + num)
                            # Add number in middle (for some patterns)
                            if '_' in password or '.' in password:
                                parts = re.split(r'[._]', password)
                                if len(parts) > 1:
                                    passwords.add(parts[0] + num + parts[1])
            except KeyError:
                continue
        
        # Generate specific combinations you mentioned
        self.generate_specific_examples(passwords, first_name, last_name, date_info, data)
        
        # Add number variations
        if data.get('add_numbers', True):
            passwords.update(self.add_number_variations(passwords, date_info))
        
        # Add special character variations
        if data.get('use_specials', False):
            passwords.update(self.add_special_variations(passwords, data.get('specials', self.common_specials)))
        
        # Add leet variations
        if data.get('use_leet', False):
            passwords.update(self.add_leet_variations(passwords))
        
        # Add common password patterns
        passwords.update(self.generate_common_passwords(first_name, last_name, date_info))
        
        return passwords
    
    def generate_specific_examples(self, passwords: Set[str], first_name: str, last_name: str, 
                                  date_info: Dict, data: Dict):
        """Generate the specific examples you mentioned"""
        
        if not first_name or not last_name:
            return
        
        day = date_info.get('day', '')
        month = date_info.get('month', '')
        year = date_info.get('year', '')
        year_short = date_info.get('year_short', '')
        
        # Example 1: firstlast + date parts
        passwords.add(f"{first_name}{last_name}{day}{month}{year_short}")
        passwords.add(f"{first_name}{last_name}{year}")
        passwords.add(f"{first_name}{last_name}{day}")
        passwords.add(f"{first_name}{last_name}{month}")
        passwords.add(f"{first_name}{last_name}{year_short}")
        
        # Example 2: lastfirst + date parts
        passwords.add(f"{last_name}{first_name}{day}{month}{year}")
        passwords.add(f"{last_name}{first_name}{year}")
        passwords.add(f"{last_name}{first_name}{day}{month}")
        
        # Example 3: first + last repeated
        passwords.add(f"{first_name}{last_name}{last_name}{year}")
        passwords.add(f"{first_name}{first_name}{last_name}{year}")
        
        # Example 4: With separators
        passwords.add(f"{first_name}.{last_name}{year_short}")
        passwords.add(f"{first_name}_{last_name}{year}")
        passwords.add(f"{first_name}{last_name}@{year_short}")
        
        # Example 5: Mixed patterns
        passwords.add(f"{first_name}{year}{last_name}")
        passwords.add(f"{year_short}{first_name}{last_name}")
        passwords.add(f"{first_name}{last_name[0]}{year}")
        
        # Example 6: Simple combinations
        passwords.add(f"{first_name}{last_name}")
        passwords.add(f"{last_name}{first_name}")
        passwords.add(f"{first_name[0]}{last_name}")
        passwords.add(f"{first_name}{last_name[0]}")
        
        # Example 7: With common endings
        passwords.add(f"{first_name}{last_name}123")
        passwords.add(f"{first_name}{last_name}!23")
        passwords.add(f"{first_name}{last_name}@123")
        
    def add_number_variations(self, passwords: Set[str], date_info: Dict) -> Set[str]:
        """Add intelligent number variations"""
        new_passwords = set()
        
        day = date_info.get('day', '')
        month = date_info.get('month', '')
        year = date_info.get('year', '')
        year_short = date_info.get('year_short', '')
        
        # Date combinations people commonly use
        date_combinations = []
        if day and month:
            date_combinations.append(f"{day}{month}")
            date_combinations.append(f"{month}{day}")
        
        if day and month and year_short:
            date_combinations.append(f"{day}{month}{year_short}")
            date_combinations.append(f"{month}{day}{year_short}")
        
        if year:
            date_combinations.append(year)
        
        if year_short:
            date_combinations.append(year_short)
        
        # Add date combinations to existing passwords
        for pwd in list(passwords)[:100]:  # Limit to avoid explosion
            for date_combo in date_combinations[:3]:  # First 3 date combos
                # Add date at end
                new_passwords.add(pwd + date_combo)
                # Add date at beginning
                new_passwords.add(date_combo + pwd)
                
                # If password already has some numbers, replace them
                if any(char.isdigit() for char in pwd):
                    # Try to replace the last numbers with date
                    num_match = re.search(r'\d+$', pwd)
                    if num_match:
                        new_pwd = pwd[:num_match.start()] + date_combo
                        new_passwords.add(new_pwd)
        
        # Add common number patterns
        for pwd in list(passwords)[:50]:
            for num in self.common_numbers[:5]:
                new_passwords.add(pwd + num)
                
                # Insert number in the middle for passwords with separators
                if len(pwd) > 5 and ('_' in pwd or '.' in pwd or '-' in pwd):
                    parts = re.split(r'[._-]', pwd)
                    if len(parts) == 2:
                        new_passwords.add(parts[0] + num + parts[1])
        
        return new_passwords
    
    def add_special_variations(self, passwords: Set[str], specials: List[str]) -> Set[str]:
        """Add special characters in human-like ways"""
        new_passwords = set()
        
        for pwd in list(passwords)[:200]:  # Limit
            new_passwords.add(pwd)  # Keep original
            
            for special in specials[:3]:  # Most common specials
                # Add at end
                new_passwords.add(pwd + special)
                
                # Add at beginning
                new_passwords.add(special + pwd)
                
                # Add at both ends
                new_passwords.add(special + pwd + special)
                
                # Replace spaces/separators with specials
                if ' ' in pwd:
                    new_passwords.add(pwd.replace(' ', special))
                
                # Insert in the middle for longer passwords
                if len(pwd) > 8:
                    mid = len(pwd) // 2
                    new_passwords.add(pwd[:mid] + special + pwd[mid:])
        
        return new_passwords
    
    def add_leet_variations(self, passwords: Set[str]) -> Set[str]:
        """Add leet speak variations (only common ones)"""
        new_passwords = set()
        
        for pwd in list(passwords)[:100]:  # Limit
            new_passwords.add(pwd)  # Keep original
            
            # Only apply leet to some passwords (30% chance)
            if random.random() < 0.3:
                leet_pwd = pwd
                
                # Apply common leet substitutions
                for char, subs in self.leet_map.items():
                    if char in leet_pwd.lower():
                        # Replace only one occurrence (not all)
                        if random.random() < 0.5:
                            leet_pwd = leet_pwd.replace(char, random.choice(subs))
                            leet_pwd = leet_pwd.replace(char.upper(), random.choice(subs))
                
                if leet_pwd != pwd:
                    new_passwords.add(leet_pwd)
        
        return new_passwords
    
    def generate_common_passwords(self, first_name: str, last_name: str, date_info: Dict) -> Set[str]:
        """Generate common password patterns"""
        passwords = set()
        
        if not first_name or not last_name:
            return passwords
        
        # Very common patterns
        passwords.add(f"{first_name}123")
        passwords.add(f"{first_name}1234")
        passwords.add(f"{last_name}123")
        passwords.add(f"{first_name}{last_name[0]}123")
        
        # With special characters
        passwords.add(f"{first_name}!23")
        passwords.add(f"{first_name}@123")
        passwords.add(f"{first_name}#123")
        
        # Year patterns
        year = date_info.get('year', '')
        year_short = date_info.get('year_short', '')
        
        if year:
            passwords.add(f"{first_name}{year}")
            passwords.add(f"{last_name}{year}")
            passwords.add(f"{first_name}{last_name[0]}{year_short}")
        
        # Simple combinations
        passwords.add(first_name.lower())
        passwords.add(first_name.title())
        passwords.add(last_name.lower())
        passwords.add(last_name.title())
        
        return passwords
    
    def analyze_and_filter(self, passwords: Set[str], min_len: int = 6, max_len: int = 20) -> Set[str]:
        """Analyze and filter passwords"""
        filtered = set()
        
        print("\n[*] Analyzing and filtering passwords...")
        
        # Count patterns
        pattern_stats = defaultdict(int)
        
        for pwd in passwords:
            # Length check
            if not (min_len <= len(pwd) <= max_len):
                continue
            
            # Remove unrealistic patterns
            # Too many consecutive specials
            if re.search(r'[!@#$%^&*]{3,}', pwd):
                continue
            
            # Too many consecutive numbers
            if re.search(r'\d{6,}', pwd):
                continue
            
            # Must have at least one letter
            if not re.search(r'[a-zA-Z]', pwd):
                continue
            
            # Categorize pattern
            if pwd.islower():
                pattern_stats['all_lowercase'] += 1
            elif pwd.isupper():
                pattern_stats['all_uppercase'] += 1
            elif pwd[0].isupper():
                pattern_stats['first_capital'] += 1
            elif pwd.title() == pwd:
                pattern_stats['title_case'] += 1
            
            if any(c in pwd for c in '!@#$%^&*'):
                pattern_stats['has_special'] += 1
            
            if re.search(r'\d', pwd):
                pattern_stats['has_numbers'] += 1
            
            filtered.add(pwd)
        
        # Print statistics
        print(f"\n[+] Pattern Statistics:")
        print(f"    Total generated: {len(passwords)}")
        print(f"    After filtering: {len(filtered)}")
        
        if filtered:
            print(f"\n    Pattern distribution:")
            for pattern, count in sorted(pattern_stats.items()):
                percentage = (count / len(filtered)) * 100
                print(f"      {pattern:20}: {count:6} ({percentage:5.1f}%)")
        
        return filtered
    
    def apply_advanced_filters(self, passwords: Set[str], options: Dict) -> Set[str]:
        """Apply advanced filtering based on user options"""
        filtered = set()
        
        similar_chars = set('il1Lo0O') if options.get('exclude_similar', False) else set()
        exclude_sequential = options.get('exclude_sequential', False)
        avoid_repeats = options.get('avoid_repeats', False)
        require_uppercase = options.get('require_uppercase', False)
        require_lowercase = options.get('require_lowercase', False)
        require_digits = options.get('require_digits', False)
        require_special = options.get('require_special', False)
        min_strength = options.get('min_strength', 0)
        max_repeat = int(options.get('max_repeat', 3))
        min_uppercase = int(options.get('min_uppercase', 0))
        min_digits = int(options.get('min_digits', 0))
        min_special = int(options.get('min_special', 0))
        
        for pwd in passwords:
            # Exclude similar characters check
            if similar_chars and any(c in pwd for c in similar_chars):
                continue
            
            # Sequential numbers check
            if exclude_sequential:
                if self._contains_sequential(pwd):
                    continue
            
            # Repeating characters check
            if avoid_repeats and self._has_repeating_chars(pwd, max_repeat):
                continue
            
            # Character requirement checks
            has_upper = any(c.isupper() for c in pwd)
            has_lower = any(c.islower() for c in pwd)
            has_digit = any(c.isdigit() for c in pwd)
            has_special = any(c in '!@#$%^&*' for c in pwd)
            
            if require_uppercase and not has_upper:
                continue
            if require_lowercase and not has_lower:
                continue
            if require_digits and not has_digit:
                continue
            if require_special and not has_special:
                continue
            
            # Minimum count requirements
            upper_count = sum(1 for c in pwd if c.isupper())
            digit_count = sum(1 for c in pwd if c.isdigit())
            special_count = sum(1 for c in pwd if c in '!@#$%^&*')
            
            if upper_count < min_uppercase or digit_count < min_digits or special_count < min_special:
                continue
            
            # Strength check
            if min_strength > 0:
                strength = self.calculate_complexity(pwd)
                if strength < min_strength:
                    continue
            
            filtered.add(pwd)
        
        return filtered
    
    def _contains_sequential(self, pwd: str) -> bool:
        """Check if password contains sequential numbers"""
        sequences = ['012', '123', '234', '345', '456', '567', '678', '789', '890', 
                    '321', '432', '543', '654', '765', '876', '987']
        return any(seq in pwd for seq in sequences)
    
    def _has_repeating_chars(self, pwd: str, max_allowed: int) -> bool:
        """Check if password has more than max_allowed repeating characters"""
        for char in set(pwd):
            count = pwd.count(char)
            if count > max_allowed:
                return True
        return False

    def calculate_complexity(self, password: str) -> int:
        """Calculate password complexity score (1-10)"""
        score = 0
        
        # Length score
        if len(password) >= 12:
            score += 3
        elif len(password) >= 8:
            score += 2
        elif len(password) >= 6:
            score += 1
        
        # Character variety
        if any(c.isupper() for c in password):
            score += 1
        if any(c.islower() for c in password):
            score += 1
        if any(c.isdigit() for c in password):
            score += 1
        if any(c in '!@#$%^&*' for c in password):
            score += 2
            
        if re.search(r'\d{4,}$', password):  # Long number sequence at end
            score += 1
            
        return min(max(score, 1), 10)
    
    def show_examples(self, passwords: Set[str], count: int = 20):
        """Show example passwords"""
        if not passwords:
            print("\n[-] No passwords generated!")
            return
        
        print(f"\n[*] Example passwords (showing {min(count, len(passwords))}):")
        print("-" * 50)
        
        sample = list(passwords)
        random.shuffle(sample)
        
        for i, pwd in enumerate(sample[:count], 1):
            # Show password with some analysis
            has_special = '✓' if any(c in pwd for c in '!@#$%^&*') else ' '
            has_number = '✓' if any(c.isdigit() for c in pwd) else ' '
            has_upper = '✓' if any(c.isupper() for c in pwd) else ' '
            
            print(f"  {i:2}. {pwd:25} [S:{has_special} N:{has_number} U:{has_upper}]")

def main():
    parser = argparse.ArgumentParser(
        description='SMART HUMAN PASSWORD GENERATOR - Creates realistic password patterns',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python smart_generator.py
  
  # Command line with your example
  python smart_generator.py --first manan --last kamboj --birth 07092010
  
  # With options
  python smart_generator.py --first john --last doe --birth 15061990 
         --special --leet --output john_passwords.txt
        """
    )
    
    parser.add_argument('--first', help='First name')
    parser.add_argument('--last', help='Last name')
    parser.add_argument('--birth', help='Birth date (DDMMYYYY or DD/MM/YYYY)')
    parser.add_argument('--nick', help='Nickname')
    
    parser.add_argument('--special', action='store_true', help='Add special characters')
    parser.add_argument('--leet', action='store_true', help='Add leet speak variations')
    parser.add_argument('--numbers', action='store_true', default=True, 
                       help='Add common number patterns')
    
    parser.add_argument('-o', '--output', default='smart_passwords.txt',
                       help='Output filename')
    parser.add_argument('--max', type=int, default=5000,
                       help='Maximum passwords to generate')
    
    args = parser.parse_args()
    
    generator = SmartHumanPasswordGenerator()
    
    print("\n" + "="*60)
    print(" SMART HUMAN PASSWORD GENERATOR")
    print("="*60)
    
    # Get user input
    data = {}
    
    if args.first and args.last and args.birth:
        # Use command line args
        print("\n[*] Using command line parameters...")
        data['first_name'] = args.first.lower()
        data['last_name'] = args.last.lower()
        data['birth_date'] = args.birth
        
        if args.nick:
            data['nickname'] = args.nick.lower()
        
        data['use_specials'] = args.special
        data['use_leet'] = args.leet
        data['add_numbers'] = args.numbers
        data['specials'] = generator.common_specials
        
    else:
        # Interactive mode
        print("\n[*] Please provide your information:")
        
        data['first_name'] = input("First name: ").strip().lower()
        while not data['first_name']:
            print("First name is required!")
            data['first_name'] = input("First name: ").strip().lower()
        
        data['last_name'] = input("Last name: ").strip().lower()
        while not data['last_name']:
            print("Last name is required!")
            data['last_name'] = input("Last name: ").strip().lower()
        
        data['birth_date'] = input("Birth date (DDMMYYYY or DD/MM/YYYY): ").strip()
        
        data['nickname'] = input("Nickname (optional): ").strip().lower()
        
        # Optional family info
        spouse = input("Spouse name (optional): ").strip().lower()
        if spouse:
            data['spouse_name'] = spouse
        
        child = input("Child name (optional): ").strip().lower()
        if child:
            data['child_name'] = child
        
        pet = input("Pet name (optional): ").strip().lower()
        if pet:
            data['pet_name'] = pet
        
        # Options
        special_choice = input("\nAdd special characters? (y/n): ").strip().lower()
        data['use_specials'] = special_choice == 'y'
        
        if data['use_specials']:
            custom = input(f"Use these specials [{''.join(generator.common_specials[:5])}] or custom? (enter for default): ").strip()
            if custom:
                data['specials'] = list(custom)
            else:
                data['specials'] = generator.common_specials[:5]
        
        leet_choice = input("Add leet speak variations? (y/n): ").strip().lower()
        data['use_leet'] = leet_choice == 'y'
        
        num_choice = input("Add common number patterns? (y/n): ").strip().lower()
        data['add_numbers'] = num_choice == 'y'
    
    print(f"\n[*] Generating passwords for: {data['first_name'].title()} {data['last_name'].title()}")
    if data.get('birth_date'):
        print(f"[*] Birth date: {data['birth_date']}")
    
    # Generate passwords
    passwords = generator.generate_smart_combinations(data)
    
    # Filter
    filtered = generator.analyze_and_filter(passwords, min_len=6, max_len=20)
    
    # Limit if specified
    if args.max > 0 and len(filtered) > args.max:
        filtered = set(list(filtered)[:args.max])
        print(f"[*] Limited to {args.max} passwords")
    
    # Show examples
    generator.show_examples(filtered)
    
    # Save to file
    if filtered:
        print(f"\n[*] Saving {len(filtered)} passwords to {args.output}...")
        
        # Sort by length and alphabetically
        sorted_passwords = sorted(filtered, key=lambda x: (len(x), x))
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(f"# Smart human passwords generated on {datetime.now().strftime('%Y-%m-%d')}\n")
            f.write(f"# Name: {data['first_name'].title()} {data['last_name'].title()}\n")
            if data.get('birth_date'):
                f.write(f"# Birth date: {data['birth_date']}\n")
            f.write(f"# Total passwords: {len(sorted_passwords)}\n")
            f.write("#" * 50 + "\n\n")
            
            for pwd in sorted_passwords:
                f.write(pwd + '\n')
        
        file_size = os.path.getsize(args.output)
        print(f"[+] Saved successfully!")
        print(f"[+] File size: {file_size:,} bytes")
        
        # Show some interesting stats
        print(f"\n[*] Interesting facts:")
        print(f"    Most common length: {max(set(len(p) for p in filtered), key=list(len(p) for p in filtered).count)} chars")
        
        # Count patterns
        special_count = sum(1 for p in filtered if any(c in p for c in '!@#$%^&*'))
        number_count = sum(1 for p in filtered if any(c.isdigit() for c in p))
        
        print(f"    Passwords with special chars: {special_count} ({special_count/len(filtered)*100:.1f}%)")
        print(f"    Passwords with numbers: {number_count} ({number_count/len(filtered)*100:.1f}%)")
        
    else:
        print("\n[-] No passwords to save!")


class PasswordGeneratorGUI:
    def __init__(self):
        self.generator = SmartHumanPasswordGenerator()
        self.passwords = set()
        self.root = tk.Tk()
        self.root.title("Smart Human Password Generator v2.0")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2b2b2b')
        
        # Set style
        self.setup_styles()
        
        # Variables
        self.current_file = None
        self.generation_in_progress = False
        
        # Create GUI
        self.create_widgets()
        
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Title.TLabel', background='#2b2b2b', foreground='#4fc3f7', 
                       font=('Arial', 16, 'bold'))
        style.configure('Section.TLabel', background='#2b2b2b', foreground='#81c784',
                       font=('Arial', 12, 'bold'))
        style.configure('Normal.TLabel', background='#2b2b2b', foreground='#e0e0e0')
        
        # Configure buttons
        style.configure('Primary.TButton', background='#1976d2', foreground='white',
                       borderwidth=1, focuscolor='none')
        style.map('Primary.TButton',
                 background=[('active', '#1565c0')],
                 foreground=[('active', 'white')])
        
        style.configure('Success.TButton', background='#388e3c', foreground='white')
        style.map('Success.TButton',
                 background=[('active', '#2e7d32')])
        
        style.configure('Info.TButton', background='#0288d1', foreground='white')
        style.map('Info.TButton',
                 background=[('active', '#0277bd')])
        
        # Configure entries
        style.configure('Custom.TEntry', fieldbackground='#424242', foreground='white',
                       borderwidth=2, relief='solid')
        
        # Configure checkbuttons
        style.configure('Custom.TCheckbutton', background='#2b2b2b', foreground='#e0e0e0')
        
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_frame = ttk.Frame(main_container)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(title_frame, text="🔒 SMART HUMAN PASSWORD GENERATOR", 
                 style='Title.TLabel').pack()
        ttk.Label(title_frame, text="Generate realistic password patterns humans actually use", 
                 style='Normal.TLabel').pack()
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_container)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Personal Information
        self.create_personal_info_tab(notebook)
        
        # Tab 2: Options
        self.create_options_tab(notebook)
        
        # Tab 3: Output
        self.create_output_tab(notebook)
        
        # Status bar
        self.create_status_bar(main_container)
        
    def create_personal_info_tab(self, notebook):
        """Create the personal information tab"""
        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text="Personal Information")
        
        # Create scrollable frame
        canvas = tk.Canvas(tab1, bg='#2b2b2b', highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab1, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Required Information Section
        required_frame = ttk.LabelFrame(scrollable_frame, text="Required Information", padding=15)
        required_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(required_frame, text="First Name:", style='Section.TLabel').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.first_name_var = tk.StringVar()
        ttk.Entry(required_frame, textvariable=self.first_name_var, width=30, style='Custom.TEntry').grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(required_frame, text="Last Name:", style='Section.TLabel').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.last_name_var = tk.StringVar()
        ttk.Entry(required_frame, textvariable=self.last_name_var, width=30, style='Custom.TEntry').grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(required_frame, text="Birth Date:", style='Section.TLabel').grid(row=2, column=0, sticky=tk.W, pady=5)
        self.birth_date_var = tk.StringVar()
        ttk.Entry(required_frame, textvariable=self.birth_date_var, width=30, style='Custom.TEntry').grid(row=2, column=1, padx=10, pady=5)
        ttk.Label(required_frame, text="Format: DDMMYYYY or DD/MM/YYYY", 
                 style='Normal.TLabel').grid(row=2, column=2, padx=10, pady=5)
        
        # Optional Information Section
        optional_frame = ttk.LabelFrame(scrollable_frame, text="Optional Information", padding=15)
        optional_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(optional_frame, text="Nickname:", style='Section.TLabel').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.nickname_var = tk.StringVar()
        ttk.Entry(optional_frame, textvariable=self.nickname_var, width=30, style='Custom.TEntry').grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(optional_frame, text="Spouse Name:", style='Section.TLabel').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.spouse_name_var = tk.StringVar()
        ttk.Entry(optional_frame, textvariable=self.spouse_name_var, width=30, style='Custom.TEntry').grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(optional_frame, text="Child Name:", style='Section.TLabel').grid(row=2, column=0, sticky=tk.W, pady=5)
        self.child_name_var = tk.StringVar()
        ttk.Entry(optional_frame, textvariable=self.child_name_var, width=30, style='Custom.TEntry').grid(row=2, column=1, padx=10, pady=5)
        
        ttk.Label(optional_frame, text="Pet Name:", style='Section.TLabel').grid(row=3, column=0, sticky=tk.W, pady=5)
        self.pet_name_var = tk.StringVar()
        ttk.Entry(optional_frame, textvariable=self.pet_name_var, width=30, style='Custom.TEntry').grid(row=3, column=1, padx=10, pady=5)
        
        # Location Information
        location_frame = ttk.LabelFrame(scrollable_frame, text="Location Information", padding=15)
        location_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(location_frame, text="City:", style='Section.TLabel').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.city_var = tk.StringVar()
        ttk.Entry(location_frame, textvariable=self.city_var, width=30, style='Custom.TEntry').grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(location_frame, text="Hometown:", style='Section.TLabel').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.hometown_var = tk.StringVar()
        ttk.Entry(location_frame, textvariable=self.hometown_var, width=30, style='Custom.TEntry').grid(row=1, column=1, padx=10, pady=5)
        
        # Work & Education
        work_frame = ttk.LabelFrame(scrollable_frame, text="Work & Education", padding=15)
        work_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(work_frame, text="Company:", style='Section.TLabel').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.company_var = tk.StringVar()
        ttk.Entry(work_frame, textvariable=self.company_var, width=30, style='Custom.TEntry').grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(work_frame, text="School:", style='Section.TLabel').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.school_var = tk.StringVar()
        ttk.Entry(work_frame, textvariable=self.school_var, width=30, style='Custom.TEntry').grid(row=1, column=1, padx=10, pady=5)
        
        # Interests
        interests_frame = ttk.LabelFrame(scrollable_frame, text="Interests & Hobbies", padding=15)
        interests_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(interests_frame, text="Favorite Sport:", style='Section.TLabel').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.sport_var = tk.StringVar()
        ttk.Entry(interests_frame, textvariable=self.sport_var, width=30, style='Custom.TEntry').grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(interests_frame, text="Favorite Team:", style='Section.TLabel').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.team_var = tk.StringVar()
        ttk.Entry(interests_frame, textvariable=self.team_var, width=30, style='Custom.TEntry').grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(interests_frame, text="Favorite Movie:", style='Section.TLabel').grid(row=2, column=0, sticky=tk.W, pady=5)
        self.movie_var = tk.StringVar()
        ttk.Entry(interests_frame, textvariable=self.movie_var, width=30, style='Custom.TEntry').grid(row=2, column=1, padx=10, pady=5)
        
        ttk.Label(interests_frame, text="Favorite Music/Artist:", style='Section.TLabel').grid(row=3, column=0, sticky=tk.W, pady=5)
        self.music_var = tk.StringVar()
        ttk.Entry(interests_frame, textvariable=self.music_var, width=30, style='Custom.TEntry').grid(row=3, column=1, padx=10, pady=5)
        
        ttk.Label(interests_frame, text="Favorite Book/Author:", style='Section.TLabel').grid(row=4, column=0, sticky=tk.W, pady=5)
        self.book_var = tk.StringVar()
        ttk.Entry(interests_frame, textvariable=self.book_var, width=30, style='Custom.TEntry').grid(row=4, column=1, padx=10, pady=5)
        
        ttk.Label(interests_frame, text="Favorite Game/Character:", style='Section.TLabel').grid(row=5, column=0, sticky=tk.W, pady=5)
        self.game_var = tk.StringVar()
        ttk.Entry(interests_frame, textvariable=self.game_var, width=30, style='Custom.TEntry').grid(row=5, column=1, padx=10, pady=5)
        
        ttk.Label(interests_frame, text="Favorite Celebrity:", style='Section.TLabel').grid(row=6, column=0, sticky=tk.W, pady=5)
        self.celebrity_var = tk.StringVar()
        ttk.Entry(interests_frame, textvariable=self.celebrity_var, width=30, style='Custom.TEntry').grid(row=6, column=1, padx=10, pady=5)
        
        ttk.Label(interests_frame, text="Favorite Place/Travel:", style='Section.TLabel').grid(row=7, column=0, sticky=tk.W, pady=5)
        self.place_var = tk.StringVar()
        ttk.Entry(interests_frame, textvariable=self.place_var, width=30, style='Custom.TEntry').grid(row=7, column=1, padx=10, pady=5)
        
        ttk.Label(interests_frame, text="Hobby/Activity:", style='Section.TLabel').grid(row=8, column=0, sticky=tk.W, pady=5)
        self.hobby_var = tk.StringVar()
        ttk.Entry(interests_frame, textvariable=self.hobby_var, width=30, style='Custom.TEntry').grid(row=8, column=1, padx=10, pady=5)
        
        ttk.Label(interests_frame, text="Lucky Number/Dates:", style='Section.TLabel').grid(row=9, column=0, sticky=tk.W, pady=5)
        self.lucky_num_var = tk.StringVar()
        ttk.Entry(interests_frame, textvariable=self.lucky_num_var, width=30, style='Custom.TEntry').grid(row=9, column=1, padx=10, pady=5)
        
        # Example presets
        presets_frame = ttk.LabelFrame(scrollable_frame, text="Quick Presets", padding=15)
        presets_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(presets_frame, text="Example: John Doe", 
                  command=lambda: self.load_preset("john"), 
                  style='Info.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(presets_frame, text="Example: Sarah Smith", 
                  command=lambda: self.load_preset("sarah"), 
                  style='Info.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(presets_frame, text="Example: Manan Kamboj", 
                  command=lambda: self.load_preset("manan"), 
                  style='Info.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(presets_frame, text="Clear All", 
                  command=self.clear_all_fields, 
                  style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        
    def create_options_tab(self, notebook):
        """Create the options tab with scrollbar"""
        tab2 = ttk.Frame(notebook)
        notebook.add(tab2, text="Generation Options")
        
        # Create canvas and scrollbar for scrollable content
        canvas = tk.Canvas(tab2, bg="#2b2b2b", highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab2, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # Configure canvas scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Options frame inside scrollable area
        options_frame = ttk.LabelFrame(scrollable_frame, text="Password Generation Options", padding=20)
        options_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Generation settings
        settings_frame = ttk.Frame(options_frame)
        settings_frame.pack(fill=tk.X, pady=10)
        
        # Checkboxes
        self.use_specials_var = tk.BooleanVar(value=True)
        self.use_leet_var = tk.BooleanVar(value=False)
        self.use_numbers_var = tk.BooleanVar(value=True)
        self.use_family_var = tk.BooleanVar(value=True)
        self.use_location_var = tk.BooleanVar(value=False)
        self.use_interests_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(settings_frame, text="Add special characters", 
                       variable=self.use_specials_var, style='Custom.TCheckbutton').grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Checkbutton(settings_frame, text="Add leet speak variations", 
                       variable=self.use_leet_var, style='Custom.TCheckbutton').grid(row=0, column=1, sticky=tk.W, pady=5, padx=20)
        ttk.Checkbutton(settings_frame, text="Add common number patterns", 
                       variable=self.use_numbers_var, style='Custom.TCheckbutton').grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Checkbutton(settings_frame, text="Include family information", 
                       variable=self.use_family_var, style='Custom.TCheckbutton').grid(row=1, column=1, sticky=tk.W, pady=5, padx=20)
        ttk.Checkbutton(settings_frame, text="Include location information", 
                       variable=self.use_location_var, style='Custom.TCheckbutton').grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Checkbutton(settings_frame, text="Include interests", 
                       variable=self.use_interests_var, style='Custom.TCheckbutton').grid(row=2, column=1, sticky=tk.W, pady=5, padx=20)
        
        # Special characters selection
        specials_frame = ttk.LabelFrame(options_frame, text="Special Characters", padding=10)
        specials_frame.pack(fill=tk.X, pady=10)
        
        self.specials_var = tk.StringVar(value='!@#$%&*')
        ttk.Label(specials_frame, text="Characters to use:", style='Normal.TLabel').pack(side=tk.LEFT, padx=5)
        ttk.Entry(specials_frame, textvariable=self.specials_var, width=20, style='Custom.TEntry').pack(side=tk.LEFT, padx=5)
        ttk.Label(specials_frame, text="(e.g., !@#$%^&*)", style='Normal.TLabel').pack(side=tk.LEFT, padx=5)
        
        # Length constraints
        length_frame = ttk.LabelFrame(options_frame, text="Password Length", padding=10)
        length_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(length_frame, text="Minimum:", style='Normal.TLabel').pack(side=tk.LEFT, padx=5)
        self.min_length_var = tk.StringVar(value='6')
        ttk.Spinbox(length_frame, from_=4, to=32, textvariable=self.min_length_var, width=5).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(length_frame, text="Maximum:", style='Normal.TLabel').pack(side=tk.LEFT, padx=5)
        self.max_length_var = tk.StringVar(value='20')
        ttk.Spinbox(length_frame, from_=6, to=64, textvariable=self.max_length_var, width=5).pack(side=tk.LEFT, padx=5)
        
        # Max passwords
        max_frame = ttk.LabelFrame(options_frame, text="Output Limits", padding=10)
        max_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(max_frame, text="Max passwords to generate:", style='Normal.TLabel').pack(side=tk.LEFT, padx=5)
        self.max_passwords_var = tk.StringVar(value='5000')
        ttk.Spinbox(max_frame, from_=100, to=50000, increment=100, 
                   textvariable=self.max_passwords_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # Pattern intensity
        pattern_frame = ttk.LabelFrame(options_frame, text="Pattern Intensity", padding=10)
        pattern_frame.pack(fill=tk.X, pady=10)
        
        self.pattern_intensity_var = tk.IntVar(value=2)
        ttk.Label(pattern_frame, text="Simple", style='Normal.TLabel').pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(pattern_frame, variable=self.pattern_intensity_var, value=1).pack(side=tk.LEFT)
        ttk.Radiobutton(pattern_frame, variable=self.pattern_intensity_var, value=2).pack(side=tk.LEFT)
        ttk.Radiobutton(pattern_frame, variable=self.pattern_intensity_var, value=3).pack(side=tk.LEFT)
        ttk.Radiobutton(pattern_frame, variable=self.pattern_intensity_var, value=4).pack(side=tk.LEFT)
        ttk.Radiobutton(pattern_frame, variable=self.pattern_intensity_var, value=5).pack(side=tk.LEFT)
        ttk.Label(pattern_frame, text="Complex", style='Normal.TLabel').pack(side=tk.LEFT, padx=5)
        
        # ==================== ADVANCED OPTIONS ====================
        advanced_frame = ttk.LabelFrame(options_frame, text="🔐 Advanced Security Options", padding=15)
        advanced_frame.pack(fill=tk.X, pady=15)
        
        # Advanced checkboxes
        self.exclude_similar_var = tk.BooleanVar(value=False)
        self.require_uppercase_var = tk.BooleanVar(value=False)
        self.require_lowercase_var = tk.BooleanVar(value=True)
        self.require_digits_var = tk.BooleanVar(value=False)
        self.require_special_var = tk.BooleanVar(value=False)
        self.exclude_sequential_var = tk.BooleanVar(value=False)
        self.avoid_repeats_var = tk.BooleanVar(value=False)
        
        advanced_row1 = ttk.Frame(advanced_frame)
        advanced_row1.pack(fill=tk.X, pady=5)
        
        ttk.Checkbutton(advanced_row1, text="Exclude similar chars (i,l,1,L,o,0,O)", 
                       variable=self.exclude_similar_var, style='Custom.TCheckbutton').pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(advanced_row1, text="Require UPPERCASE letters", 
                       variable=self.require_uppercase_var, style='Custom.TCheckbutton').pack(side=tk.LEFT, padx=10)
        
        advanced_row2 = ttk.Frame(advanced_frame)
        advanced_row2.pack(fill=tk.X, pady=5)
        
        ttk.Checkbutton(advanced_row2, text="Require lowercase letters", 
                       variable=self.require_lowercase_var, style='Custom.TCheckbutton').pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(advanced_row2, text="Require at least 1 digit", 
                       variable=self.require_digits_var, style='Custom.TCheckbutton').pack(side=tk.LEFT, padx=10)
        
        advanced_row3 = ttk.Frame(advanced_frame)
        advanced_row3.pack(fill=tk.X, pady=5)
        
        ttk.Checkbutton(advanced_row3, text="Require special character", 
                       variable=self.require_special_var, style='Custom.TCheckbutton').pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(advanced_row3, text="Avoid sequential numbers (123, 456)", 
                       variable=self.exclude_sequential_var, style='Custom.TCheckbutton').pack(side=tk.LEFT, padx=10)
        
        advanced_row4 = ttk.Frame(advanced_frame)
        advanced_row4.pack(fill=tk.X, pady=5)
        
        ttk.Checkbutton(advanced_row4, text="Avoid repeating characters (aa, bb, etc.)", 
                       variable=self.avoid_repeats_var, style='Custom.TCheckbutton').pack(side=tk.LEFT, padx=10)
        
        # Minimum strength requirements
        strength_frame = ttk.LabelFrame(options_frame, text="🎯 Minimum Password Strength", padding=10)
        strength_frame.pack(fill=tk.X, pady=10)
        
        strength_row = ttk.Frame(strength_frame)
        strength_row.pack(fill=tk.X)
        
        ttk.Label(strength_row, text="Minimum Strength Score:", style='Normal.TLabel').pack(side=tk.LEFT, padx=5)
        self.min_strength_var = tk.IntVar(value=0)
        strength_scale = ttk.Scale(strength_row, from_=0, to=10, orient=tk.HORIZONTAL, 
                                   variable=self.min_strength_var, length=200)
        strength_scale.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        ttk.Label(strength_row, text="(0-10)", style='Normal.TLabel').pack(side=tk.LEFT, padx=5)
        
        # Complexity options
        complexity_frame = ttk.LabelFrame(options_frame, text="📈 Complexity Controls", padding=10)
        complexity_frame.pack(fill=tk.X, pady=10)
        
        complexity_row1 = ttk.Frame(complexity_frame)
        complexity_row1.pack(fill=tk.X, pady=5)
        
        ttk.Label(complexity_row1, text="Min uppercase letters:", style='Normal.TLabel').pack(side=tk.LEFT, padx=5)
        self.min_uppercase_var = tk.StringVar(value='0')
        ttk.Spinbox(complexity_row1, from_=0, to=10, textvariable=self.min_uppercase_var, width=5).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(complexity_row1, text="Min digits:", style='Normal.TLabel').pack(side=tk.LEFT, padx=20)
        self.min_digits_var = tk.StringVar(value='0')
        ttk.Spinbox(complexity_row1, from_=0, to=10, textvariable=self.min_digits_var, width=5).pack(side=tk.LEFT, padx=5)
        
        complexity_row2 = ttk.Frame(complexity_frame)
        complexity_row2.pack(fill=tk.X, pady=5)
        
        ttk.Label(complexity_row2, text="Min special chars:", style='Normal.TLabel').pack(side=tk.LEFT, padx=5)
        self.min_special_var = tk.StringVar(value='0')
        ttk.Spinbox(complexity_row2, from_=0, to=10, textvariable=self.min_special_var, width=5).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(complexity_row2, text="Max repeating chars:", style='Normal.TLabel').pack(side=tk.LEFT, padx=20)
        self.max_repeat_var = tk.StringVar(value='3')
        ttk.Spinbox(complexity_row2, from_=1, to=10, textvariable=self.max_repeat_var, width=5).pack(side=tk.LEFT, padx=5)
        
        # Performance options
        performance_frame = ttk.LabelFrame(options_frame, text="⚙️ Performance", padding=10)
        performance_frame.pack(fill=tk.X, pady=10)
        
        self.use_threading_var = tk.BooleanVar(value=True)
        self.filter_duplicates_var = tk.BooleanVar(value=True)
        
        perf_row = ttk.Frame(performance_frame)
        perf_row.pack(fill=tk.X)
        
        ttk.Checkbutton(perf_row, text="Use multithreading for generation", 
                       variable=self.use_threading_var, style='Custom.TCheckbutton').pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(perf_row, text="Remove duplicate passwords", 
                       variable=self.filter_duplicates_var, style='Custom.TCheckbutton').pack(side=tk.LEFT, padx=10)
        
        # Action buttons
        action_frame = ttk.Frame(options_frame)
        action_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(action_frame, text="🔧 Generate Passwords", 
                  command=self.generate_passwords_threaded,
                  style='Success.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="📊 Analyze Patterns", 
                  command=self.analyze_patterns,
                  style='Info.TButton').pack(side=tk.LEFT, padx=5)
        
    def create_output_tab(self, notebook):
        """Create the output tab"""
        tab3 = ttk.Frame(notebook)
        notebook.add(tab3, text="Password Output")
        
        # Create main frame
        main_output_frame = ttk.Frame(tab3)
        main_output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(main_output_frame, text="Generation Statistics", padding=10)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.stats_text = scrolledtext.ScrolledText(stats_frame, height=8, width=80, 
                                                   bg='#1e1e1e', fg='#e0e0e0',
                                                   font=('Consolas', 10))
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
        # Generated passwords frame
        passwords_frame = ttk.LabelFrame(main_output_frame, text="Generated Passwords", padding=10)
        passwords_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add search/filter frame
        filter_frame = ttk.Frame(passwords_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(filter_frame, text="Search:", style='Normal.TLabel').pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_passwords)
        ttk.Entry(filter_frame, textvariable=self.search_var, width=30, style='Custom.TEntry').pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filter_frame, text="Sort by:", style='Normal.TLabel').pack(side=tk.LEFT, padx=5)
        self.sort_var = tk.StringVar(value='Length')
        sort_combo = ttk.Combobox(filter_frame, textvariable=self.sort_var, 
                                 values=['Length', 'Alphabetical', 'Complexity'], width=15)
        sort_combo.pack(side=tk.LEFT, padx=5)
        sort_combo.bind('<<ComboboxSelected>>', lambda e: self.display_passwords())
        
        # Password display area
        self.passwords_text = scrolledtext.ScrolledText(passwords_frame, height=20, width=80,
                                                       bg='#1e1e1e', fg='#e0e0e0',
                                                       font=('Consolas', 10))
        self.passwords_text.pack(fill=tk.BOTH, expand=True)
        
        # Export buttons
        export_frame = ttk.Frame(passwords_frame)
        export_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(export_frame, text="💾 Save to File", 
                  command=self.save_to_file, style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="📋 Copy All", 
                  command=self.copy_all_passwords, style='Info.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="🎲 Copy Random", 
                  command=self.copy_random_password, style='Info.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="🔄 Refresh Display", 
                  command=self.display_passwords, style='Info.TButton').pack(side=tk.LEFT, padx=5)
        
    def create_status_bar(self, parent):
        """Create status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))
        
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(status_frame, textvariable=self.status_var, 
                 style='Normal.TLabel').pack(side=tk.LEFT)
        
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate', length=200)
        self.progress.pack(side=tk.RIGHT, padx=10)
        
    def load_preset(self, preset_name):
        """Load example presets"""
        presets = {
            "john": {
                "first_name": "john",
                "last_name": "doe",
                "birth_date": "15061990",
                "nickname": "johny",
                "spouse_name": "jane",
                "city": "newyork",
                "company": "techcorp",
                "sport": "football",
                "team": "cowboys",
                "movie": "action",
                "music": "rock",
                "game": "gaming"
            },
            "sarah": {
                "first_name": "sarah",
                "last_name": "smith",
                "birth_date": "22081985",
                "pet_name": "max",
                "city": "london",
                "sport": "tennis",
                "book": "mystery",
                "music": "pop",
                "hobby": "reading",
                "celebrity": "emma"
            },
            "manan": {
                "first_name": "manan",
                "last_name": "kamboj",
                "birth_date": "07092010",
                "nickname": "manu",
                "hometown": "delhi",
                "school": "dps",
                "sport": "cricket",
                "game": "gaming",
                "movie": "bollywood",
                "place": "goa",
                "hobby": "coding"
            }
        }
        
        if preset_name in presets:
            preset = presets[preset_name]
            self.first_name_var.set(preset.get("first_name", ""))
            self.last_name_var.set(preset.get("last_name", ""))
            self.birth_date_var.set(preset.get("birth_date", ""))
            self.nickname_var.set(preset.get("nickname", ""))
            self.spouse_name_var.set(preset.get("spouse_name", ""))
            self.child_name_var.set(preset.get("child_name", ""))
            self.pet_name_var.set(preset.get("pet_name", ""))
            self.city_var.set(preset.get("city", ""))
            self.hometown_var.set(preset.get("hometown", ""))
            self.company_var.set(preset.get("company", ""))
            self.school_var.set(preset.get("school", ""))
            self.sport_var.set(preset.get("sport", ""))
            self.team_var.set(preset.get("team", ""))
            self.movie_var.set(preset.get("movie", ""))
            self.music_var.set(preset.get("music", ""))
            self.book_var.set(preset.get("book", ""))
            self.game_var.set(preset.get("game", ""))
            self.celebrity_var.set(preset.get("celebrity", ""))
            self.place_var.set(preset.get("place", ""))
            self.hobby_var.set(preset.get("hobby", ""))
            self.lucky_num_var.set(preset.get("lucky_num", ""))
            
            messagebox.showinfo("Preset Loaded", f"Loaded '{preset_name}' preset!")
    
    def clear_all_fields(self):
        """Clear all input fields"""
        self.first_name_var.set("")
        self.last_name_var.set("")
        self.birth_date_var.set("")
        self.nickname_var.set("")
        self.spouse_name_var.set("")
        self.child_name_var.set("")
        self.pet_name_var.set("")
        self.city_var.set("")
        self.hometown_var.set("")
        self.company_var.set("")
        self.school_var.set("")
        self.sport_var.set("")
        self.team_var.set("")
        self.movie_var.set("")
        self.music_var.set("")
        self.book_var.set("")
        self.game_var.set("")
        self.celebrity_var.set("")
        self.place_var.set("")
        self.hobby_var.set("")
        self.lucky_num_var.set("")
        
    def generate_passwords_threaded(self):
        """Generate passwords in a separate thread to keep GUI responsive"""
        if self.generation_in_progress:
            return
        
        # Validate inputs
        if not self.first_name_var.get() or not self.last_name_var.get():
            messagebox.showerror("Error", "First name and last name are required!")
            return
        
        # Start generation in separate thread
        self.generation_in_progress = True
        self.progress.start()
        self.status_var.set("Generating passwords...")
        
        thread = threading.Thread(target=self.generate_passwords)
        thread.daemon = True
        thread.start()
        
        # Check thread completion
        self.root.after(100, self.check_generation_complete, thread)
    
    def check_generation_complete(self, thread):
        """Check if generation thread has completed"""
        if thread.is_alive():
            self.root.after(100, self.check_generation_complete, thread)
        else:
            self.progress.stop()
            self.generation_in_progress = False
    
    def generate_passwords(self):
        """Generate passwords based on user input"""
        try:
            # Prepare data for generator
            data = {
                'first_name': self.first_name_var.get().lower(),
                'last_name': self.last_name_var.get().lower(),
                'birth_date': self.birth_date_var.get(),
                'use_specials': self.use_specials_var.get(),
                'use_leet': self.use_leet_var.get(),
                'add_numbers': self.use_numbers_var.get(),
                'specials': list(self.specials_var.get())
            }
            
            # Add optional fields if they exist and are enabled
            if self.use_family_var.get():
                if self.nickname_var.get():
                    data['nickname'] = self.nickname_var.get().lower()
                if self.spouse_name_var.get():
                    data['spouse_name'] = self.spouse_name_var.get().lower()
                if self.child_name_var.get():
                    data['child_name'] = self.child_name_var.get().lower()
                if self.pet_name_var.get():
                    data['pet_name'] = self.pet_name_var.get().lower()
            
            # Add location info if enabled
            if self.use_location_var.get():
                if self.city_var.get():
                    data['city'] = self.city_var.get().lower()
                if self.hometown_var.get():
                    data['hometown'] = self.hometown_var.get().lower()
            
            # Add interests if enabled
            if self.use_interests_var.get():
                if self.sport_var.get():
                    data['sport'] = self.sport_var.get().lower()
                if self.team_var.get():
                    data['team'] = self.team_var.get().lower()
                if self.company_var.get():
                    data['company'] = self.company_var.get().lower()
                if self.school_var.get():
                    data['school'] = self.school_var.get().lower()
                # New interest fields
                if self.movie_var.get():
                    data['movie'] = self.movie_var.get().lower()
                if self.music_var.get():
                    data['music'] = self.music_var.get().lower()
                if self.book_var.get():
                    data['book'] = self.book_var.get().lower()
                if self.game_var.get():
                    data['game'] = self.game_var.get().lower()
                if self.celebrity_var.get():
                    data['celebrity'] = self.celebrity_var.get().lower()
                if self.place_var.get():
                    data['place'] = self.place_var.get().lower()
                if self.hobby_var.get():
                    data['hobby'] = self.hobby_var.get().lower()
                if self.lucky_num_var.get():
                    data['lucky_num'] = self.lucky_num_var.get().lower()
            
            # Generate passwords
            passwords = self.generator.generate_smart_combinations(data)
            
            # Filter based on options
            min_len = int(self.min_length_var.get())
            max_len = int(self.max_length_var.get())
            filtered = self.generator.analyze_and_filter(passwords, min_len, max_len)
            
            # Apply advanced filters
            advanced_options = {
                'exclude_similar': self.exclude_similar_var.get(),
                'exclude_sequential': self.exclude_sequential_var.get(),
                'avoid_repeats': self.avoid_repeats_var.get(),
                'require_uppercase': self.require_uppercase_var.get(),
                'require_lowercase': self.require_lowercase_var.get(),
                'require_digits': self.require_digits_var.get(),
                'require_special': self.require_special_var.get(),
                'min_strength': self.min_strength_var.get(),
                'max_repeat': self.max_repeat_var.get(),
                'min_uppercase': self.min_uppercase_var.get(),
                'min_digits': self.min_digits_var.get(),
                'min_special': self.min_special_var.get(),
            }
            
            filtered = self.generator.apply_advanced_filters(filtered, advanced_options)
            
            # Remove duplicates if enabled
            if self.filter_duplicates_var.get():
                filtered = set(filtered)
            
            # Limit number of passwords
            max_pwds = int(self.max_passwords_var.get())
            if len(filtered) > max_pwds:
                filtered = set(list(filtered)[:max_pwds])
            
            self.passwords = filtered
            
            # Update GUI in main thread
            self.root.after(0, self.update_output_display)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Generation Error", str(e)))
            self.root.after(0, lambda: self.status_var.set("Error occurred"))
    
    def update_output_display(self):
        """Update the output display with generated passwords"""
        self.display_passwords()
        self.update_statistics()
        self.status_var.set(f"Generated {len(self.passwords)} passwords")
        messagebox.showinfo("Success", f"Successfully generated {len(self.passwords)} passwords!")
    
    def display_passwords(self):
        """Display passwords in the text area"""
        self.passwords_text.delete(1.0, tk.END)
        
        if not self.passwords:
            self.passwords_text.insert(tk.END, "No passwords generated yet.\n")
            self.passwords_text.insert(tk.END, "Go to 'Generation Options' tab and click 'Generate Passwords'.")
            return
        
        # Filter passwords based on search
        search_term = self.search_var.get().lower()
        filtered_pwds = [pwd for pwd in self.passwords if search_term in pwd.lower()]
        
        # Sort passwords
        sort_by = self.sort_var.get()
        if sort_by == 'Length':
            sorted_pwds = sorted(filtered_pwds, key=lambda x: (len(x), x))
        elif sort_by == 'Complexity':
            sorted_pwds = sorted(filtered_pwds, 
                                key=lambda x: (sum(1 for c in x if c.isupper()) + 
                                               sum(1 for c in x if c.isdigit()) + 
                                               sum(1 for c in x if c in '!@#$%^&*'), 
                                               len(x)), 
                                reverse=True)
        else:  # Alphabetical
            sorted_pwds = sorted(filtered_pwds)
        
        # Display with formatting
        for i, pwd in enumerate(sorted_pwds, 1):
            # Color code based on complexity
            complexity = self.calculate_complexity(pwd)
            color = self.get_complexity_color(complexity)
            
            # Format line
            line = f"{i:4}. {pwd:30} "
            line += f"[L:{len(pwd):2}] "
            
            # Add indicators
            if any(c.isupper() for c in pwd):
                line += "U"
            if any(c.isdigit() for c in pwd):
                line += "N"
            if any(c in '!@#$%^&*' for c in pwd):
                line += "S"
            
            line += f" | {complexity}/10"
            
            # Insert with tag for color
            self.passwords_text.insert(tk.END, line + "\n", color)
        
        # Configure tags for colors
        for color in ['simple', 'medium', 'complex', 'strong']:
            self.passwords_text.tag_config(color, foreground=self.get_color_value(color))
    
    def calculate_complexity(self, password):
        """Calculate password complexity score (1-10)"""
        score = 0
        
        # Length score
        if len(password) >= 12:
            score += 3
        elif len(password) >= 8:
            score += 2
        elif len(password) >= 6:
            score += 1
        
        # Character variety
        if any(c.isupper() for c in password):
            score += 1
        if any(c.islower() for c in password):
            score += 1
        if any(c.isdigit() for c in password):
            score += 1
        if any(c in '!@#$%^&*' for c in password):
            score += 2
        
        # Pattern detection (penalize simple patterns)
        if password.lower() == self.first_name_var.get().lower() + self.last_name_var.get().lower():
            score -= 1
        if re.search(r'\d{4,}$', password):  # Long number sequence at end
            score += 1
        
        return min(max(score, 1), 10)
    
    def get_complexity_color(self, score):
        """Get color tag based on complexity score"""
        if score <= 3:
            return 'simple'
        elif score <= 5:
            return 'medium'
        elif score <= 7:
            return 'complex'
        else:
            return 'strong'
    
    def get_color_value(self, color_name):
        """Get color value for tags"""
        colors = {
            'simple': '#ff6b6b',  # Red
            'medium': '#ffa726',  # Orange
            'complex': '#42a5f5',  # Blue
            'strong': '#66bb6a'   # Green
        }
        return colors.get(color_name, '#e0e0e0')
    
    def filter_passwords(self, *args):
        """Filter displayed passwords based on search term"""
        self.display_passwords()
    
    def update_statistics(self):
        """Update statistics display"""
        self.stats_text.delete(1.0, tk.END)
        
        if not self.passwords:
            return
        
        # Calculate statistics
        total = len(self.passwords)
        lengths = [len(pwd) for pwd in self.passwords]
        avg_length = sum(lengths) / total if total > 0 else 0
        
        # Count patterns
        with_special = sum(1 for pwd in self.passwords if any(c in '!@#$%^&*' for c in pwd))
        with_numbers = sum(1 for pwd in self.passwords if any(c.isdigit() for c in pwd))
        with_upper = sum(1 for pwd in self.passwords if any(c.isupper() for c in pwd))
        with_lower = sum(1 for pwd in self.passwords if any(c.islower() for c in pwd))
        
        # Find most common patterns
        patterns = defaultdict(int)
        for pwd in self.passwords:
            if pwd.islower():
                patterns['all_lower'] += 1
            elif pwd.isupper():
                patterns['all_upper'] += 1
            elif pwd[0].isupper() and pwd[1:].islower():
                patterns['capitalized'] += 1
            elif any(c.isdigit() for c in pwd):
                patterns['has_numbers'] += 1
        
        # Display statistics
        self.stats_text.insert(tk.END, f"{'='*60}\n")
        self.stats_text.insert(tk.END, "PASSWORD GENERATION STATISTICS\n")
        self.stats_text.insert(tk.END, f"{'='*60}\n\n")
        
        self.stats_text.insert(tk.END, f"📊 Total Passwords: {total}\n")
        self.stats_text.insert(tk.END, f"📏 Average Length: {avg_length:.1f} characters\n")
        self.stats_text.insert(tk.END, f"📐 Length Range: {min(lengths)} - {max(lengths)} characters\n\n")
        
        self.stats_text.insert(tk.END, "🔤 CHARACTER DISTRIBUTION:\n")
        self.stats_text.insert(tk.END, f"  • With uppercase: {with_upper} ({with_upper/total*100:.1f}%)\n")
        self.stats_text.insert(tk.END, f"  • With lowercase: {with_lower} ({with_lower/total*100:.1f}%)\n")
        self.stats_text.insert(tk.END, f"  • With numbers: {with_numbers} ({with_numbers/total*100:.1f}%)\n")
        self.stats_text.insert(tk.END, f"  • With special: {with_special} ({with_special/total*100:.1f}%)\n\n")
        
        self.stats_text.insert(tk.END, "🎭 COMMON PATTERNS:\n")
        for pattern, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True)[:5]:
            percentage = count/total*100
            self.stats_text.insert(tk.END, f"  • {pattern.replace('_', ' ').title()}: {count} ({percentage:.1f}%)\n")
    
    def analyze_patterns(self):
        """Analyze input patterns and suggest improvements"""
        if not self.first_name_var.get() or not self.last_name_var.get():
            messagebox.showinfo("Analysis", "Please enter at least first and last name for analysis.")
            return
        
        # Create analysis report
        report = []
        report.append("="*60)
        report.append("PATTERN ANALYSIS REPORT")
        report.append("="*60)
        report.append("")
        
        # Analyze name patterns
        first = self.first_name_var.get().lower()
        last = self.last_name_var.get().lower()
        
        report.append("📝 NAME ANALYSIS:")
        report.append(f"  First name: {first}")
        report.append(f"  Last name: {last}")
        report.append(f"  Initials: {first[0]}{last[0]}")
        report.append("")
        
        # Predict common patterns
        report.append("🎯 PREDICTED COMMON PATTERNS:")
        report.append(f"  1. {first}{last}")
        report.append(f"  2. {first}{last}123")
        report.append(f"  3. {first.capitalize()}{last.capitalize()}")
        
        if self.birth_date_var.get():
            bdate = re.sub(r'[^\d]', '', self.birth_date_var.get())
            if len(bdate) >= 4:
                year = bdate[-4:] if len(bdate) >= 8 else bdate[-2:]
                report.append(f"  4. {first}{year}")
                report.append(f"  5. {last}{year}")
        
        report.append("")
        report.append("💡 RECOMMENDATIONS:")
        report.append("  • Avoid using only name + common numbers")
        report.append("  • Mix uppercase and lowercase letters")
        report.append("  • Include special characters (!@#$)")
        report.append("  • Use longer passwords (12+ characters)")
        
        # Show report
        messagebox.showinfo("Pattern Analysis", "\n".join(report))
    
    def save_to_file(self):
        """Save passwords to file"""
        if not self.passwords:
            messagebox.showerror("Error", "No passwords to save!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"passwords_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"# Smart Human Password Generator - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"# Generated for: {self.first_name_var.get().title()} {self.last_name_var.get().title()}\n")
                    f.write(f"# Total passwords: {len(self.passwords)}\n")
                    f.write("#" * 60 + "\n\n")
                    
                    # Sort passwords
                    sorted_pwds = sorted(self.passwords, key=lambda x: (len(x), x))
                    
                    for i, pwd in enumerate(sorted_pwds, 1):
                        f.write(f"{pwd}\n")
                
                messagebox.showinfo("Success", f"Saved {len(self.passwords)} passwords to:\n{filename}")
                self.status_var.set(f"Saved to {os.path.basename(filename)}")
                
            except Exception as e:
                messagebox.showerror("Save Error", f"Could not save file:\n{str(e)}")
    
    def copy_all_passwords(self):
        """Copy all passwords to clipboard"""
        if not self.passwords:
            messagebox.showerror("Error", "No passwords to copy!")
            return
        
        password_list = "\n".join(sorted(self.passwords, key=lambda x: (len(x), x)))
        self.root.clipboard_clear()
        self.root.clipboard_append(password_list)
        
        self.status_var.set(f"Copied {len(self.passwords)} passwords to clipboard")
        messagebox.showinfo("Copied", f"Copied {len(self.passwords)} passwords to clipboard!")
    
    def copy_random_password(self):
        """Copy a random password to clipboard"""
        if not self.passwords:
            messagebox.showerror("Error", "No passwords to copy!")
            return
        
        random_pwd = random.choice(list(self.passwords))
        self.root.clipboard_clear()
        self.root.clipboard_append(random_pwd)
        
        self.status_var.set("Copied random password to clipboard")
        messagebox.showinfo("Copied", f"Copied password: {random_pwd}")
    
    def run(self):
        """Run the GUI application"""
        self.root.mainloop()

def main():
    """Main function"""
    try:
        app = PasswordGeneratorGUI()
        app.run()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"Application failed to start:\n{str(e)}")

if __name__ == "__main__":
    main()