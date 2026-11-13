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

## 🛠️ Resolving `MemoryError` on TI-84 Evo / CE

Graphing calculators like the TI-84 Evo and TI-84 Plus CE Python share **154 KB of total RAM** between OS variables (TI-BASIC programs, lists L1–L6, matrices, pictures) and the sandboxed MicroPython execution heap. If your free RAM is low, MicroPython cannot allocate enough compiler buffer space and will raise:
```text
MemoryError: memory allocation failed, allocating ... bytes
```

### Quick Fix Steps:

1. **Check Your Available RAM:**
   * Press `[2nd]` + `[+]` (MEM).
   * Select `2:Mem Management/Delete...`.
   * Check the number next to **`RAM FREE`**. If it is below ~60–80 KB, your RAM is cluttered with other calculator data.

2. **Archive Unused Programs & Variables to Flash ROM:**
   * In `Mem Management/Delete...`, select `7:Program...` (or `1:All...`).
   * Scroll to programs, matrices, or large lists and press `[enter]` to toggle the **Archive** status (an asterisk `*` appears next to archived items).
   * *Note:* Archived programs and data are safely stored in your 3 MB Flash ROM and do not consume active RAM!

3. **Reset the Python Environment:**
   * If you recently ran another script in Python, exit the Python App completely to release the MicroPython shell memory, then relaunch it.

4. **Choose the Right Edition for Your Device:**
   * **`flowce.py` (Standard Edition, ~36 KB)**: Full CAS engine with step-by-step differentiation explanations, Taylor series, limits/L'Hôpital's rule, and calculus geometry (tangent/normal lines). Recommended when you have $\ge 70$ KB of free RAM.
   * **[`flowce_lite.py`](flowce_lite.py) (Lite Edition, ~18 KB)**: Streamlined, ultra-compact CAS engine with exact fractions, symbolic differentiation, symbolic & definite integrals, algebraic simplification, and interactive REPL. Recommended for memory-constrained environments or when you have many active variables in RAM.

---

## 📲 Installation on TI-84 Evo / CE

1. Connect your TI-84 Evo or TI-84 Plus CE Python to your computer via USB-C.
2. Open **TI Connect CE**.
3. Drag and drop [`flowce.py`](flowce.py) (or [`flowce_lite.py`](flowce_lite.py)) onto your calculator.
4. On the calculator:
   * Press **[prgm]**
   * Select **Python**
   * Select **`FLOWCE`** (or **`FLOWCELI`**) and press **[enter]** to run.

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
