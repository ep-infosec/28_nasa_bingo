# Ignoring some linting rules in tests
# pylint: disable=missing-docstring
import pytest
import numpy as np
from bingo.chromosomes.chromosome import Chromosome
from bingo.variation.var_or import VarOr


@pytest.fixture
def dummy_chromosome(mocker):
    mocker.patch('bingo.chromosomes.chromosome.Chromosome', autospec=True)
    mocker.patch.object(Chromosome, "__abstractmethods__",
                        new_callable=set)
    return Chromosome


@pytest.fixture
def dummy_population(dummy_chromosome):
    return [dummy_chromosome(fitness="replication") for _ in range(5)]


@pytest.fixture
def dummy_crossover(mocker, dummy_chromosome):
    crossover_cromosome = dummy_chromosome(fitness="crossover")
    return mocker.Mock(return_value=(crossover_cromosome,
                                     crossover_cromosome),
                       last_crossover_types=("default", "default"))


@pytest.fixture
def dummy_mutation(mocker, dummy_chromosome):
    mutation_chromosome = dummy_chromosome(fitness="mutation")
    return mocker.Mock(return_value=mutation_chromosome,
                       last_mutation_type="default")


def test_set_crossover_and_mutation_types(dummy_mutation, dummy_crossover):
    var_or = VarOr(dummy_crossover, dummy_mutation, 0.4, 0.4)
    assert var_or.crossover_types == dummy_crossover.types
    assert var_or.mutation_types == dummy_mutation.types


@pytest.mark.parametrize("cx_prob", [-0.1, 1.1, 0.6])
@pytest.mark.parametrize("mut_prob", [-0.1, 1.1, 0.6])
def test_invalid_probabilities(mocker, cx_prob, mut_prob):
    crossover = mocker.Mock()
    mutation = mocker.Mock()
    with pytest.raises(ValueError):
        _ = VarOr(crossover, mutation, cx_prob, mut_prob)


def test_probabilities_are_about_right(dummy_population, dummy_crossover,
                                       dummy_mutation):
    np.random.seed(0)
    variation = VarOr(dummy_crossover, dummy_mutation, 0.5, 0.3)
    offspring = variation(dummy_population, 1000)

    source = [individual.fitness for individual in offspring]
    assert source.count("replication") == 205
    assert source.count("crossover") == 487
    assert source.count("mutation") == 308


def test_diagnostics_source(dummy_population, dummy_crossover, dummy_mutation):
    variation = VarOr(dummy_crossover, dummy_mutation, 0.5, 0.3)
    offspring = variation(dummy_population, 100)

    for off, cross, mut in zip(offspring, variation.crossover_offspring_type,
                               variation.mutation_offspring_type):
        if off.fitness == "replication":
            assert not cross and not mut
        elif off.fitness == "crossover":
            assert cross == "default" and not mut
        elif off.fitness == "mutation":
            assert not cross and mut == "default"


def test_diagnostics_parents(dummy_population, dummy_crossover,
                             dummy_mutation):
    variation = VarOr(dummy_crossover, dummy_mutation, 0.5, 0.3)
    _ = variation(dummy_population, 100)

    for parents, cross, mut in zip(variation.offspring_parents,
                                   variation.crossover_offspring_type,
                                   variation.mutation_offspring_type):
        if cross:
            assert len(parents) == 2
        else:
            assert len(parents) == 1
        assert max(parents) < 5 and min(parents) >= 0


def test_offspring_is_not_parent(dummy_population, dummy_crossover,
                                 dummy_mutation):
    variation = VarOr(dummy_crossover, dummy_mutation, 0., 0.)
    offspring = variation(dummy_population, 25)

    for indv in enumerate(offspring):
        assert indv not in offspring
