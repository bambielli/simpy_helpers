# Simpy Helpers

The `simpy_helpers` package was written to make building simulations and collecting statistics about simulations using the [Simpy](https://simpy.readthedocs.io/en/latest/) framework simpler. 

`simpy_helpers` provides 4 main classes: 

1. Entity
2. Resource
3. Source
4. Stats

These building blocks allow you to build complex simulations quickly, while hiding much of the necessary orchestration of simpy components hidden from the user.

Entity, Resource and Source are `abstract classes`. Read the API documentation to learn which methods are required for building a simulation.

## Why Not Just Use Simpy Directly?

Simpy is not that simple to learn and use... 
- Simpy Helpers hides much of this complexity from end users, so they can focus on building simulations instead of orchestrating simpy.

Simpy does not collect statistics for you...
- Simpy Helpers provides a `Stats` class which collects relevant statistics about your simulation automatically e.g. utilization of resources

## API Documentation

See the [Using_Simpy_Helpers_Package.ipynb](./Using_Simpy_Helpers_Package.ipynb) notebook for more detail, and a walkthrough of a simple M/M/K simulation using helper classes.
