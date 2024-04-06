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

def coro(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper  

def wallet():
    mint = "https://mint.nimo.cash"
    wallet_db = "postgres://postgres:password@abctel.co:6432/nzq1mmzlcm9jaw91cw"

    wallet = Wallet(mint, wallet_db)

    asyncio.run(migrate_databases(wallet.db, migrations))
    asyncio.run(wallet._init_private_key())
    asyncio.run(wallet.load_proofs())
    asyncio.run(wallet.load_mint())

    amount = int(input("what is the amount to receive? "))
    invoice = asyncio.run(wallet.request_mint(amount))
    print("invoice:", invoice.bolt11 )
    print("----")
    print("id: ", invoice.id)
    paid = input("have you paid yet?")
    if paid =='y':
        asyncio.run(wallet.mint(amount, id=invoice.id))
        print("balance:", wallet.balance_per_keyset())
        print(wallet.available_balance)  

@click.command()
@click.option('--name', prompt='Your name',
              help='The person to greet.', default='Guest')
@click.option('--title', prompt='Your title',
              help='The title to greet.', default='Honourable')
@click.option('--superpower', prompt='Your superpower',
              help='Your superpower.', default='invisibility')
@click.argument('command', default='view')

def main(command, name, title, superpower):
    click.echo(f'Hello, {title} {name} commanding {command} with your superpower as {superpower}!')
    print(math_operations.add(5,3))
    print(__name__)

    




if __name__ == '__main__':
    main()
