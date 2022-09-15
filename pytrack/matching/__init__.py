# This lets you use package.module.Class as package.Class in your code.
from .candidate import Candidate

# This lets Sphinx know you want to document package.module.Class as package.Class.
__all__ = ['Candidate']