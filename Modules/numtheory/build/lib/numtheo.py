# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 18:03:28 2023

@author: 14083
"""
#prime judgment
def isprime(x):
    if x==1:
        return False
    if x==2:
        return True
    else:
        for i in range(2,int(x**0.5)+1):
            if x%i==0:
                return False
    return True

#the greatest common divisor
def gcd(x,y):
    r=x%y
    while r!=0:
        x=y
        y=r
        r=x%y
    return y

#the least common multiple
def lcm(x,y):
    l=int(x*y/gcd(x,y))
    return l

#Euler function
def phi(x):
    count=0
    for i in (1,x):
        if gcd(i,x)==1:
            count+=1
    return count

#amount of divisors
def dnum(x):
    count=0
    for i in range(1,x+1):
        if x%i==0:
            count+=1
    return count

#sum of divisors
def dsum(x):
    sum=0
    for i in range(1,x+1):
        if x%i==0:
            sum+=i
    return sum

#list of divisors
def dlist(x):
    l=[]
    if x==1:
        l=[1]
    else:
        for i in range(1,x+1):
            if x%i==0:
                l.append(i)
    return l

#list of prime factors
def plist(x):
    l=dlist(x)
    k=[]
    for i in l:
        if isprime(i)==True:
            k.append(i)
    return k

#the largest power of prime
def v(p,x):
    k=0
    while x%p==0:
        x/=p
        k+=1
    return k

#Jocobi symbol (x/y)
def jacobi(x,y):
    for i in range(0,y):
        if (i**2)%y==x:
            return True
    return False

#factorial function
def factorial(n):
    if n==0:
        return 1
    else:
        return n*factorial(n-1)
    
#combination funtion c(n,m)
def c(n,m):
    if m>n:
        return 0
    else:
        d=int(factorial(n)/(factorial(m)*factorial(n-m)))
        return d

if __name__=="__init__":
    print("Welcome")
    