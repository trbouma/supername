#!/usr/bin/env python

import typer

from lib.simple_package import math_operations, greeting


def main():
    print("Hello World")
    print(math_operations.add(5, 3)) 

if __name__ == "__main__":
    typer.run(main)
