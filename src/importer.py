"""
importer.py

Contains the root class for importers, who fetch data from external data
sources and add them to the database.
"""


class ImporterException(Exception):
    pass



class Importer(object):
    
    def import_data(self):
        """
        Does the importing; throws ImporterException on error.
        Must be transactional.
        """

        raise NotImplementedError('Method must be defined in subclass')
