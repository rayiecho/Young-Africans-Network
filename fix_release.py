import json
import requests
from google.oauth2 import service_account
import google.auth.transport.requests

sa_path = '/home/ayiecho/projects/yan_website/serviceAccount.json'
with open(sa_path, 'r') as f:
    sa = json.load(f)
project_id = sa['project_id']

creds = service_account.Credentials.from_service_account_file(
    sa_path, scopes=['https://www.googleapis.com/auth/cloud-platform']
)
creds.refresh(google.auth.transport.requests.Request())
token = creds.token
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# Get latest ruleset
resp = requests.get(
    f'https://firebaserules.googleapis.com/v1/projects/{project_id}/rulesets',
    headers=headers
)
rulesets = resp.json().get('rulesets', [])
latest = rulesets[0]['name']
print(f"Latest ruleset: {latest}")

# Release with correct field name
rel = requests.patch(
    f'https://firebaserules.googleapis.com/v1/projects/{project_id}/releases/cloud.firestore',
    headers=headers,
    json={
        'release': {
            'name': f'projects/{project_id}/releases/cloud.firestore',
            'rulesetName': latest
        }
    }
)
print(f"Release: {rel.status_code}")
if rel.status_code == 200:
    print("✅ Rules deployed successfully!")
else:
    print(rel.text)
