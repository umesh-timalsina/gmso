from typing import Optional, Any, Union

import unyt as u
from pydantic import Field, validator

from gmso.abc.abstract_potential import AbstractPotential
from gmso.utils.expression import _PotentialExpression
from gmso.utils.decorators import confirm_dict_existence
from gmso.exceptions import GMSOError


class ParametricPotential(AbstractPotential):
    __base_doc__ = """A parametric potential class.

    Potential stores a general interaction between components of a chemical
    topology that can be specified by a mathematical expression. The functional
    form of the potential is stored as a `sympy` expression and the parameters
    are stored explicitly. This class is agnostic to the instantiation of the
    potential, which can be e.g. a non-bonded potential, a bonded potential, an
    angle potential, a dihedral potential, etc. and is designed to be inherited
    by classes that represent these potentials.
    """

    # FIXME: Use proper forward referencing??
    topology_: Optional[Any] = Field(
        None,
        description="the topology of which this potential is a part of"
    )

    set_ref_: Optional[str] = Field(
        None,
        description='The string name of the bookkeeping set in gmso.Topology class. '
                    'This is used to track property based hashed object\'s '
                    'changes so that a dictionary/set can keep track of them'
    )

    def __init__(self,
                 name="ParametricPotential",
                 expression='a*x+b',
                 parameters=None,
                 potential_expression=None,
                 independent_variables=None,
                 topology=None,
                 **kwargs
                 ):
        if potential_expression is not None \
                and (expression is not None
                     or independent_variables is not None
                     or parameters is not None):
            raise ValueError(
                'When using potential expressions '
                'please do not provide arguments for '
                'expression, independent_variables or parameters.'
            )
        if potential_expression is None:
            if expression is None:
                expression = 'a*x+b'

            if parameters is None:
                parameters = {
                    'a': 1.0 * u.dimensionless,
                    'b': 1.0 * u.dimensionless
                }

            if independent_variables is None:
                independent_variables = {'x'}

            _potential_expression = _PotentialExpression(
                expression=expression,
                independent_variables=independent_variables,
                parameters=parameters
            )
        else:
            _potential_expression = potential_expression

        super().__init__(
            name=name,
            potential_expression=_potential_expression,
            topology=topology,
            **kwargs
        )

    @property
    def parameters(self):
        """Optional[dict]\n\tThe parameters of the `Potential` expression and their corresponding values, as `unyt` quantities"""
        return self.potential_expression_.parameters

    @property
    def topology(self):
        return self.__dict__.get('topology_')

    @property
    def set_ref(self):
        return self.__dict__.get('set_ref_')

    @validator('topology_')
    def is_valid_topology(cls, value):
        if value is None:
            return None
        else:
            from gmso.core.topology import Topology
            if not isinstance(value, Topology):
                raise TypeError(f'{type(value).__name__} is not of type Topology')
        return value

    @confirm_dict_existence
    def __setattr__(self, key: Any, value: Any) -> None:
        if key == 'parameters':
            self.potential_expression_.parameters = value
        else:
            super().__setattr__(key, value)

    @confirm_dict_existence
    def set_expression(self, expression=None, parameters=None, independent_variables=None):
        """Set the expression, parameters, and independent variables for this potential.

        Parameters
        ----------
        expression: sympy.Expression or string
            The mathematical expression corresponding to the potential
            If None, the expression remains unchanged
        parameters: dict
            {parameter: value} in the expression
            If None, the parameters remain unchanged

        Notes
        -----
        Be aware of the symbols used in the `expression` and `parameters`.
        If unnecessary parameters are supplied, an error is thrown.
        If only a subset of the parameters are supplied, they are updated
        while the non-passed parameters default to the existing values
       """
        self.potential_expression_.set(
            expression=expression,
            independent_variables=independent_variables,
            parameters=parameters
        )

    def dict(
            self,
            *,
            include: Union['AbstractSetIntStr', 'MappingIntStrAny'] = None,
            exclude: Union['AbstractSetIntStr', 'MappingIntStrAny'] = None,
            by_alias: bool = False,
            skip_defaults: bool = None,
            exclude_unset: bool = False,
            exclude_defaults: bool = False,
            exclude_none: bool = False
    ) -> dict:
        exclude = {'topology_', 'set_ref_'}
        return super().dict(
            include=include,
            exclude=exclude,
            by_alias=True,
            skip_defaults=skip_defaults,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none
        )

    @classmethod
    def from_template(cls, potential_template, parameters, topology=None):
        """Create a potential object from the potential_template

        Parameters
        ----------
        potential_template : gmso.lib.potential_templates.PotentialTemplate,
                            The potential template object
        parameters : dict,
                    The parameters of the potential object to create
        topology : gmso.Topology, default=None
                   The topology to which the created potential object belongs to

        Returns
        -------
        gmso.ParametricPotential
            The potential object created

        Raises
        ------
        GMSOError
            If potential_template is not of instance PotentialTemplate
        """
        from gmso.lib.potential_templates import PotentialTemplate
        if not isinstance(potential_template, PotentialTemplate):
            raise GMSOError(f'Object {type(potential_template)} is not an instance of PotentialTemplate.')

        return cls(name=potential_template.name,
                   expression=potential_template.expression,
                   independent_variables=potential_template.independent_variables,
                   parameters=parameters,
                   topology=topology)

    class Config:
        fields = {
            'topology_': 'topology',
            'set_ref_': 'set_ref'
        }
        alias_to_fields = {
            'topology': 'topology_'
        }
        validate_assignment = True
