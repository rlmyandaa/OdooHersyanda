def check_table_pos(func):
    """Decorator to check whether command should be ignored or not.
    Command will only executed if the robot is properly placed in the table
    """

    def inner(self):
        if not self.is_properly_placed:
            return None
        else:
            # Execute function first, then check whether the function execution is valid
            # (within the table boundary area)
            func(self)
            return self._check_out_of_bound()

    return inner
