import base64
import json
from fido2.webauthn import AuthenticatorAttestationResponse

def response_to_json(response: AuthenticatorAttestationResponse):
    # Base64 encode the binary data to make it JSON serializable
    client_data_json_base64 = base64.b64encode(response.client_data).decode('utf-8')
    attestation_object_base64 = base64.b64encode(response.attestation_object).decode('utf-8')

    # Construct the JSON object
    response_json = {
        "clientDataJSON": client_data_json_base64,
        "attestationObject": attestation_object_base64
    }
    
    # Convert dictionary to JSON string if needed
    return json.dumps(response_json)

# Example usage
# Assuming you have a `response` which is an instance of AuthenticatorAttestationResponse
# response_json = response_to_json(response)
# print(response_json)
