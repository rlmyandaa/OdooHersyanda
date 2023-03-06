from odoo.exceptions import ValidationError


class ProperPositionException(ValidationError):
    """
    Exception for when the object position is going to be out off table boundary.
    """
    pass


class TestingException(Exception):
    """
    Custom exception for unittest purpose. Using this exception so that it could
    return back error as dictionary.
    """

    def __init__(self, error_data):
        self.error_data = error_data
