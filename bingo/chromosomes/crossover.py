"""The genetic operation of crossover.

This module defines the basis of crossover in bingo evolutionary analyses.
"""

from abc import ABCMeta, abstractmethod


class Crossover(metaclass=ABCMeta):
    """Crossover for chromosomes.

    An abstract base class for the crossover between two genetic individuals
    in bingo.
    """
    @abstractmethod
    def __call__(self, parent_1, parent_2):
        """Crossover between two individuals

        Parameters
        ----------
        parent_1 : Chromosome
                   The first parent individual
        parent_2 : Chromosome
                   The second parent individual

        Returns
        -------
        tuple(Chromosome, Chromosome) :
            The two children from the crossover.
        """
        raise NotImplementedError
