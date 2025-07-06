# sfmc-client-python
## Overview

This Python client library provides a synchronous, easy-to-use interface to interact with Salesforce Marketing Cloud (SFMC) APIs, including REST and SOAP endpoints.

It supports authentication via OAuth 2 client credentials and exposes high-level managers for core SFMC objects like Data Extensions, Automations, Queries, and Subscribers.

Async support is planned for future releases.

Installation
Install via cloning the repo or copying the module files into your project, or install locally with:

```bash
pip install -e .
```

## Configuration

You can configure the client by passing parameters directly to the constructor or by setting environment variables.

| Parameter        | Env Variable          | Description                                               |
| ---------------- | --------------------- | --------------------------------------------------------- |
| client_id        | SFMC_CLIENT_ID        | OAuth Client ID                                           |
| client_secret    | SFMC_CLIENT_SECRET    | OAuth Client Secret                                       |
| account_name     | N/A                   | Logical account name used to select account ID (optional) |
| account_id       | SFMC_ACCOUNT_IDS      | Account ID (MID) overrides account_name (optional)        |
| tenant_subdomain | SFMC_TENANT_SUBDOMAIN | Tenant-specific subdomain for API endpoints               |

Note: SFMC_ACCOUNT_IDS environment variable should be a JSON string mapping account names to account IDs, e.g. See .env.example file:

```python
SFMC_ACCOUNT_IDS={"AccountName1": "123456789", "AccountName2": "987654321"}
```

## Usage

### Initializing Client

You can initialize the client in two ways:

1. Passing parameters directly to the constructor

```python
from core.sfmc_api_client import SFMCAPIClient

client = SFMCAPIClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    account_name="default",
    tenant_subdomain="yourtenant"
)
```

2. Using environment variables (recommended):
   Make sure the required environment variables are set, then simply:

```python
from core.sfmc_api_client import SFMCAPIClient

client = SFMCAPIClient()
```

### Working with Managers

Managers provide high-level interfaces to common SFMC objects.

```python
# Get a Data Extension by key
de = client.data_extensions.get_by_key("my_data_extension_key")
print(de)

# List Data Extensions by name
des = client.data_extensions.get_by_name("Example DE")
print(des)

# Create a new Data Extension (example payload)
new_de = {
    "name": "My New Data Extension",
    "customerKey": "my_new_de_key",
    "fields": [
        {"name": "EmailAddress", "type": "EmailAddress", "isRequired": True, "isPrimaryKey": True},
        {"name": "FirstName", "type": "Text", "isRequired": False}
    ]
}
response = client.data_extensions.create(new_de)
print(response)

# Retrieve Subscriber by key
subscriber = client.subscribers.get_by_key("subscriber_key_123")
print(subscriber)
```

Note: All current methods are synchronous. Managers are a work in progress and may have limited features.

### Authentication

The client automatically handles OAuth 2.0 client credentials authentication and token refresh.

If needed, you can manually force authentication:

```python
client.authenticate()
```

### Error Handling

Methods may raise exceptions such as:

- AuthenticationError — When authentication fails.
- RequestError — When API requests fail or return errors.

### Future Plans

- Asynchronous support for non-blocking requests.
- Expanded managers and features for additional SFMC objects.
- Better error handling and logging options.

### License

This project is licensed under the MIT License.
