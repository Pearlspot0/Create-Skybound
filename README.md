# FlowCE for TI-84 Evo / TI-84 Plus CE Python

A pure-Python rewrite of the **FlowCE** Computer Algebra System (CAS), engineered specifically for the **TI-84 Evo** and **TI-84 Plus CE Python** graphing calculators.

---

## 🌟 Overview

The original FlowCE CAS was written in native eZ80 C / Assembly. With newer OS protections and new hardware platforms like the TI-84 Evo, running native C/ASM binaries requires complex jailbreak workarounds. 

This repository provides **FlowCE Python Edition**—a clean, self-contained, high-performance pure-Python CAS engine that runs natively inside Texas Instruments' MicroPython / CircuitPython environment without requiring jailbreaks, custom OS patches, or external dependencies.

---

## 🚀 Key Features

* **Strict Hardware Compatibility**: Built for the Python 3.4 / CircuitPython baseline on TI graphing calculators:
  * Zero f-strings (uses `%` string formatting).
  * Zero `re` regex engine dependencies (features custom lexer and recursive-descent parser).
  * 100% standard library; runs within calculator memory limits.
* **Exact Rational Arithmetic**: Fractions and coefficients remain exact (e.g. `1/3`, `9/2`, `-5/4`) instead of losing precision to floating-point decimals.
* **Symbolic Differentiation**:
  * Power rule, product rule, quotient rule, and chain rule.
  * Trigonometric (`sin`, `cos`, `tan`), exponential (`exp`), logarithmic (`ln`, `log`), and polynomial terms.
  * Step-by-step differentiation explanations (`diff_steps()`).
* **Symbolic & Definite Integration**:
  * Exact antiderivatives and definite integration via Fundamental Theorem of Calculus.
  * Numerical Riemann sum approximations (`riemann_sum()`).
* **Limits & Taylor Series**:
  * Limits via direct substitution, algebraic factoring, and L'Hôpital's rule steps.
  * Maclaurin and Taylor polynomial expansions to order $n$.
* **Calculus Geometry**:
  * Tangent line and normal line calculations at point $x = c$.
* **Dual-Mode UI / CLI**:
  * Direct calculator LCD display support via `ti_system` and `ti_draw`.
  * Fallback to terminal REPL and CLI batch flags on PC.

---

## 📲 Installation on TI-84 Evo / CE

1. Connect your TI-84 Evo or TI-84 Plus CE Python to your computer via USB-C.
2. Open **TI Connect CE** (or your preferred calculator file manager).
3. Transfer [`flowce.py`](flowce.py) to your calculator's Python app storage.
4. On the calculator:
   * Press **[prgm]**
   * Select **Python**
   * Select **`FLOWCE`** and press **[enter]** to run.

---

## 💻 Running & Testing on PC

### CLI Usage
You can run and test `flowce.py` directly from the terminal:

```bash
# Symbolic differentiation
python3 flowce.py --diff "x^3 + sin(x)" x
# Output: 3*x^2 + cos(x)

# Symbolic integration
python3 flowce.py --int "3*x^2 + cos(x)" x
# Output: x^3 + sin(x)

# Algebraic simplification
python3 flowce.py --sim "2*x + 3*x - x + 5 - 2"
# Output: 4*x + 3
```

### Python API
```python
import flowce

# Step-by-step derivative
steps = flowce.diff_steps("sin(x^2)", "x")
for s in steps:
    print(s)

# Tangent line to y = x^2 at x = 2
print(flowce.tangent_line("x^2", "x", 2))
# Output: 4*x - 4

# Normal line to y = x^2 at x = 2
print(flowce.normal_line("x^2", "x", 2))
# Output: -1/4*x + 9/2
```

### Automated PC Test Suite
Hardware mocks for TI proprietary modules (`ti_system`, `ti_draw`, `ti_plotlib`, `ti_hub`) are included in the repository so you can test headlessly on PC:

```bash
pytest -v
```

All 134 automated unit and property tests cover:
- Syntax & AST compliance (Python 3.4 enforcement)
- TI hardware mock verification
- Lexer & Precedence Parser
- Exact Rational Arithmetic
- Algebraic Simplification
- Derivatives, Integrals & Step-by-Step solutions
- Limits, Series & Calculus Geometry
- Tier 4 AP Calculus & Kinematics Physics Scenarios

---

## 📁 Repository Structure

* `flowce.py` - Core standalone Python CAS engine for TI-84 Evo.
* `ti_system.py`, `ti_draw.py`, `ti_plotlib.py`, `ti_hub.py` - TI hardware mock modules for PC testing.
* `tests/` - Comprehensive test suite (134 tests).
* `TEST_INFRA.md` - Test architecture and coverage documentation.
* `minecraft_mod/` - Archived files from the prior Create: Skybound Minecraft mod project.
