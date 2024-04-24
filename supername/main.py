#!/usr/bin/env python
import os
import yaml
import requests
import click, asyncio
from functools import wraps
from binascii import hexlify

from fido2.hid import CtapHidDevice
from fido2.client import Fido2Client, UserInteraction
from fido2.server import Fido2Server

from getpass import getpass
import sys
import ctypes

from enum import Enum
import json

import base64
import cbor

from webauthn import (
    generate_registration_options,
    verify_registration_response,
    options_to_json,
    base64url_to_bytes,
    
)
from webauthn.helpers.cose import COSEAlgorithmIdentifier
from webauthn.helpers.structs import (
    AttestationConveyancePreference,
    AuthenticatorAttachment,
    AuthenticatorSelectionCriteria,
    PublicKeyCredentialDescriptor,
    ResidentKeyRequirement,
    PublicKeyCredentialCreationOptions,
    AttestationObject
)

# Handle user interaction
class CliInteraction(UserInteraction):
    def prompt_up(self):
        print("\nTouch your authenticator device now...\n")

    def request_pin(self, permissions, rd_id):
        return getpass("Enter PIN: ")

    def request_uv(self, permissions, rd_id):
        print("User Verification required.")
        return True

class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value  # or obj.name to serialize as the name
        return json.JSONEncoder.default(self, obj)

uv = "discouraged"

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

@click.command
@click.argument('message')
def post(message):
    click.echo(f"nostr post{message}")
    send_url = scheme + wallet_server + "/supername/post"
    headers = {"X-superkey": wallet_key }

    send_data = {
                    "msg": message
                    
                }

    print("post:", send_url, send_data, headers)
    print(send_url,)
    response = requests.post(send_url, json=send_data, headers=headers)
    print("response:", response.text) 

@click.command
@click.argument('recipient')
@click.argument('message')
def dm(recipient, message):
    click.echo(f"nostr dm {recipient} {message}")
    send_url = scheme + wallet_server + "/supername/dm"
    headers = {"X-superkey": wallet_key }

    send_data = {
                    "recipient": recipient,
                    "msg": message
                    
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
    click.echo(f"Local Amount: {profile_obj['currency_symbol']}{profile_obj['local_amount']} {profile_obj['local_currency']}" )

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
@click.option('--server', default=None)
@click.pass_context
def config(ctx, debug, server):
    click.echo(f'Your wallet key: {wallet_key}')
    click.echo(f'Your wallet server: {wallet_server}')
    if server:
        click.echo(f"server: {server}")
        config_obj['profile']['server']=server
        with open(file_path, 'w') as file:        
            yaml.dump(config_obj, file)

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


@click.command()
def fido():
    click.echo(f'fido')
    uv = "discouraged"

    
    # Locate a device
    dev = next(CtapHidDevice.list_devices(), None)
    if dev is not None:
        print("Use USB HID channel.")
    else:
        try:
            from fido2.pcsc import CtapPcscDevice

            dev = next(CtapPcscDevice.list_devices(), None)
            print("Use NFC channel.")
        except Exception as e:
            print("NFC channel search error:", e)

    if not dev:
        print("No FIDO device found")
        sys.exit(1)

    
    # Set up a FIDO 2 client using the origin wallet_server
    client = Fido2Client(dev, f"https://{wallet_server}", user_interaction=CliInteraction())
    

    # Prefer UV if supported and configured
    if client.info.options.get("uv") or client.info.options.get("pinUvAuthToken"):
        uv = "preferred"
        print("Authenticator supports User Verification")

    server = Fido2Server({"id": wallet_server, "name": "Example RP"}, attestation="direct")

    user = {"id": wallet_key.encode(), "name": wallet_key}
    # Prepare parameters for makeCredential
    create_options, state = server.register_begin(
        user, user_verification=uv, authenticator_attachment="cross-platform"
    )
    print("create options:", dict(create_options["publicKey"]))
    # Create a credential
    result = client.make_credential(create_options["publicKey"])
    print("completed!", type(result))
   
    # Complete registration
    auth_data = server.register_complete(
        state, result.client_data, result.attestation_object
    )
    credential_data = auth_data.credential_data
    credentials = [credential_data]
    
    click.echo("New credential created!")
    # click.echo(f"CLIENT DATA: {result.client_data}")
    # click.echo(f"ATTESTATION OBJECT: {result.attestation_object}")    
    # click.echo(f"CREDENTIAL DATA: {auth_data.credential_data}")
    # click.echo(f"Credential: {auth_data.credential_data.aaguid}")
    # click.echo(f"Credential ID: {hexlify(auth_data.credential_data.credential_id).decode()}")
    # click.echo(f"Credential Public Key: {auth_data.credential_data.public_key}")
  
    # x = input("Get Authentication")
    click.echo(f"{credentials}")
    # Prepare parameters for getAssertion
    request_options, state = server.authenticate_begin(credentials, user_verification=uv)

    # Authenticate the credential
    result = client.get_assertion(request_options["publicKey"])

    # Only one cred in allowCredentials, only one response.
    result = result.get_response(0)

    # Complete authenticator
    server.authenticate_complete(
        state,
        credentials,
        result.credential_id,
        result.client_data,
        result.authenticator_data,
        result.signature,
    )

    click.echo("Credential authenticated!")

    # print("CLIENT DATA:", result.client_data)
    # print()
    # print("AUTH DATA:", result.authenticator_data)

@click.command()
def register():
    click.echo(f'register')
    uv = "discouraged"

    dev = next(CtapHidDevice.list_devices(), None)

    send_url = scheme + wallet_server + "/supername/register/begin"
    headers = {"X-superkey": wallet_key }
    # print(send_url,)
    response = requests.post(send_url, headers=headers)
    register = response.json()
    click.echo(f"register: {register}")

    json_data = json.dumps(register, cls=EnumEncoder)
    click.echo(f"json_data: {json_data}")
    # click.echo(f"rp: {register['rp']}")
    # click.echo(f"user: {register['user']}")
    # click.echo(f"challenge: {register['challenge']}")
    # click.echo(f"pubKeyCredParams: {register['pubKeyCredParams']}")
    # click.echo(f"timeout: {register['timeout']}")
    # click.echo(f"excludeCredentials: {register['excludeCredentials']}")
    # click.echo(f"attestation: {register['attestation']}")
    hello_world = b'Hello, Worldss!'
    click.echo(hello_world)
    click.echo(base64.b64encode(hello_world))

    
    # server = Fido2Server({"id": wallet_server, "name": register['rp']['name']}, attestation="direct")



    try:
        client = Fido2Client(dev, f"https://{register['rp']['id']}", user_interaction=CliInteraction())
    except:
        click.echo("No device found!")
        sys.exit(1)
    
    user = {"id": wallet_key.encode(), "name": wallet_key}
    # Prepare parameters for makeCredential
    # create_options, state = server.register_begin(
    #     user, user_verification=uv, authenticator_attachment="cross-platform"
    # )
    # click.echo(f"create options publickey:  {create_options['publicKey']}")
    
    click.echo(f"create options register:  {register}")

    # Prepare parameters for makeCredential
    rp = {"id": register['rp']['id'], "name": register['rp']['name']}
    # rp = register['rp']
    user = {"id": register['user']['id'].encode(), "name": register['user']['name']}
    # user = register['user']
    challenge = register['challenge']
    challenge_padded = challenge +len(challenge)%4*"="
    challenge_decoded = base64.b64decode(challenge_padded)
    pub_key_cred_params = register['pubKeyCredParams']

    credential_options = PublicKeyCredentialCreationOptions( rp=rp, 
                                                             challenge=challenge_decoded, user=user, pub_key_cred_params=pub_key_cred_params
                                                            )
    
    result = client.make_credential(options=
    {
        "rp": rp,
        "user": user,
        "challenge": challenge_decoded,
        "pubKeyCredParams": pub_key_cred_params
        
    },
    )

    click.echo(f"rp {rp}") 
    click.echo(f"user {user}") 
    click.echo(f"pubKeyCredParams {pub_key_cred_params}") 
    click.echo(f"challenge decoded {challenge_decoded}") 

   # click.echo(f"make credential: {result} \n client data: {result.client_data}")
   # client_data_json = json.dump(result.client_data, cls=EnumEncoder)
    
    make_credential = {
        "id": "ZoIKP1JQvKdrYj1bTUPJ2eTUsbLeFkv-X5xJQNr4k6s",
        "rawId": "ZoIKP1JQvKdrYj1bTUPJ2eTUsbLeFkv-X5xJQNr4k6s",
        "response": {
            "attestationObject": "o2NmbXRkbm9uZWdhdHRTdG10oGhhdXRoRGF0YVkBZ0mWDeWIDoxodDQXD2R2YFuP5K65ooYyx5lc87qDHZdjRQAAAAAAAAAAAAAAAAAAAAAAAAAAACBmggo_UlC8p2tiPVtNQ8nZ5NSxst4WS_5fnElA2viTq6QBAwM5AQAgWQEA31dtHqc70D_h7XHQ6V_nBs3Tscu91kBL7FOw56_VFiaKYRH6Z4KLr4J0S12hFJ_3fBxpKfxyMfK66ZMeAVbOl_wemY4S5Xs4yHSWy21Xm_dgWhLJjZ9R1tjfV49kDPHB_ssdvP7wo3_NmoUPYMgK-edgZ_ehttp_I6hUUCnVaTvn_m76b2j9yEPReSwl-wlGsabYG6INUhTuhSOqG-UpVVQdNJVV7GmIPHCA2cQpJBDZBohT4MBGme_feUgm4sgqVCWzKk6CzIKIz5AIVnspLbu05SulAVnSTB3NxTwCLNJR_9v9oSkvphiNbmQBVQH1tV_psyi9HM1Jtj9VJVKMeyFDAQAB",
            "clientDataJSON": "eyJ0eXBlIjoid2ViYXV0aG4uY3JlYXRlIiwiY2hhbGxlbmdlIjoiQ2VUV29nbWcwY2NodWlZdUZydjhEWFhkTVpTSVFSVlpKT2dhX3hheVZWRWNCajBDdzN5NzN5aEQ0RmtHU2UtUnJQNmhQSkpBSW0zTFZpZW40aFhFTGciLCJvcmlnaW4iOiJodHRwOi8vbG9jYWxob3N0OjUwMDAiLCJjcm9zc09yaWdpbiI6ZmFsc2V9",
            "transports": ["internal"  ]
                },
        "type": "public-key",
        "authenticatorAttachment": "platform",
        "clientExtensionResults": {}
        }
    
    make_real_credential = {
        "id": "ZoIKP1JQvKdrYj1bTUPJ2eTUsbLeFkv-X5xJQNr4k6s",
        "rawId": "ZoIKP1JQvKdrYj1bTUPJ2eTUsbLeFkv-X5xJQNr4k6s",
        "response": {
            "attestationObject": "o2NmbXRkbm9uZWdhdHRTdG10oGhhdXRoRGF0YVkBZ0mWDeWIDoxodDQXD2R2YFuP5K65ooYyx5lc87qDHZdjRQAAAAAAAAAAAAAAAAAAAAAAAAAAACBmggo_UlC8p2tiPVtNQ8nZ5NSxst4WS_5fnElA2viTq6QBAwM5AQAgWQEA31dtHqc70D_h7XHQ6V_nBs3Tscu91kBL7FOw56_VFiaKYRH6Z4KLr4J0S12hFJ_3fBxpKfxyMfK66ZMeAVbOl_wemY4S5Xs4yHSWy21Xm_dgWhLJjZ9R1tjfV49kDPHB_ssdvP7wo3_NmoUPYMgK-edgZ_ehttp_I6hUUCnVaTvn_m76b2j9yEPReSwl-wlGsabYG6INUhTuhSOqG-UpVVQdNJVV7GmIPHCA2cQpJBDZBohT4MBGme_feUgm4sgqVCWzKk6CzIKIz5AIVnspLbu05SulAVnSTB3NxTwCLNJR_9v9oSkvphiNbmQBVQH1tV_psyi9HM1Jtj9VJVKMeyFDAQAB",
            "clientDataJSON": "eyJ0eXBlIjoid2ViYXV0aG4uY3JlYXRlIiwiY2hhbGxlbmdlIjoiQ2VUV29nbWcwY2NodWlZdUZydjhEWFhkTVpTSVFSVlpKT2dhX3hheVZWRWNCajBDdzN5NzN5aEQ0RmtHU2UtUnJQNmhQSkpBSW0zTFZpZW40aFhFTGciLCJvcmlnaW4iOiJodHRwOi8vbG9jYWxob3N0OjUwMDAiLCJjcm9zc09yaWdpbiI6ZmFsc2V9",
            "transports": ["internal"  ]
                },
        "type": "public-key",
        "authenticatorAttachment": "platform",
        "clientExtensionResults": {}
        }
    # click.echo(make_credential)
    # click.echo(make_real_credential)
    send_url = scheme + wallet_server + "/supername/register/end"
    # click.echo(send_url)
    headers = {"X-superkey": wallet_key }
    json_data = make_credential
    # print(send_url,)
    response = requests.post(send_url, json=make_real_credential,headers=headers)
    register_end = response.json()
    # click.echo(f"register end: {register_end}")



    return

    try:
        # result = client.make_credential(create_options["publicKey"])
        print("before make: ", register)
        register['timeout'] = 0
        register['attestation'] = 'direct'
        register['user']['id'] = register['user']['id'].encode()
        challenge = register['challenge']
        challenge_padded = challenge +len(challenge)%4*"="
        challenge_decoded = base64.b64decode(challenge_padded)
        print("challenge",challenge)
        print("challenge decoded", challenge_decoded)
        print("challenge_padded", challenge_padded)
        # register['challenge'] = base64.b64encode(hello_world)
        print(register['challenge']+ len(register['challenge'])%4*"=")
        register['challenge'] = challenge_decoded
        print("make: ", register)
        result = client.make_credential(register)
    except Exception as e:
        click.echo(f"Error! {e}")
        sys.exit(1) 

    
    # click.echo(f"result: {result_dict}")
    # click.echo(f"clientDataJSON: {result_dict['clientDataJSON']}")
    # click.echo(f"attestationObject: {result_dict['attestationObject']}")
    # click.echo(f"extensionResults: {result_dict['extensionResults']}")
    click.echo(f"result.client_data: {result.client_data}")
    click.echo(f"result.client_data: {result.client_data.type}")
    click.echo(f"result.client_data: {base64.b64encode(result.client_data.challenge).decode().replace('/','_').replace('+','-').replace('=','')}")
    click.echo(f"result.client_data: {result.client_data.origin}")

    
    # click.echo(f"state: {state}")

@click.command()
def webauthn():
    click.echo(f'webauthn')  
    rp_id="staging.nimo.cash"
    user_name = "trbouma"

    simple_registration_options = generate_registration_options(
    rp_id=rp_id,
    rp_name="Nimo Cash",
    user_name=user_name,
    )
    
    

    simple_registration_options_json = json.loads(options_to_json(simple_registration_options))
    click.echo(f"simple registration options json: {simple_registration_options_json}")
    click.echo(f"rp id: {simple_registration_options_json['rp']}")
    click.echo(f"user: {simple_registration_options_json['user']}")
    click.echo(f"challenge: {simple_registration_options_json['challenge']}")
    click.echo(f"pubKeyCredParams: {simple_registration_options_json['pubKeyCredParams']}")

    dev = next(CtapHidDevice.list_devices(), None)
    client = Fido2Client(dev, f"https://{rp_id}", user_interaction=CliInteraction())

   

    user_parm = simple_registration_options_json['user']
    user_parm['id'] = base64url_to_bytes(user_parm['id'])
    challenge_parm = base64url_to_bytes(simple_registration_options_json['challenge'])

    result = client.make_credential(options=
    {
        "rp": simple_registration_options_json['rp'],
        "user": user_parm,
        "challenge": challenge_parm,
        "pubKeyCredParams": simple_registration_options_json['pubKeyCredParams']
        
    },
    )
    
    

    click.echo(f"CLIENT DATA: {result.client_data}")
    click.echo(f"ATTESTATION OBJECT:{result.attestation_object}")
    # click.echo(f"{result.extension_results}")

    id = base64.b64encode(result.attestation_object.auth_data.credential_data.credential_id).decode()
    click.echo(f"base64 id {id}")
    registration_verification = verify_registration_response(
    # Demonstrating the ability to handle a plain dict version of the WebAuthn response
    credential={
        "id": "ZoIKP1JQvKdrYj1bTUPJ2eTUsbLeFkv-X5xJQNr4k6s",
        "rawId": "ZoIKP1JQvKdrYj1bTUPJ2eTUsbLeFkv-X5xJQNr4k6s",
        "response": {
            "attestationObject": "o2NmbXRkbm9uZWdhdHRTdG10oGhhdXRoRGF0YVkBZ0mWDeWIDoxodDQXD2R2YFuP5K65ooYyx5lc87qDHZdjRQAAAAAAAAAAAAAAAAAAAAAAAAAAACBmggo_UlC8p2tiPVtNQ8nZ5NSxst4WS_5fnElA2viTq6QBAwM5AQAgWQEA31dtHqc70D_h7XHQ6V_nBs3Tscu91kBL7FOw56_VFiaKYRH6Z4KLr4J0S12hFJ_3fBxpKfxyMfK66ZMeAVbOl_wemY4S5Xs4yHSWy21Xm_dgWhLJjZ9R1tjfV49kDPHB_ssdvP7wo3_NmoUPYMgK-edgZ_ehttp_I6hUUCnVaTvn_m76b2j9yEPReSwl-wlGsabYG6INUhTuhSOqG-UpVVQdNJVV7GmIPHCA2cQpJBDZBohT4MBGme_feUgm4sgqVCWzKk6CzIKIz5AIVnspLbu05SulAVnSTB3NxTwCLNJR_9v9oSkvphiNbmQBVQH1tV_psyi9HM1Jtj9VJVKMeyFDAQAB",
            "clientDataJSON": "eyJ0eXBlIjoid2ViYXV0aG4uY3JlYXRlIiwiY2hhbGxlbmdlIjoiQ2VUV29nbWcwY2NodWlZdUZydjhEWFhkTVpTSVFSVlpKT2dhX3hheVZWRWNCajBDdzN5NzN5aEQ0RmtHU2UtUnJQNmhQSkpBSW0zTFZpZW40aFhFTGciLCJvcmlnaW4iOiJodHRwOi8vbG9jYWxob3N0OjUwMDAiLCJjcm9zc09yaWdpbiI6ZmFsc2V9",
            "transports": ["internal"],
        },
        "type": "public-key",
        "clientExtensionResults": {},
        "authenticatorAttachment": "platform",
    },
    expected_challenge=base64url_to_bytes(
        "CeTWogmg0cchuiYuFrv8DXXdMZSIQRVZJOga_xayVVEcBj0Cw3y73yhD4FkGSe-RrP6hPJJAIm3LVien4hXELg"
    ),
    expected_origin="http://localhost:5000",
    expected_rp_id="localhost",
    require_user_verification=True,
)
    

###############################################################################
        
cli.add_command(send)
cli.add_command(receive)
cli.add_command(balance)
cli.add_command(config)
cli.add_command(login)
cli.add_command(profile,name="whoami")
cli.add_command(profile)
cli.add_command(get)
cli.add_command(set)
cli.add_command(did)
cli.add_command(ecash)
cli.add_command(sign)
cli.add_command(fido)
cli.add_command(register)
cli.add_command(post)
cli.add_command(dm)
cli.add_command(webauthn)
    

if __name__ == '__main__':
    cli()
