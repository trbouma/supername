#!/usr/bin/env python
import os
import yaml
import requests
import click, asyncio
from functools import wraps

# Do absolute imports if entry point from package - see [tool.poetry.scripts]



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
def profile():
    click.echo('Profile')

@click.command()
@click.argument('name')
def get(name):
    click.echo(f'Get {name}')
    get_url = f"https://{wallet_server}/available/{name}"
    print(get_url
          )
    response = requests.get(get_url)
    print(response.text)
                            



@click.command()
def receive():
    click.echo('Receive')

@click.command()
def info():
    click.echo(f'Your wallet key: {wallet_key}')

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
cli.add_command(profile)
cli.add_command(get)
    

if __name__ == '__main__':
    cli()
