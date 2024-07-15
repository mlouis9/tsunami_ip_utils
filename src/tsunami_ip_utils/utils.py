import re
import numpy as np
from uncertainties import ufloat
from pathlib import Path
from typing import Callable
import functools

def isotope_reaction_list_to_nested_dict(isotope_reaction_list, field_of_interest):
    """Converts a list of dictionaries containing isotope-reaction pairs (and some other key that represents a value of
    interest, e.g. an sdf profile or a contribution) to a nested dictionary
    
    Parameters
    ----------
    - isotope_reaction_list: list of dict, list of dictionaries containing isotope-reaction pairs and some other key
    - field_of_interest: str, the key in the dictionary that represents the value of interest

    Returns
    -------
    - nested_dict: dict, nested dictionary containing the isotope-reaction pairs and the value of interest"""

    isotope_reaction_dict = {}

    def get_atomic_number(isotope):
        matches = re.findall(r'\d+', isotope)
        return int(matches[0] if matches else -1) # Return -1 if no atomic number is found, these isotopes will be sorted last
                                                  # Should only be applicable to carbon in ENDF 7.1
    
    # Sort isotopes by atomic number so plots will have similar colors across different calls
    all_isotopes = list(set([isotope_reaction['isotope'] for isotope_reaction in isotope_reaction_list]))
    all_isotopes.sort(key=get_atomic_number)
    isotope_reaction_dict = { isotope: {} for isotope in all_isotopes }

    for isotope_reaction in isotope_reaction_list:
        isotope = isotope_reaction['isotope']
        reaction = isotope_reaction['reaction_type']
        value = isotope_reaction[field_of_interest]

        isotope_reaction_dict[isotope][reaction] = value

    return isotope_reaction_dict

def filter_redundant_reactions(data_dict, redundant_reactions=['chi', 'capture', 'nubar', 'total']):
    """Filters out redundant reactions from a nested isotope-reaction dictionary
    
    Parameters
    ----------
    - data_dict: dict, nested dictionary containing isotope-reaction pairs
    - redundant_reactions: list of str, list of reactions to filter out"""
    return { isotope: { reaction: data_dict[isotope][reaction] for reaction in data_dict[isotope] \
                        if reaction not in redundant_reactions } for isotope in data_dict }

def filter_by_nuclie_reaction_dict(data_dict, nuclide_reactions):
    """Filters out isotopes that are not in the nuclide_reactions dictionary
    
    Parameters
    ----------
    - data_dict: dict, nested dictionary containing isotope-reaction pairs
    - nuclide_reactions: dict, dictionary containing isotopes and their reactions"""
    return {nuclide: {reaction: xs for reaction, xs in reactions.items() if reaction in nuclide_reactions[nuclide]} \
                        for nuclide, reactions in data_dict.items() if nuclide in nuclide_reactions.keys()}


def parse_ufloats(array_of_strings):
    """ Parses a 2D array of strings into a 2D array of ufloats, assuming zero uncertainty if '+/-' is not found. """
    def to_ufloat(s):
        if isinstance(s, float):
            return ufloat(s, s)
        
        parts = s.split('+/-')
        if len(parts) == 2:
            value, error = parts
        else:
            value = s
            error = 0
        return ufloat(float(value), float(error))
    
    return np.vectorize(to_ufloat)(array_of_strings)

def convert_paths(func: Callable) -> Callable:
    """
    Decorator to ensure that any list argument passed to the decorated function,
    which contains strings, has those strings converted to pathlib.Path objects.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        new_args = []
        for arg in args:
            if isinstance(arg, list):
                # Convert all string items in the list to Path objects
                new_arg = [Path(item) if isinstance(item, str) else item for item in arg]
                new_args.append(new_arg)
            else:
                new_args.append(arg)
        
        new_kwargs = {k: [Path(item) if isinstance(item, str) else item for item in v] if isinstance(v, list) else v
                      for k, v in kwargs.items()}
        
        return func(*new_args, **new_kwargs)
    
    return wrapper