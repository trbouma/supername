#!/usr/bin/env python

import click

@click.command()
@click.option('--name', prompt='Your name',
              help='The person to greet.')
@click.option('--title', prompt='Your title',
              help='The title to greet.')
def main(name, title):
    click.echo(f'Hello, {title} {name}!')

if __name__ == '__main__':
    main()
