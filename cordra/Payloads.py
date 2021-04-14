from pathlib import Path

from . import aslist

class Payloads():
    def __init__(self, names=None, filenames=None):
        """
        Class initialization
        
        Parameters
        ----------
        names : str or list, optional
            The name(s) to assign to the payload(s).  If given, must
            give equal numbers of filenames.
        filenames : str or list, optional
            The filename(s) of the payload(s). If given, must give
            equal numbers of names.
        
        Raises
        ------
        AssertionError
            If equal numbers of names and filenames are not given.
        """
        self.__names = []
        self.__filenames = []
        
        if names is not None or filenames is not None:
            assert names is not None and filenames is not None
            names = aslist(names)
            filenames = aslist(filenames)
            assert len(names) == len(filenames)
            
            for name, filename in zip(names, filenames):
                self.add_payload(name, filename)
        
    def add_payload(self, name, filename):
        """
        Adds a payload listing.
        
        Parameters
        ----------
        name : str
            The name to assign to the payload.
        filename : str
            The filename of the payload.
        
        Raises
        ------
        ValueError
            If a matching payload name already exists
        """
        if name in self.__names:
            raise ValueError(f'A payload named {name} is already set')
        self.__names.append(name)
        self.__filenames.append(filename)
    
    def update_payload(self, name, filename):
        """
        Allows for the file associated with a payload to be changed.
        
        Parameters
        ----------
        name : str
            The name of the payload to change.
        filename : str
            The new filename for the payload.
        
        Raises
        ------
        ValueError
            If a payload with the given name doesn't exist
        """
        i = self.__names.index(name)
        self.__filenames[i] = filename
        
    
    def json(self):
        """
        Generates the JSON content for the payloads
        """
        out = {}
        for name, filename in zip(self.__names, self.__filenames):
            out[name] = (Path(filename).name, open(filename,'rb'))
        
        return out