"""Argumentation engine (Part 1) and strategic argumentation (Part 2)."""

from .framework import ArgumentationFramework
from .semantics import (grounded_extension, grounded_trace, complete_extensions,
                        preferred_extensions, stable_extensions,
                        semi_stable_extensions, admissible_sets, all_extensions)
from .labelling import (legal_labellings, is_legal_labelling, extension_to_labelling,
                        extensions_via_labellings, format_labelling)
from .acceptance import acceptance_status, acceptance_report
from .strategic import (grounded_mechanism, utility, best_responses,
                        satisfies_theorem_5_3, is_strategyproof,
                        theorem_5_4_condition, is_strategyproof_by_theorem_5_4)
from .generator import random_instance
