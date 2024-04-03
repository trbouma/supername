#!/usr/bin/env python

import click

import supername.simple_package.math_operations as math_operations

    

@click.command()
@click.option('--name', prompt='Your name',
              help='The person to greet.', default='Guest')
@click.option('--title', prompt='Your title',
              help='The title to greet.', default='Honourable')
@click.option('--superpower', prompt='Your superpower',
              help='Your superpower.', default='invisibility')
def main(name, title, superpower):
    click.echo(f'Hello, {title} {name} with your superpower as {superpower}!')
    print(math_operations.add(5,3))
    print(__name__)

if __name__ == '__main__':
    main()
