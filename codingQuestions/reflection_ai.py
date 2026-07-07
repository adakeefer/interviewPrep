'''
function to synthesize math functions

simplify(x + x) = 2x

1. data structure for math expression
2. function (ds) -> simplified (ds)

input: numbers and just 1 variable. +-/*. sin/cos. polynomials. others.

'''

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from fractions import Fraction
from typing import Tuple


class Expr(ABC):
    """Base class for every expression node. Frozen + hashable throughout."""

    @abstractmethod
    def children(self) -> Tuple["Expr", ...]:
        """Direct child sub-expressions, in evaluation order. Empty for leaves."""
        raise NotImplementedError


# ---- leaves ---------------------------------------------------------------

@dataclass(frozen=True)
class Num(Expr):
    value: Fraction  # exact rational; keeps simplify from drifting into floats

    def children(self) -> Tuple[Expr, ...]:
        return ()


@dataclass(frozen=True)
class Var(Expr):
    def children(self) -> Tuple[Expr, ...]:
        return ()


class Const(Enum):
    PI = auto()
    E = auto()


@dataclass(frozen=True)
class Constant(Expr):
    which: Const

    def children(self) -> Tuple[Expr, ...]:
        return ()


# ---- commutative, variadic -------------------------------------------------

@dataclass(frozen=True)
class Add(Expr):
    terms: Tuple[Expr, ...]

    def children(self) -> Tuple[Expr, ...]:
        return self.terms


@dataclass(frozen=True)
class Mul(Expr):
    factors: Tuple[Expr, ...]

    def children(self) -> Tuple[Expr, ...]:
        return self.factors


# ---- non-commutative, binary ----------------------------------------------

@dataclass(frozen=True)
class Sub(Expr):
    left: Expr
    right: Expr

    def children(self) -> Tuple[Expr, ...]:
        return (self.left, self.right)


@dataclass(frozen=True)
class Div(Expr):
    numerator: Expr
    denominator: Expr

    def children(self) -> Tuple[Expr, ...]:
        return (self.numerator, self.denominator)


@dataclass(frozen=True)
class Pow(Expr):
    base: Expr
    exponent: Expr

    def children(self) -> Tuple[Expr, ...]:
        return (self.base, self.exponent)


# ---- unary ------------------------------------------------------------------

@dataclass(frozen=True)
class Neg(Expr):
    operand: Expr

    def children(self) -> Tuple[Expr, ...]:
        return (self.operand,)


# ---- generic function node -------------------------------------------------

class FnName(Enum):
    SIN = auto()
    COS = auto()
    TAN = auto()
    ASIN = auto()
    ACOS = auto()
    ATAN = auto()
    LN = auto()
    EXP = auto()
    SQRT = auto()
    ABS = auto()


@dataclass(frozen=True)
class Function(Expr):
    name: FnName
    arg: Expr

    def children(self) -> Tuple[Expr, ...]:
        return (self.arg,)


# ---- calculus ---------------------------------------------------------------

@dataclass(frozen=True)
class Derivative(Expr):
    expr: Expr
    order: int = 1  # d^order/dx^order; single variable, so no var field needed

    def children(self) -> Tuple[Expr, ...]:
        return (self.expr,)


'''

2x + 2x

(Mul(Num(Fraction(4)), Var())

simplifyForAdd() -> 2x, 2x
op1, op2 = simplifyForAdd(node)
if op1.isValid and op2.isValid
    return op1.val + op2.val, var

simplifyForDerivative() -> 

Add((Mul((Num(Fraction(2)), Var())), Mul((Num(Fraction(2)), Var()))))

* at each node:
* terminal? var, num -> return val
* else: 
    res = visit (child in children)
    case MUL:
        return child * child
    
        -> 2x



sin(x)/cos(x) - x^2
Sub(
    Div(Function(FnName.SIN, Var()), Function(FnName.COS, Var())),
    Pow(Var(), Num(Fraction(2)))
)

d/dx(x^3)
Derivative(Pow(Var(), Num(Fraction(3))), order=1)

2x + 2x
2x * 2x

x^3 * x^-2

1/3 + 2/3 


* variables must be in the subtree
* eval subtrees without variables

* exponentionation
* addition/subtraction w/variable (only matters if they are the same degree x^2 x^2)


* Needs:

** simplifying function rules
** 





'''


def simplify(Expr e) -> Expr:
