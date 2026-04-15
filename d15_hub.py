"""
d15_hub — MIND-side re-export of the canonical D15 Hub module.

Allows native_cycle_engine.py and other root-level modules to::

    from d15_hub import D15Hub

without path gymnastics.
"""

try:
    from hf_deployment.elpidaapp.d15_hub import *          # noqa: F401,F403
    from hf_deployment.elpidaapp.d15_hub import D15Hub     # explicit for readers
except ImportError:
    # Running inside the elpidaapp package (e.g. HuggingFace Spaces)
    from elpidaapp.d15_hub import *                         # noqa: F401,F403
    from elpidaapp.d15_hub import D15Hub                    # noqa: F811
