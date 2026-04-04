"""
Polynomial module

A full set of functions and operations on polynomial class

Features:
    1. Visit and edit a polynomial through index
    2. Judge whether two polynomials are equivalent or not
    3. Basic operations: +, -, *, /
    4. Advanced operations: power, derivative, evaluate
    5. Additional functions: GCD, LCM
"""

def simp(coeff):
    """
    Remove the leading 0's of a list of coefficients
    
    :param coeff: the list of coefficients of a polynomial, where index i
        corresponds with x^i
    :type coeff: list[int | float]
    :return: a coefficient list where leading 0's are removed
    :rtype: list[int | float]
    
    :raises TypeError: if coeff is not a list
        
    .. math::
        P(x) = a_0 + a_1 x + a_2 x^2 + ... + a_n x^n
    """

    if not isinstance(coeff, list):
        raise TypeError

    if not coeff:
        return [0]
    while coeff[-1] == 0 and len(coeff) > 1:
        coeff.pop()
    return coeff


class Polynomial:
    """
    Polynomial class
    
    Expression: coeff corresponds with polynomial
    P(x) = coeff[0] + coeff[1] x + coeff[2] x^2 + ... + coeff[-1] x^(len(coeff)-1)
    
    Attributes:
        coeff (list): Coefficient list, ascending order
        
    Examples:
        >>> p = Polynomial([1, 2, 3])
        3*x^2 + 2*x + 1
        >>> p.deg()
        2
        >>> p.evaluate(2)
        17
    """

    def __init__(self, coeff):
        self.coeff = simp(coeff)

    def deg(self):
        """
        The degree of a polynomial
        
        :param self: a polynomial
        :type self: Polynomial
        :return: the degree of the polynomial
        :rtype: int
        """

        return len(self.coeff) - 1

    def __getitem__(self, i):
        """
        Get the coefficient of x^i in the polynomial
        
        :param self: Polynomial
        :param i: int

        :note: if index out of range, returns 0.
        """

        try:
            return self.coeff[i]
        except IndexError:
            return 0

    def __setitem__(self, i, target):
        """
        Change a particular coefficient
        
        :param self: Polynomial
        :param i: int
        :param target: int, float
        """

        if not isinstance(target, (int, float)):
            raise TypeError("Target value must be a real number.")
        
        if not isinstance(i, int):
            raise TypeError("Index must be an integer.")

        if i < 0:
            raise IndexError("The index must be non-negative.")
        
        if i <= self.deg():
            self.coeff[i] = target # type: ignore

        if i > self.deg():
            self.coeff += [0] * (i - self.deg() - 1) + [target]
        
        self.coeff = simp(self.coeff)
        
    def __eq__(self, other):
        """
        Judge if two polynomials are equivalent
        
        :param self: Polynomial
        :param other: Polynomial
        :return: whether two polynomials equal
        :rtype: bool

        :raises TypeError: other is neither a polynomial, int nor float
        """

        if not isinstance(other, (Polynomial, int, float)):
            raise TypeError("Not comparable to a polynomial.")

        if isinstance(other, (int, float)):
            other = Polynomial([other])

        if self.deg() != other.deg():
            return False
        for i in range(0, self.deg() + 1, 1):
            if self.coeff[i] != other.coeff[i]:
                return False
        return True

    def __ne__(self, other):
        return not self == other

    def __add__(self, other):
        """
        The sum of self and other
        
        :param self: Polynomial
        :param other: Polynomial
        :return: the sum of self and other
        :rtype: Polynomial

        :raises TypeError: other is neither a polynomial, int nor float
        """

        if not isinstance(other, (Polynomial, int, float)):
            raise TypeError("Can't operate + between given operands.")

        if isinstance(other, (int, float)):
            other = Polynomial([other])

        deg = max(self.deg(), other.deg())
        self_coeff = self.coeff[:] + [0]*(deg - self.deg())
        other_coeff = other.coeff[:] + [0]*(deg - other.deg())

        coeff = [self_coeff[i] + other_coeff[i] for i in range(0, deg + 1, 1)]
        result = Polynomial(coeff)
        return result

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        """
        The difference between self and other
        
        :param self: Polynomial
        :param other: Polynomial
        :return: the difference between self and other
        :rtype: Polynomial

        :raises TypeError: other is neither a polynomial, int nor float
        """

        if not isinstance(other, (Polynomial, int, float)):
            raise TypeError("Can't operate - between given operands.")

        if isinstance(other, (int, float)):
            other = Polynomial([other])

        minus_other = other * (-1)
        result = self + minus_other
        return result

    def __rsub__(self, other):
        return other - self

    def __mul__(self, other):
        """
        The product of self and other
        
        :param self: Polynomial
        :param other: Polynomial
        :return: the product of self and other
        :rtype: Polynomial

        :raises TypeError: other is neither a polynomial, int nor float
        """

        if not isinstance(other, (Polynomial, int, float)):
            raise TypeError("Can't operate * between given operands.")

        if isinstance(other, (int, float)):
            coeff = [self.coeff[i] *
                     other for i in range(0, self.deg() + 1, 1)]
            result = Polynomial(coeff)
            return result

        prod = [0] * (self.deg() + other.deg() + 1)
        for i in range(0, other.deg() + 1, 1):
            for j in range(0, self.deg() + 1, 1):
                prod[i + j] += self.coeff[j] * other.coeff[i] # type: ignore
        result = Polynomial(prod)
        return result

    def __rmul__(self, other):
        try:
            return self * other
        except TypeError:
            return NotImplemented

    def __pow__(self, power):
        """
        Docstring for __pow__
        
        :param self: Polynomial
        :param power: non-negative int
        """

        if not isinstance(power, int):
            raise TypeError("The exponent must be an integer.")
        
        if power < 0:
            raise ValueError("The exponent must be non-negative.")
        
        if power == 0:
            return Polynomial([1])
        
        res = self
        for _ in range(1, power, 1):
            res *= self
        return res

    def div_with_rem(self, other):
        """
        Division with remainder
        
        :param self: Polynomial
        :param other: Polynomial
        :return: a list contains the quotient and the remainder
        :rtype: list[Polynomial], len = 2

        :raises ZeroDivisionError: divided by zero polynomial
        :raises TypeError: other is neither a polynomial, int nor float
        """

        if not isinstance(other, (Polynomial, int, float)):
            raise TypeError("Can't operate / between given operands.")

        if isinstance(other, (int, float)):
            if other == 0:
                raise ZeroDivisionError("Can't be divided by zero!")
            else:
                return [self * (1/other), Polynomial([0])]

        if other.coeff == [0]:
            raise ZeroDivisionError("Can't be divided by a zero Polynomial!")

        self_copy = Polynomial(self.coeff[:])
        other_copy = Polynomial(other.coeff[:])
        result = [0] * (self.deg() - other.deg() + 1)

        while self_copy.deg() >= other_copy.deg():
            diff = self_copy.deg() - other_copy.deg()
            temp = [0]*diff + [self_copy.coeff[-1]/other_copy.coeff[-1]]
            self_copy -= other_copy * Polynomial(temp)
            result[diff] = temp[-1]  # type: ignore

        return [Polynomial(result), self_copy]

    def __truediv__(self, other):
        return self.div_with_rem(other)[0]

    def __mod__(self, other):
        return self.div_with_rem(other)[1]

    def __str__(self):
        """
        Display polynomial in a mathematical way
        
        :param self: Polynomial
        """

        display = ""
        coeff = self.coeff

        for i in range(self.deg(), -1, -1):
            if i == 0:
                if coeff[i] > 0:
                    display += "+ " + str(coeff[i])
                elif coeff[i] == 0:
                    if self.deg() == 0:
                        return "0"
                elif self.deg() == 0:
                    display += str(coeff[i])
                else:
                    display += " " + str(coeff[i])

            elif i == 1:
                if coeff[i] == 1:
                    display += "+ x "
                elif coeff[i] == -1:
                    display += "-x"
                elif coeff[i] > 0:
                    display += f"+ {str(coeff[i])}x "
                elif coeff[i] == 0:
                    pass
                elif self.deg() == 1:
                    display += str(coeff[i])
                else:
                    display += " " + str(coeff[i])

            elif i == self.deg():
                if coeff[i] == 1:
                    display += f"x^{i} "
                elif coeff[i] == -1:
                    display += f"-x^{i} "
                elif coeff[i] > 0:
                    display += f"{str(coeff[i])}x^{i} "
                elif coeff[i] == 0:
                    pass
                else:
                    display += f"{str(coeff[i])}x^{i} "

            else:
                if coeff[i] == 1:
                    display += f"+ x^{i} "
                elif coeff[i] == -1:
                    display += f"- x^{i} "
                elif coeff[i] > 0:
                    display += f"+ {str(coeff[i])}x^{i} "
                elif coeff[i] == 0:
                    pass
                else:
                    display += f" {str(coeff[i])}x^{i} "

        if display[0] == '+':
            display = display[2:]
        return display

    def __repr__(self):
        return f"Polynomial({self.coeff})"

    def d(self):
        """
        Derivative of a polynomial
        
        :param self: Polynomial
        :return: derivative of the polynomial
        :rtype: Polynomial
        """

        if isinstance(self, (int, float)):
            return Polynomial([0])

        coeff = [0] * self.deg()
        if self.deg() == 0:
            return Polynomial([0])
        for i in range(0, self.deg(), 1):
            coeff[i] = (i + 1) * self.coeff[i + 1] # type: ignore
        return Polynomial(coeff)

    def derivative(self, order=1):
        """
        Multiple-order derivative of a polynomial
        
        :param self: Polynomial
        :param order: int, default=1
        :return: derivative of the polynomial
        :rtype: Polynomial

        :raises TypeError: self is neither a polynomial, int nor float
        :raises TypeError: order is not an int
        :raises ValueError: order <= 0
        """

        if not isinstance(self, (Polynomial, int, float)):
            raise TypeError("Can't operate derivative on the given operand.")

        if not isinstance(order, int):
            raise TypeError("Order must be an integer.")

        if order <= 0:
            raise ValueError("Order should be positive.")

        if isinstance(self, (int, float)):
            return Polynomial([0])

        res = Polynomial(self.coeff[:])
        for _ in range(0, order, 1):
            res = res.d()
        return res

    def evaluate(self, x):
        """
        Compute the value of polynomial at a given point

        :param x: int, float
        :return: 
        :rtype: int, float

        :raises TypeError: if x is neither an int nor a float

        ..note::
            Applying Horner's method to enhance efficiency.

        ..math::
            P(x) = a_0 + a_1 x + a_2 x ^ 2 + ... + a_n x ^ n
        """

        result = 0
        for i in range(self.deg(), -1, -1):
            result = result * x + self.coeff[i]
        return result


def gcd(poly1, poly2):
    """
    Greatest common divisor of two polynomials
    
    :param poly1: Polynomial
    :param poly2: Polynomial
    :return: GCD
    :rtype: Polynomial

    :raises TypeError: if one of the variables is not a polynomial
    """

    if not isinstance(poly1, (Polynomial, int, float)) or not isinstance(poly2, (Polynomial, int, float)):
        raise TypeError("Operands must be polynomials or numbers.")

    if isinstance(poly1, (int, float)):
        poly1 = Polynomial([poly1])

    if isinstance(poly2, (int, float)):
        poly2 = Polynomial([poly2])

    if poly1 == Polynomial([0]) and poly2 == Polynomial([0]):
        return Polynomial([0])

    if poly2 == Polynomial([0]):
        return poly1 / poly1.coeff[-1]

    if poly1 == Polynomial([0]):
        return poly2 / poly2.coeff[-1]

    rem = poly1 % poly2

    while rem != Polynomial([0]):
        poly1 = poly2
        poly2 = rem
        rem = poly1 % poly2

    return poly2 / poly2.coeff[-1]


def lcm(poly1, poly2):
    """
    Least common multiple of two polynomials
    
    :param poly1: Polynomial
    :param poly2: Polynomial
    :return: LCM
    :rtype: Polynomial

    :raises TypeError: if one of the variables is not a polynomial
    """

    if not isinstance(poly1, (Polynomial, int, float)) or not isinstance(poly2, (Polynomial, int, float)):
        raise TypeError("Operands must be polynomials or numbers.")

    if isinstance(poly1, (int, float)):
        poly1 = Polynomial([poly1])

    if isinstance(poly2, (int, float)):
        poly2 = Polynomial([poly2])

    if poly1 == Polynomial([0]) or poly2 == Polynomial([0]):
        return Polynomial([0])

    res = poly1 * poly2 / gcd(poly1, poly2)
    return res / res.coeff[-1]


# Test
if __name__ == '__main__':
    pass
    a = Polynomial([1, 4, 6, 4, 1, 0])
    # b = Polynomial([1, 2])
    # print(a / b)
    # print(a % b)
    # c = Polynomial([1])
    print(a)
    # print((a/2).coeff)
    # print((a % b).coeff)
    # print(a.derivative(order=6))
    # print(b)
    # print(c)
    # print(a.evaluate(0))
    # print(a.derivative().evaluate(0))
    # print(a.derivative(order=2).evaluate(0))
    # print(a[2])
    a[2] = 3
    print(a)
    a[7] = 1
    print(a)
    a[8] = 0
    print(a)
