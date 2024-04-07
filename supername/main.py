#!/usr/bin/env python
import os
import yaml
import requests
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

home_directory = os.path.expanduser('~')
super_directory = '/.supername'
filename = '/config.yml'
os.makedirs(home_directory+super_directory, exist_ok=True)
with open(home_directory+super_directory+ filename, 'a') as file:
    pass

with open(home_directory+super_directory+ filename, 'r') as file:
    config_obj = yaml.safe_load(file)

print(config_obj['profile']['server'])

wallet_server =config_obj['profile']['server']
wallet_key =config_obj['profile']['key']

@click.group()
def cli():
    pass

@click.command()
@click.option('--unit', default='sat', help='unit of account')
@click.option('--message', default='Thank you!', help='message to send')
@click.argument('amount', default=21)
@click.argument('recipient', default='hello@supername')
def send(amount, recipient, unit, message):
    click.echo(f'Send  {amount} {unit} to {recipient} with {message}')

    send_url = "https://" + wallet_server + "/wallet/lnpay"
    send_data = {
                    "wallet_key": wallet_key,
                    "ln_address": recipient,
                    "ln_amount": amount,
                    "ln_comment": message,
                    "ln_currency": "SAT"
                }
    print(send_url, send_data)
    response = requests.post(send_url, json=send_data)
    print(response.text)

@click.command()
def receive():
    click.echo('Receive')

@click.command()
def info():
    click.echo(f'Your information: {home_directory}')

@click.command()
def balance():
    click.echo('Your balance:')

@click.command()
@click.argument('key', default='None')
def login(key):
    click.echo(f'Login with your key {key}')

cli.add_command(send)
cli.add_command(receive)
cli.add_command(balance)
cli.add_command(info)
cli.add_command(login)
    

if __name__ == '__main__':
    cli()
