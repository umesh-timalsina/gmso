from functools import wraps


def confirm_dict_existence(setter_function):
    """This decorator confirms that any core type
     member is in the topology's set (if it is used to
    wrap setters of the core type member class)
    """
    @wraps(setter_function)
    def setter_with_dict_removal(self, *args, **kwargs):
        if self._topology:
            self._topology._set_refs[self._set_ref].pop(self, None)
            prev_associations = self._topology._association_refs[self._set_ref].pop(self, set())
            setter_function(self, *args, **kwargs)
            self._topology._set_refs[self._set_ref][self] = (self)
            self._topology._association_refs[self._set_ref][self] = prev_associations
        else:
            setter_function(self, *args, **kwargs)
    return setter_with_dict_removal
