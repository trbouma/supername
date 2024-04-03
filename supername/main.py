#!/usr/bin/env python

import argparse

def main():
    # Create ArgumentParser object
    parser = argparse.ArgumentParser(description='A simple program with argparse')

    # Add arguments
    parser.add_argument('--name', '-n', type=str, help='Your name')
    parser.add_argument('--age', '-a', type=int, help='Your age')

    # Parse the arguments
    args = parser.parse_args()

    # Access the values of the arguments
    name = args.name
    age = args.age

    # Print out the values
    print(f'Your name is: {name}')
    print(f'Your age is: {age}')

if __name__ == "__main__":
    main()
