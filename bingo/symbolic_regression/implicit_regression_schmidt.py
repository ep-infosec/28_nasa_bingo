"""
Implicit Regression, Adapted from Schmidt and Lipson papers

Fitness in this method is the difference of partial derivatives pairs
calculated with the data and the input `Equation` individual.

This may not be a correct implementation of this algorithm.  Importantly,
it couldn't reproduce the  results in the papers. Currently, there is no effort
to maintain functionality of this module.
"""
import numpy as np

from bingo.evaluation.fitness_function import VectorBasedFunction


class ImplicitRegressionSchmidt(VectorBasedFunction):
    """ Implicit Regression, Adapted from Schmidt and Lipson papers

    Fitness in this method is the difference of partial derivatives pairs
    calculated with the data and the input `Equation` individual.

    See "Symbolic Regression of Implicit Equations" by Michael Schmidt
    and Hod Lipson for more info.

    Parameters
    ----------
    training_data : ImplicitTrainingData
        data that is used in fitness evaluation.  Must have attributes x and
        dx_dt.
    """
    def evaluate_fitness_vector(self, individual):
        r"""Evaluates the fitness of an implicit individual

        Evaluates the fitness of the input Equation individual based on
        the ratio of partial derivatives between pairs of variables.

        fitness = :math:`-\frac{1}{N} \sum_{i=1}^N \log \left(1 + |
        \frac{\Delta x_i}{\Delta y_i} + \frac{\delta x_i}{\delta y_i}| \right)`
        for each :math:`x` and :math:`y` pair in training_data.x where
        :math:`N` is the length of the training_data,
        :math:`\frac{\Delta x_i}{\Delta y_i} = \frac{dx/dt}{dy/dt}` from
        training_data.dx_dt, and :math:`\frac{\delta x_i}{\delta y_i} =
        \frac{\delta f / \delta y}{\delta f / \delta x}` from the input
        Equation individual's output on training_data.x.

        Parameters
        ----------
        individual : Equation
            individual whose fitness is evaluated on `training_data`

        Returns
        -------
        float
            the fitness of the input Equation individual
        """
        _, df_dx = individual.evaluate_equation_with_x_gradient_at(
            x=self.training_data.x)

        num_parameters = self.training_data.x.shape[1]
        worst_fitness = 0
        diff_worst = np.full((num_parameters, ), np.inf)
        for i in range(num_parameters):
            for j in range(num_parameters):
                if i != j:
                    df_dxi = np.copy(df_dx[:, i])
                    df_dxj = np.copy(df_dx[:, j])
                    dxi_dxj_2 = (self.training_data.dx_dt[:, i] /
                                 self.training_data.dx_dt[:, j])
                    for k in range(num_parameters):
                        if k not in (i, j):
                            df_dxj += df_dx[:, k] * \
                                      self.training_data.dx_dt[:, k] / \
                                      self.training_data.dx_dt[:, j]

                    dxi_dxj_1 = df_dxj / df_dxi
                    diff = np.log(1. + np.abs(dxi_dxj_1 + dxi_dxj_2))
                    fit = np.mean(diff)
                    if np.isfinite(fit) and fit > worst_fitness:
                        diff_worst = np.copy(diff)
                        worst_fitness = fit
        return diff_worst
