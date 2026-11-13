# E2E Test Infra: FlowCE Calculator CAS

## Test Philosophy
- Opaque-box, requirement-driven testing for the pure Python FlowCE CAS on TI-84 Plus CE Python.
- Headless PC execution utilizing pure-Python mocks of proprietary TI hardware modules (`ti_system`, `ti_draw`, `ti_plotlib`, `ti_hub`).
- Strict syntax and AST compatibility verification enforcing Python 3.4 / CircuitPython constraints (zero f-strings, zero `re`, zero external dependencies).
- Methodology: Category-Partition + Boundary Value Analysis (BVA) + Pairwise Combinatorial Testing + AP Calculus Workload Testing.

---

## Feature Inventory
| # | Feature | Source (Requirement) | Tier 1 (Min 5) | Tier 2 (Min 5) | Tier 3 (Pairwise) | Tier 4 (Workloads) |
|---|---------|----------------------|:--------------:|:--------------:|:-----------------:|:------------------:|
| F1 | TI Hardware Mocks | ORIGINAL_REQUEST R3, Survey R3 | 5 | 5 | ✓ | ✓ |
| F2 | Syntax & AST Compatibility | ORIGINAL_REQUEST R2, Survey R2 | 5 | 5 | ✓ | ✓ |
| F3 | Lexer & Precedence Parser | ORIGINAL_REQUEST R2, Survey R2 | 5 | 5 | ✓ | ✓ |
| F4 | Exact Rational Arithmetic | ORIGINAL_REQUEST R2, Survey R2 | 5 | 5 | ✓ | ✓ |
| F5 | Algebraic Simplification | ORIGINAL_REQUEST R2, Survey R2 | 5 | 5 | ✓ | ✓ |
| F6 | Symbolic Differentiation | ORIGINAL_REQUEST R2, Survey R2 | 5 | 5 | ✓ | ✓ |
| F7 | Step-by-Step Explanations | ORIGINAL_REQUEST R2, Survey R2 | 5 | 5 | ✓ | ✓ |
| F8 | Symbolic & Definite Integration | ORIGINAL_REQUEST R2, Survey R2 | 5 | 5 | ✓ | ✓ |
| F9 | Limits & Series | ORIGINAL_REQUEST R2, Survey R2 | 5 | 5 | ✓ | ✓ |
| F10 | Tangent & Normal Lines | ORIGINAL_REQUEST R2, Survey R2 | 5 | 5 | ✓ | ✓ |
| F11 | Dual-Mode CLI & Module API | ORIGINAL_REQUEST R2, Survey R2 | 5 | 5 | ✓ | ✓ |

---

## Test Architecture
- **Test Runner**: Standard `pytest` or `python3 -m unittest discover tests` executable directly on PC.
- **Pass/Fail Semantics**: All test assertions must pass with exit code 0. No unhandled exceptions or crashes.
- **Directory Layout**:
  ```
  /workspaces/test/
  ├── ti_system.py           # TI system mock module (disp_clr, disp_at, get_key, etc.)
  ├── ti_draw.py             # TI draw mock module (clear, draw_line, draw_text, etc.)
  ├── ti_plotlib.py          # TI plotlib mock module (window, axes, plot, show_plot, etc.)
  ├── ti_hub.py              # TI hub mock module (connect, sleep, etc.)
  └── tests/
      ├── __init__.py
      ├── test_derivatives.py        # Tier 1-3 symbolic differentiation tests
      ├── test_integrals.py          # Tier 1-3 symbolic/definite integration & FTC tests
      ├── test_simplification.py     # Tier 1-3 algebraic simplification & rational arithmetic
      ├── test_limits_algebra.py     # Tier 1-3 limits, series, tangent lines, algebra
      ├── test_ti_compat.py          # Tier 1-3 TI hardware mock imports and dual-mode CLI tests
      ├── test_syntax.py             # AST validator: zero f-strings, zero re, pure Python 3.4
      └── test_real_world.py         # Tier 4 AP Calculus real-world scenarios
  ```

---

## Real-World Application Scenarios (Tier 4)
| # | Scenario | Features Exercised | Complexity |
|---|----------|--------------------|------------|
| S1 | Kinematics Physics Pipeline ($s(t) \to v(t) = s'(t) \to a(t) = v'(t)$, net distance $\int |v(t)| dt$) | F3, F4, F5, F6, F8 | High |
| S2 | Tangent & Normal Line to Curve at Point ($y - f(c) = f'(c)(x-c)$, perpendicular slope $-1/f'(c)$) | F3, F5, F6, F10 | Medium |
| S3 | Area Between Two Curves ($\int_a^b (f(x) - g(x)) dx$, e.g., $y = x^2$ and $y = 2x$) | F3, F4, F5, F8 | High |
| S4 | Taylor Polynomial Approximation ($T_n(x) = \sum \frac{f^{(k)}(0)}{k!} x^k$ for $\sin(x)$ or $e^x$) | F3, F5, F6, F9 | High |
| S5 | Indeterminate Limits via L'Hôpital's Rule ($\lim_{x \to 0} \frac{\sin(x)}{x} = \lim \frac{\cos(x)}{1} = 1$) | F3, F5, F6, F9 | Medium |
| S6 | Optimization Problem (find critical points where $f'(x) = 0$, test concavity via $f''(x)$) | F3, F5, F6, F10 | Medium |

---

## Coverage Thresholds
- **Tier 1 (Feature Coverage)**: $\ge 5$ isolated tests per feature ($11 \times 5 = 55$ minimum tests).
- **Tier 2 (Boundary & Corner Cases)**: $\ge 5$ boundary tests per feature ($11 \times 5 = 55$ minimum tests: empty inputs, division by zero, zero exponent, negative bases, deep nesting, constant expressions).
- **Tier 3 (Cross-Feature Combinations)**: $\ge 15$ tests covering pairwise feature interactions (e.g., differentiating an integral, limit of a derivative, simplification of an integral result, tangent line on rational function).
- **Tier 4 (Real-World Applications)**: $\ge 6$ comprehensive AP Calculus / physics application scenarios.
- **Syntax / AST Verifier**: Automated check enforcing zero `JoinedStr` (f-strings) and zero `re` usage across `flowce.py` and mocks.
- **Total Minimum Test Count**: $\ge 130$ test assertions.
