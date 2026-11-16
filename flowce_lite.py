# FlowCE Lite for TI-84 Evo / TI-84 Plus CE Python
# Ultra-lightweight CAS (<8 KB) for calculators with constrained free RAM.
import math, sys
try:
    import gc
    gc.collect()
except ImportError: pass
try:
    import ti_system
    import ti_draw
    HAS_TI = True
except ImportError: HAS_TI = False

def gcd(a, b):
    a, b = abs(int(a)), abs(int(b))
    while b: a, b = b, a % b
    return a

class Expr(object):
    def __add__(self, o): return _b(self, to_expr(o), '+')
    def __radd__(self, o): return _b(to_expr(o), self, '+')
    def __sub__(self, o): return _b(self, to_expr(o), '-')
    def __rsub__(self, o): return _b(to_expr(o), self, '-')
    def __mul__(self, o): return _b(self, to_expr(o), '*')
    def __rmul__(self, o): return _b(to_expr(o), self, '*')
    def __truediv__(self, o): return _b(self, to_expr(o), '/')
    def __rtruediv__(self, o): return _b(to_expr(o), self, '/')
    def __div__(self, o): return self.__truediv__(o)
    def __rdiv__(self, o): return self.__rtruediv__(o)
    def __pow__(self, o): return _b(self, to_expr(o), '^')
    def __rpow__(self, o): return _b(to_expr(o), self, '^')
    def __neg__(self): return self * Rational(-1, 1)
    def diff(self, v="x"): return diff(self, v)
    def integrate(self, v="x", a=None, b=None): return integrate(self, v, a, b)
    def simplify(self): return simplify(self)
    def subs(self, k, v=None):
        if v is None and isinstance(k, dict):
            r = self
            for sk, sv in k.items(): r = r.subs(sk, sv)
            return r
        return self._s(str(k), to_expr(v))
    def _s(self, k, v): return self
    def evalf(self, d=None): return float(self) if not d else self.subs(d).evalf()
    def f_syms(self): return set()
    @property
    def is_zero(self): return False
    @property
    def is_one(self): return False

def _b(a, b, op):
    if isinstance(a, Rational) and isinstance(b, Rational):
        if op == '+': return Rational(a.num * b.den + b.num * a.den, a.den * b.den)
        if op == '-': return Rational(a.num * b.den - b.num * a.den, a.den * b.den)
        if op == '*': return Rational(a.num * b.num, a.den * b.den)
        if op == '/':
            if b.num == 0: raise ZeroDivisionError("div 0")
            return Rational(a.num * b.den, a.den * b.num)
        if op == '^':
            if b.den == 1:
                p = b.num
                return Rational(a.num**p, a.den**p) if p >= 0 else Rational(a.den**(-p), a.num**(-p))
            return float_to_rational(float(a) ** float(b))
    if isinstance(a, Rational) and isinstance(b, (int, float)): return _b(a, to_expr(b), op)
    if isinstance(b, Rational) and isinstance(a, (int, float)): return _b(to_expr(a), b, op)
    if op == '+': return Add(a, b)
    if op == '-': return Sub(a, b)
    if op == '*': return Mul(a, b)
    if op == '/': return Div(a, b)
    if op == '^': return Pow(a, b)

class Rational(Expr):
    def __init__(self, n, d=1):
        if isinstance(n, str) and d == 1:
            p = n.split("/")
            if len(p) == 2: n, d = int(p[0].strip()), int(p[1].strip())
            else: r = float_to_rational(float(n)); n, d = r.num, r.den
        elif isinstance(n, Rational): n, d = n.num, n.den * int(d)
        elif isinstance(n, float) and d == 1: r = float_to_rational(n); n, d = r.num, r.den
        else: n, d = int(n), int(d)
        if d == 0: raise ZeroDivisionError("div 0")
        if d < 0: n, d = -n, -d
        g = gcd(n, d)
        self.num, self.den = n // g, d // g
    @property
    def is_zero(self): return self.num == 0
    @property
    def is_one(self): return self.num == 1 and self.den == 1
    def __float__(self): return float(self.num) / float(self.den)
    def __int__(self): return self.num // self.den
    def __eq__(self, o): return isinstance(o, Rational) and self.num == o.num and self.den == o.den
    def __str__(self): return str(self.num) if self.den == 1 else "%d/%d" % (self.num, self.den)
    def __repr__(self): return str(self)
    def evalf(self, d=None): return float(self.num) / float(self.den)

def float_to_rational(v, tol=1e-5):
    sign, v = (-1 if v < 0 else 1), abs(v)
    if abs(v - round(v)) < tol: return Rational(sign * int(round(v)), 1)
    p0, q0, p1, q1, x = 0, 1, 1, 0, v
    for _ in range(8):
        a = int(x)
        p2, q2 = a * p1 + p0, a * q1 + q0
        if q2 > 200: break
        p0, q0, p1, q1 = p1, q1, p2, q2
        if abs(v - float(p1) / float(q1)) < tol: return Rational(sign * p1, q1)
        d = x - a
        if d < 1e-9: break
        x = 1.0 / d
    return Rational(sign * p1, q1)

def to_expr(x):
    if isinstance(x, Expr): return x
    if isinstance(x, int): return Rational(x, 1)
    if isinstance(x, float): return Rational(int(x), 1) if x.is_integer() else float_to_rational(x)
    if isinstance(x, str): return parse(x)
    return x

class Symbol(Expr):
    def __init__(self, n): self.name = str(n).strip()
    def f_syms(self): return {self.name}
    def _s(self, k, v): return v if self.name == k else self
    def evalf(self, d=None):
        if d and self.name in d: return float(d[self.name])
        if self.name == "pi": return math.pi
        if self.name == "e": return math.e
        raise ValueError("Unbound: %s" % self.name)
    def __str__(self): return self.name
    def __repr__(self): return self.name
    def __eq__(self, o): return isinstance(o, Symbol) and self.name == o.name

class Nary(Expr):
    def __init__(self, *args):
        self.args = tuple(y for a in args for y in (to_expr(a).args if isinstance(to_expr(a), self.__class__) else (to_expr(a),)))
    def f_syms(self): return set().union(*[a.f_syms() for a in self.args])
    def _s(self, k, v): return self.__class__(*[a._s(k, v) for a in self.args])
    def __eq__(self, o): return isinstance(o, self.__class__) and self.args == o.args

class Add(Nary):
    def evalf(self, d=None): return sum(a.evalf(d) for a in self.args)
    def __str__(self):
        return " + ".join(str(a) for a in self.args).replace("+ -", "- ") if self.args else "0"

class Mul(Nary):
    def evalf(self, d=None):
        p = 1.0
        for a in self.args: p *= a.evalf(d)
        return p
    def __str__(self):
        return "*".join(("(%s)" % str(a) if isinstance(a, (Add, Sub)) else str(a)) for a in self.args) if self.args else "1"

class Binary(Expr):
    def __init__(self, l, r):
        self.left, self.right = to_expr(l), to_expr(r)
        self.args = (self.left, self.right)
    def f_syms(self): return self.left.f_syms() | self.right.f_syms()
    def _s(self, k, v): return self.__class__(self.left._s(k, v), self.right._s(k, v))
    def __eq__(self, o): return isinstance(o, self.__class__) and self.left == o.left and self.right == o.right

class Sub(Binary):
    def evalf(self, d=None): return self.left.evalf(d) - self.right.evalf(d)
    def __str__(self):
        sr = "(%s)" % str(self.right) if isinstance(self.right, (Add, Sub)) else str(self.right)
        return "%s - %s" % (str(self.left), sr)

class Div(Binary):
    @property
    def num(self): return self.left
    @property
    def den(self): return self.right
    def evalf(self, d=None):
        dv = self.right.evalf(d)
        if dv == 0: raise ZeroDivisionError("div 0")
        return self.left.evalf(d) / dv
    def __str__(self):
        sn = "(%s)" % str(self.left) if isinstance(self.left, (Add, Sub)) else str(self.left)
        sd = "(%s)" % str(self.right) if isinstance(self.right, (Add, Sub, Mul, Div)) else str(self.right)
        return "%s/%s" % (sn, sd)

class Pow(Binary):
    @property
    def base(self): return self.left
    @property
    def exp(self): return self.right
    def evalf(self, d=None): return self.left.evalf(d) ** self.right.evalf(d)
    def __str__(self):
        sb = "(%s)" % str(self.left) if isinstance(self.left, (Add, Sub, Mul, Div)) else str(self.left)
        se = "(%s)" % str(self.right) if isinstance(self.right, (Add, Sub, Mul, Div)) else str(self.right)
        return "%s^%s" % (sb, se)

class Function(Expr):
    def __init__(self, name, arg): self.name, self.arg, self.args = name, to_expr(arg), (to_expr(arg),)
    def f_syms(self): return self.arg.f_syms()
    def _s(self, k, v): return Function(self.name, self.arg._s(k, v))
    def evalf(self, d=None):
        v, n = self.arg.evalf(d), self.name
        if n == "sin": return math.sin(v)
        if n == "cos": return math.cos(v)
        if n == "tan": return math.tan(v)
        if n == "exp": return math.exp(v)
        if n == "ln": return math.log(v)
        if n == "sqrt": return math.sqrt(v)
        if n == "abs": return abs(v)
        raise ValueError(n)
    def __str__(self): return "%s(%s)" % (self.name, str(self.arg))
    def __eq__(self, o): return isinstance(o, Function) and self.name == o.name and self.arg == o.arg

Sin = lambda a: Function("sin", a)
Cos = lambda a: Function("cos", a)
Tan = lambda a: Function("tan", a)
Exp = lambda a: Function("exp", a)
Ln = lambda a: Function("ln", a)
Sqrt = lambda a: Function("sqrt", a)
Abs = lambda a: Function("abs", a)

_KF = {"sin": Sin, "cos": Cos, "tan": Tan, "exp": Exp, "ln": Ln, "sqrt": Sqrt, "abs": Abs}
_KC = {"pi": math.pi, "e": math.e}

def _tokenize(s):
    toks, i, n = [], 0, len(s)
    while i < n:
        c = s[i]
        if c <= ' ': i += 1; continue
        if c.isdigit() or (c == '.' and i + 1 < n and s[i+1].isdigit()):
            j = i + 1
            while j < n and (s[j].isdigit() or s[j] == '.'): j += 1
            toks.append(('N', s[i:j])); i = j
        elif c.isalpha() or c == '_':
            j = i + 1
            while j < n and (s[j].isalnum() or s[j] == '_'): j += 1
            toks.append(('I', s[i:j])); i = j
        elif s[i:i+2] == '**': toks.append(('O', '^')); i += 2
        elif c in '+-*/^(),': toks.append(('O', c)); i += 1
        else: raise SyntaxError(c)
    return toks

def _iim(t):
    r = []
    for i in range(len(t)):
        r.append(t[i])
        if i + 1 < len(t):
            t1, t2 = t[i], t[i+1]
            c1 = t1[0] == 'N' or t1[1] == ')' or (t1[0] == 'I' and t1[1].lower() not in _KF)
            c2 = t2[0] in ('N', 'I') or t2[1] == '('
            if c1 and c2: r.append(('O', '*'))
    return r

class _P(object):
    def __init__(self, t): self.t, self.p = t, 0
    def peek(self): return self.t[self.p] if self.p < len(self.t) else ('E', '')
    def get(self): tok = self.peek(); self.p += 1; return tok
    def parse_e(self, mp=1):
        left = self.parse_p()
        while self.peek()[0] == 'O':
            op = self.peek()[1]
            pr = 1 if op in '+-' else (2 if op in '*/' else (4 if op == '^' else 0))
            if pr < mp: break
            self.get()
            right = self.parse_e(pr if op == '^' else pr + 1)
            left = _b(left, right, op)
        return left
    def parse_p(self):
        tok = self.peek()
        if tok == ('O', '+'): self.get(); return self.parse_p()
        if tok == ('O', '-'): self.get(); return Mul(Rational(-1, 1), self.parse_e(3))
        if tok[0] == 'N': self.get(); return Rational(tok[1])
        if tok == ('O', '('):
            self.get(); e = self.parse_e(1)
            if self.get() != ('O', ')'): raise SyntaxError(')')
            return e
        if tok[0] == 'I':
            self.get(); name, low = tok[1], tok[1].lower()
            if self.peek() == ('O', '('):
                self.get(); arg = self.parse_e(1)
                if self.get() != ('O', ')'): raise SyntaxError(')')
                if low in _KF: return _KF[low](arg)
                return Function(name, arg)
            return Symbol(low) if low in _KC else Symbol(name)
        raise SyntaxError(str(tok))

def parse(s):
    if not s or not str(s).strip(): return None
    t = _iim(_tokenize(str(s).strip()))
    p = _P(t)
    tree = p.parse_e(1)
    if p.p < len(t): raise SyntaxError("dangling")
    return tree

def _sct(e):
    if isinstance(e, Rational): return e, Rational(1, 1)
    if isinstance(e, Mul):
        c, r = Rational(1, 1), []
        for a in e.args:
            if isinstance(a, Rational): c = c * a
            else: r.append(a)
        return c, (Rational(1, 1) if not r else (r[0] if len(r) == 1 else Mul(*r)))
    return Rational(1, 1), e

def simplify(e):
    e = to_expr(e)
    if isinstance(e, (Rational, Symbol)): return e
    if isinstance(e, Add):
        terms, c_sum, t_map = [], Rational(0, 1), []
        for a in e.args:
            sa = simplify(a)
            if isinstance(sa, Add): terms.extend(sa.args)
            else: terms.append(sa)
        for t in terms:
            c, k = _sct(t)
            if k == Rational(1, 1): c_sum = c_sum + c
            else:
                for item in t_map:
                    if item[0] == k: item[1] = item[1] + c; break
                else: t_map.append([k, c])
        res = [k if c == Rational(1, 1) else (Mul(Rational(-1, 1), k) if c == Rational(-1, 1) else Mul(c, k)) for k, c in t_map if c.num]
        if c_sum.num or not res: res.append(c_sum)
        return res[0] if len(res) == 1 else Add(*res)
    if isinstance(e, Sub): return simplify(Add(e.left, Mul(Rational(-1, 1), e.right)))
    if isinstance(e, Mul):
        factors, coeff, b_map = [], Rational(1, 1), []
        for a in e.args:
            sa = simplify(a)
            if isinstance(sa, Mul): factors.extend(sa.args)
            else: factors.append(sa)
        for f in factors:
            if isinstance(f, Rational): coeff = coeff * f
            else:
                b, p = (f.base, f.exp) if isinstance(f, Pow) else (f, Rational(1, 1))
                for item in b_map:
                    if item[0] == b: item[1] = simplify(Add(item[1], p)); break
                else: b_map.append([b, p])
        if coeff.num == 0: return Rational(0, 1)
        res = [b if p == Rational(1, 1) else Pow(b, p) for b, p in b_map if not (isinstance(p, Rational) and p.is_zero)]
        if not res: return coeff
        return res[0] if len(res) == 1 and coeff.is_one else Mul(coeff, *res)
    if isinstance(e, Div):
        sn, sd = simplify(e.num), simplify(e.den)
        if isinstance(sd, Rational) and sd.is_zero: raise ZeroDivisionError("div 0")
        if isinstance(sn, Rational) and sn.is_zero: return Rational(0, 1)
        if isinstance(sd, Rational) and sd.is_one: return sn
        if isinstance(sn, Rational) and isinstance(sd, Rational): return sn / sd
        if sn == sd: return Rational(1, 1)
        return Div(sn, sd)
    if isinstance(e, Pow):
        sb, se = simplify(e.base), simplify(e.exp)
        if isinstance(se, Rational) and se.is_zero: return Rational(1, 1)
        if isinstance(se, Rational) and se.is_one: return sb
        if isinstance(sb, Rational) and isinstance(se, Rational): return sb ** se
        return Pow(sb, se)
    if isinstance(e, Function):
        sa = simplify(e.arg)
        if isinstance(sa, Rational) and sa.is_zero and e.name in ("sin", "tan"): return Rational(0, 1)
        if isinstance(sa, Rational) and sa.is_zero and e.name in ("cos", "exp"): return Rational(1, 1)
        return Function(e.name, sa)
    return e

def diff(e, v="x"):
    e, vs = to_expr(e), str(v).strip()
    return simplify(_dn(e, vs))

def _dn(n, v):
    if isinstance(n, Rational): return Rational(0, 1)
    if isinstance(n, Symbol): return Rational(1, 1) if n.name == v else Rational(0, 1)
    if isinstance(n, Add): return Add(*[_dn(a, v) for a in n.args])
    if isinstance(n, Sub): return Sub(_dn(n.left, v), _dn(n.right, v))
    if isinstance(n, Mul):
        return Add(*[Mul(*[n.args[j] if i != j else _dn(n.args[j], v) for j in range(len(n.args))]) for i in range(len(n.args))])
    if isinstance(n, Div):
        u, d = n.num, n.den
        return Div(Sub(Mul(_dn(u, v), d), Mul(u, _dn(d, v))), Pow(d, Rational(2, 1)))
    if isinstance(n, Pow):
        b, e = n.base, n.exp
        if v not in e.f_syms(): return Mul(e, Pow(b, Sub(e, Rational(1, 1))), _dn(b, v))
        if v not in b.f_syms(): return Mul(n, Function("ln", b), _dn(e, v))
        return Mul(n, Add(Mul(_dn(e, v), Function("ln", b)), Div(Mul(e, _dn(b, v)), b)))
    if isinstance(n, Function):
        a, da, nm = n.arg, _dn(n.arg, v), n.name
        if nm == "sin": return Mul(Function("cos", a), da)
        if nm == "cos": return Mul(Rational(-1, 1), Function("sin", a), da)
        if nm == "exp": return Mul(Function("exp", a), da)
        if nm == "ln": return Div(da, a)
    return Rational(0, 1)

def integrate(e, v="x", a=None, b=None):
    e, vs = to_expr(e), str(v).strip()
    if a is not None and b is not None:
        fa, fb = float(a), float(b)
        if fa == fb: return Rational(0, 1)
        F = integrate(e, vs)
        return F.subs(vs, fb).evalf() - F.subs(vs, fa).evalf()
    return simplify(_in(e, vs))

def _in(n, v):
    sy = Symbol(v)
    if isinstance(n, Rational): return Mul(n, sy)
    if isinstance(n, Symbol): return Mul(Rational(1, 2), Pow(sy, Rational(2, 1))) if n.name == v else Mul(n, sy)
    if isinstance(n, Add): return Add(*[_in(a, v) for a in n.args])
    if isinstance(n, Sub): return Sub(_in(n.left, v), _in(n.right, v))
    if isinstance(n, Mul):
        c, k = _sct(n)
        if c != Rational(1, 1): return Mul(c, _in(k, v))
    if isinstance(n, Pow) and isinstance(n.base, Symbol) and n.base.name == v:
        if isinstance(n.exp, Rational) and n.exp == Rational(-1, 1): return Function("ln", sy)
        ne = simplify(Add(n.exp, Rational(1, 1)))
        return Div(Pow(sy, ne), ne)
    if isinstance(n, Div) and isinstance(n.num, Rational) and isinstance(n.den, Symbol) and n.den.name == v:
        return Mul(n.num, Function("ln", sy))
    if isinstance(n, Function) and isinstance(n.arg, Symbol) and n.arg.name == v:
        if n.name == "sin": return Mul(Rational(-1, 1), Function("cos", sy))
        if n.name == "cos": return Function("sin", sy)
        if n.name == "exp": return Function("exp", sy)
    return Mul(n, sy)

MENU_ITEMS = [
    "1. Differentiate  (d/dx)",
    "2. Integrate      (S dx)",
    "3. Simplify Expression",
    "4. Evaluate / Subs",
    "5. Interactive Shell",
]

def draw_gui_menu(selected=0):
    if not HAS_TI: return
    try:
        ti_draw.clear()
        ti_draw.set_color(18, 48, 88)
        ti_draw.fill_rect(0, 0, 320, 24)
        ti_draw.set_color(40, 140, 230)
        ti_draw.fill_rect(0, 24, 320, 2)
        ti_draw.set_color(255, 255, 255)
        ti_draw.draw_text(8, 6, "FlowCE Lite CAS")
        ti_draw.set_color(120, 200, 255)
        ti_draw.draw_text(210, 6, "v1.1 [Evo Edition]")
        ti_draw.set_color(25, 30, 42)
        ti_draw.fill_rect(8, 28, 304, 182)
        ti_draw.set_color(45, 55, 75)
        ti_draw.draw_rect(8, 28, 304, 182)
        for i, item in enumerate(MENU_ITEMS):
            y = 38 + i * 26
            if i == selected:
                ti_draw.set_color(38, 75, 125)
                ti_draw.fill_rect(12, y - 2, 296, 22)
                ti_draw.set_color(255, 255, 255)
            else:
                ti_draw.set_color(200, 215, 235)
            ti_draw.draw_text(16, y, item)
        ti_draw.set_color(14, 20, 30)
        ti_draw.fill_rect(0, 214, 320, 26)
        ti_draw.set_color(160, 200, 240)
        ti_draw.draw_text(8, 220, "[1-5] Select | [^/v] Move | [CLEAR] Exit")
    except Exception: pass

def draw_result_screen(title, query, result):
    if not HAS_TI:
        print("--- %s ---\nInput:  %s\nResult: %s" % (str(title), str(query), str(result)))
        return
    try:
        ti_draw.clear()
        ti_draw.set_color(18, 48, 88)
        ti_draw.fill_rect(0, 0, 320, 24)
        ti_draw.set_color(40, 140, 230)
        ti_draw.fill_rect(0, 24, 320, 2)
        ti_draw.set_color(255, 255, 255)
        ti_draw.draw_text(8, 6, "FlowCE Lite - " + str(title)[:24])
        ti_draw.set_color(25, 30, 42)
        ti_draw.fill_rect(8, 28, 304, 182)
        ti_draw.set_color(40, 140, 230)
        ti_draw.draw_rect(8, 28, 304, 182)
        ti_draw.set_color(130, 165, 205)
        ti_draw.draw_text(16, 36, "Input:")
        ti_draw.set_color(255, 255, 255)
        ti_draw.draw_text(16, 54, str(query)[:36])
        ti_draw.set_color(45, 55, 75)
        ti_draw.draw_line(16, 76, 296, 76)
        ti_draw.set_color(80, 220, 140)
        ti_draw.draw_text(16, 88, "Result:")
        ti_draw.set_color(255, 255, 255)
        rs = str(result)
        ti_draw.draw_text(16, 108, rs[:36])
        if len(rs) > 36: ti_draw.draw_text(16, 128, rs[36:72])
        if len(rs) > 72: ti_draw.draw_text(16, 148, rs[72:108])
        ti_draw.set_color(18, 48, 88)
        ti_draw.fill_rect(0, 214, 320, 26)
        ti_draw.set_color(220, 235, 255)
        ti_draw.draw_text(8, 220, "[ENTER] / [CLEAR] Return to Menu")
        ti_system.get_key(1)
    except Exception: pass

def prompt_ti_input(title, prompt, default_val=""):
    if HAS_TI:
        try:
            ti_system.disp_clr()
            ti_system.disp_at(1, "--- " + str(title) + " ---", "center")
            ti_system.disp_at(3, str(prompt))
            if default_val: ti_system.disp_at(5, "[Default: " + str(default_val) + "]")
        except Exception: pass
    try:
        val = input(prompt).strip()
    except Exception: val = ""
    return val if val else default_val

def run_action(idx):
    try:
        if idx == 0:
            f = prompt_ti_input("Differentiate", "f(x) = ")
            if not f or f.lower() in ("q", "menu", "exit"): return
            v = prompt_ti_input("Differentiate", "var [x] = ", "x")
            res = diff(f, v)
            draw_result_screen("Derivative", "d/d" + v + "(" + f + ")", str(res))
        elif idx == 1:
            f = prompt_ti_input("Integrate", "f(x) = ")
            if not f or f.lower() in ("q", "menu", "exit"): return
            v = prompt_ti_input("Integrate", "var [x] = ", "x")
            la = prompt_ti_input("Integrate", "lower lim [none] = ", "")
            if la:
                lb = prompt_ti_input("Integrate", "upper lim = ", "")
                res = integrate(f, v, la, lb)
                draw_result_screen("Definite Integral", "S[" + la + ".." + lb + "] " + f + " d" + v, str(res))
            else:
                res = integrate(f, v)
                draw_result_screen("Indefinite Integral", "S " + f + " d" + v, str(res) + " + C")
        elif idx == 2:
            f = prompt_ti_input("Simplify", "expr = ")
            if not f or f.lower() in ("q", "menu", "exit"): return
            res = simplify(parse(f))
            draw_result_screen("Simplify", f, str(res))
        elif idx == 3:
            f = prompt_ti_input("Evaluate", "expr = ")
            if not f or f.lower() in ("q", "menu", "exit"): return
            x_val = prompt_ti_input("Evaluate", "x = ", "1")
            val = float(x_val) if '.' in x_val else int(x_val)
            res = to_expr(f).subs("x", val).evalf()
            draw_result_screen("Evaluate", f + " @ x=" + x_val, str(res))
        elif idx == 4:
            run_interactive_shell()
    except Exception as err:
        draw_result_screen("Error", "Execution Error", str(err))
    finally:
        try: gc.collect()
        except Exception: pass

def run_interactive_shell():
    if HAS_TI:
        try:
            ti_system.disp_clr()
            ti_system.disp_at(1, "FlowCE Lite Terminal", "center")
            ti_system.disp_at(3, "Type 'menu' to return")
        except Exception: pass
    print("FlowCE Lite Terminal. Type expression or 'menu' to return.")
    while True:
        try:
            line = input("CAS> ").strip()
            if not line: continue
            if line.lower() in ("menu", "quit", "exit", "q"): break
            lower = line.lower()
            if lower.startswith("diff "):
                parts = line[5:].split()
                var = parts[1] if len(parts) > 1 else "x"
                print("= %s" % str(diff(parts[0], var)))
            elif lower.startswith("int "):
                parts = line[4:].split()
                var = parts[1] if len(parts) > 1 else "x"
                print("= %s + C" % str(integrate(parts[0], var)))
            elif lower.startswith("sim "):
                print("= %s" % str(simplify(parse(line[4:]))))
            else:
                print("= %s" % str(simplify(parse(line))))
            try: gc.collect()
            except Exception: pass
        except (KeyboardInterrupt, EOFError): break
        except Exception as err: print("Error: %s" % str(err))

def run_ti_gui():
    selected = 0
    num_opts = len(MENU_ITEMS)
    while True:
        draw_gui_menu(selected)
        try: k = ti_system.get_key(1)
        except Exception: k = ti_system.disp_wait()
        if k == "" or k is None: break
        if k in (82, '1'): run_action(0)
        elif k in (83, '2'): run_action(1)
        elif k in (84, '3'): run_action(2)
        elif k in (72, '4'): run_action(3)
        elif k in (73, '5'): run_action(4)
        elif k in (25, 'up'): selected = (selected - 1) % num_opts
        elif k in (35, 'down'): selected = (selected + 1) % num_opts
        elif k in (105, 95, 'enter', '\n'): run_action(selected)
        elif k in (45, 'clear', 'esc', 'exit', 'q'): break
    try:
        ti_draw.clear()
        ti_system.disp_clr()
    except Exception: pass

def run_pc_cli():
    print("FlowCE Lite CAS (TI-84 Evo)")
    for item in MENU_ITEMS: print(" " + item)
    print(" [q] Exit")
    while True:
        try:
            choice = input("\nSelect [1-5, q]: ").strip().lower()
            if not choice: continue
            if choice in ("q", "quit", "exit"): break
            if choice in ("1", "2", "3", "4", "5"):
                run_action(int(choice) - 1)
            else:
                print("= %s" % str(simplify(parse(choice))))
        except (KeyboardInterrupt, EOFError): break
        except Exception as err: print("Error: %s" % str(err))

def main():
    if HAS_TI: run_ti_gui()
    else: run_pc_cli()

if __name__ == "__main__":
    main()
