"""
docstrings_example.py - This module is an example of how you should write docstrings. 
It will provide an example of module docstrings, class docstrings, and function docstrings. 

Classes: 
ExampleClass : class that is an example of a class

Functions: 
example_function : accepts an int and a str, and returns a dictionary of those parameters

Author: Michael Ke
Version: 1.0
Date Last Modified: August 25th, 2022
"""

class ExampleClass(): 
    """
    ExampleClass - this class serves as an example of a class, and is used to illustrate
    the types of docstrings that are needed to describe a class. 

    Attributes:
    parameter : integer value that is an integer

    Methods: 
    example_simple_method : return sum of parameter and parameter2
    example_complex_method : return a list of elements with the value of parameter
    """

    def __init__(self, parameter : int) -> None: 
        self.parameter = parameter
    
    def example_simple_method(self, parameter2: int) -> int:
        """Add int to self.parameter"""
        return (self.parameter + parameter2)
    
    def example_complex_method(self, parameter2: int) -> list:
        """
        Return a list of elements with the value of self.parameter
        
        Parameters: 
        parameter2 : number of elements the returned list should have
        Returns: 
        listy_mclistface : list of length parameter2 of self.parameter
        """
        
        listy_mclistface = []
        for i in range(parameter2):
            listy_mclistface.append(self.parameter)
        return listy_mclistface

def example_function(parameter1 : int, parameter2: str) -> dict: 
    """
    Return a dictionary of the supplied parameters with the names of their type

    Parameters: 
    parameter1 : integer that is an integer
    parameter2 : string that is a string

    Return: 
    dictionary_mcdictionaryface : dictionary of supplied parameters
    """

    dictionary_mcdictionaryface = {}
    dictionary_mcdictionaryface['int'] = parameter1
    dictionary_mcdictionaryface['str'] = parameter2

    return dictionary_mcdictionaryface

#Simple functions can use a one-liner doc-string