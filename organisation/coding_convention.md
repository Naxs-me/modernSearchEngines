# Coding Convention
## Docstring
We are using the Google Docstring format.

Consider augmenting functions, especially the important ones, with short and informative
Docstrings.

## Type annotations
Each function should be annotated with the types of its arguments and the return type.
This helps code readability, catching some mistakes early and supports the development. [PEP 484](https://peps.python.org/pep-0484/) has the details of type hints.

### APIs must be documented including type annotations and docstrings.

## Tools to help
Consider using a plugin to help generate docstrings.
For example the [autoDocstring](https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring) plugin for VS Code. Make sure to set the Docstring Format to "google".

[Mypy](https://mypy-lang.org/) is a powerful static type checker for python. 
It catches typing problems and warns about them, but does not influence the runtime behaviour of python.
It can be used as a seperate tool (see [getting started](https://mypy.readthedocs.io/en/stable/getting_started.html)) or in a plugin ([Mypy for VS Code](https://marketplace.visualstudio.com/items?itemName=matangover.mypy)). See the installation instructions.

## Final thoughts
Documentation can help the development process. However, considering the time and scope of the project, we should prioritize _working_ code over _well documented_ code.
