#!/usr/bin/env python
import os
import yaml
import requests
import click, asyncio
from functools import wraps

# Do absolute imports if entry point from package - see [tool.poetry.scripts]



home_directory = os.path.expanduser('~')
super_directory = '.supername'
config_file = 'config.yml'
config_directory = os.path.join(home_directory, super_directory)
file_path = os.path.join(home_directory, super_directory, config_file)
print('file path:',file_path)
os.makedirs(config_directory, exist_ok=True)

if os.path.exists(file_path):
    with open(file_path, 'r') as file:
        config_obj = yaml.safe_load(file)
else:
    config_obj = {'profile': {'key': '123mocha', 'server': 'nimo.cash'}}
    with open(file_path, 'w') as file:        
        yaml.dump(config_obj, file)



# print(config_obj)

wallet_server =config_obj['profile']['server']
wallet_key =config_obj['profile']['key']

if wallet_server == 'localhost:8000':
    scheme = "http://"
else:
    scheme = "https://"

@click.group()
def cli():
    pass



@click.command()
@click.argument('recipient', default='hello@supername')
@click.argument('amount', default=21)
@click.option('--message', default='Thank you!', help='message to send')
def send(amount, recipient, message):
    click.echo(f'Send  {amount}  to {recipient} with message {message}')

   

    send_url = scheme + wallet_server + "/supername/send"
    headers = {"X-superkey": wallet_key }

    send_data = {
                    "recipient": recipient,
                    "amount": amount,
                    "message": message,
                    "currency": "SAT"
                }

    
    print("post:", send_url, send_data, headers)
    
    
    print(send_url,)
    response = requests.post(send_url, json=send_data, headers=headers)
    print("response:", response.text) 


@click.command()
@click.argument('amount', default=21)
def ecash(amount):
    click.echo(f'ecash  {amount} ')

   

    send_url = scheme + wallet_server + "/supername/ecash"
    headers = {"X-superkey": wallet_key }

    send_data = {                    
                    "amount": amount,                    
                    "currency": "SAT"
                }
    

    
    # print("post:", send_url, send_data, headers)
    
    
    # print(send_url,)
    response = requests.post(send_url, json=send_data, headers=headers)
    # print("response:", response.text) 
    click.echo(response.json()["cashu_tokens"][0])

@click.command()
def profile():
    click.echo(f'Local: server: {wallet_server} key: {wallet_key}')

    click.echo ('Getting details...')
    send_url = scheme + wallet_server + "/supername/profile"
    headers = {"X-superkey": wallet_key }

    response = requests.get(send_url, headers=headers)
    
    profile_obj = response.json()

    click.echo(f"Super Name: {profile_obj['wallet_name']}@{wallet_server}" )
    click.echo(f"Nostr Npub: {profile_obj['nostr_npub']}" )
    click.echo(f"Nostr Nsec: {profile_obj['nostr_nsec']}" )
    click.echo(f"Balance: {profile_obj['balance']}" )

@click.command()
def did():
    click.echo(f'Local: server: {wallet_server} key: {wallet_key}')

    click.echo ('Getting details...')
    send_url = scheme + wallet_server + "/supername/balance"
    headers = {"X-superkey": wallet_key }

    response = requests.get(send_url, headers=headers)
    
    balance_amt = response.json()['balance']

    click.echo(f'Balance: {balance_amt}' )

@click.command()
@click.option('--key', default=None, help='set super key')
@click.option('--server', default=None, help='set server')
def set(key, server):
    click.echo(f'Set Key {key}, {server}')
    if key != None:
        config_obj['profile']['key']=key
    if server != None:
        config_obj['profile']['server']=server

    with open(file_path, 'w') as file:        
        yaml.dump(config_obj, file)

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
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def info(ctx, debug):
    click.echo(f'Your wallet key: {wallet_key}')
    click.echo(f'Your wallet server: {wallet_server}')

@click.command()
def balance():
    click.echo('Getting your balance...')
    send_url = scheme + wallet_server + "/supername/balance"
    headers = {"X-superkey": wallet_key }
  
    # print("get:", send_url, headers)
   
    print(send_url,)
    response = requests.get(send_url, headers=headers)
    print("response:", response.json()) 
    balance_amt = response.json()['balance']

    click.echo(f'Balance: {balance_amt}' )


@click.command()
def me():
    click.echo('Getting your balance...')
    send_url = scheme + wallet_server + "/supername/balance"
    headers = {"X-superkey": wallet_key }
  
    # print("get:", send_url, headers)
   
    print(send_url,)
    response = requests.get(send_url, headers=headers)
    print("response:", response.json()) 
    balance_amt = response.json()['balance']

    click.echo(f'Balance: {balance_amt}' )

@click.command()
@click.argument('key', default='None')
def login(key):
    click.echo(f'Login with your key {key}')

@click.command()
@click.argument('message', default='Thank you!')
def sign(message):
    click.echo(f'message  {message} ')

   

    send_url = scheme + wallet_server + "/supername/sign"
    headers = {"X-superkey": wallet_key }

    send_data = {                    
                    "msg": message,                    
                    "digest": None,
                    "alg": "schnorr"
                }
    

    
    
    
    
    # print(send_url,)
    response = requests.post(send_url, json=send_data, headers=headers)
    # print("response:", response.text) 
    click.echo(response.json())

cli.add_command(send)
cli.add_command(receive)
cli.add_command(balance)
cli.add_command(info)
cli.add_command(login)
cli.add_command(profile,name="whoami")
cli.add_command(profile)
cli.add_command(get)
cli.add_command(set)
cli.add_command(did)
cli.add_command(ecash)
cli.add_command(sign)
    

if __name__ == '__main__':
    cli()
