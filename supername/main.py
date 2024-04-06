#!/usr/bin/env python

import click, asyncio
from functools import wraps

# Do absolute imports if entry point from package - see [tool.poetry.scripts]

if __name__== 'supername.main':
    import supername.simple_package.math_operations as math_operations
    from supername.cashu.wallet.wallet import Wallet as Wallet
    from supername.cashu.wallet.cli.cli_helpers import get_mint_wallet, print_mint_balances, verify_mint
    from supername.cashu.core.migrations import migrate_databases
    from supername.cashu.wallet import migrations
else:
    import simple_package.math_operations as math_operations
    from cashu.wallet.wallet import Wallet as Wallet
    from cashu.wallet.cli.cli_helpers import get_mint_wallet, print_mint_balances, verify_mint
    from cashu.core.migrations import migrate_databases
    from cashu.wallet import migrations



@click.group()
def cli():
    pass

@click.command()
@click.option('--unit', default='sat', help='unit of account')
@click.argument('amount', default=21)
@click.argument('recipient', default='hello@supername')
def send(amount, recipient, unit):
    click.echo(f'Send  {amount} {unit} to {recipient}')

@click.command()
def receive():
    click.echo('Receive')

cli.add_command(send)
cli.add_command(receive)
    




if __name__ == '__main__':
    cli()
