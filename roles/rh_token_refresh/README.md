# rh_token_refresh

An Ansible role to retrieve and manage Red Hat API access tokens.

## Description

The `rh_token_refresh` role retrieves an access token for the Red Hat API using an offline token. The obtained token is cached locally to manage its lifecycle and minimize unnecessary API calls. This role is a prerequisite for other roles in this collection that interact with the Red Hat Support API.

### Key Features

- **Token caching** – Stores tokens locally to reduce API calls and improve performance
- **Automatic refresh** – Checks token age and refreshes when expired
- **Environment variable support** – Reads offline token from environment variables by default
- **Configurable cache** – Customize cache location and token validity period

## Requirements

None. This role runs on `localhost` using only built-in Ansible modules.

## Role Variables

### Input Variables

| Variable | Description | Type | Required | Default |
|----------|-------------|------|----------|---------|
| `rh_token_refresh_api_offline_token` | Your Red Hat offline token used to acquire the API access token. | `string` | Yes | `{{ offline_token \| default(lookup('env', 'REDHAT_OFFLINE_TOKEN')) }}` |
| `rh_token_refresh_token_cache_file` | Full path to the file where the access token and timestamp will be cached. | `path` | No | `/tmp/redhat_refresh_token.json` |
| `rh_token_refresh_token_max_age_seconds` | Maximum age (in seconds) of a cached token before it's considered expired. | `int` | No | `900` (15 minutes) |
| `rh_token_refresh_api_token_url` | Full URL for the Red Hat SSO token endpoint. | `string` | No | `https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token` |
| `rh_token_refresh_api_base_url` | Base URL for the Red Hat API (e.g., `https://api.access.redhat.com`). | `string` | No | `https://api.access.redhat.com` |
| `rh_token_refresh_use_proxy` | Whether to use a proxy for API requests. | `bool` | No | `false` |
| `rh_token_refresh_http_proxy` | HTTP/HTTPS proxy URL for API requests (e.g., `http://proxy.example.com:8080`). | `string` | No | `""` |
| `rh_token_refresh_no_log` | Suppress sensitive output in logs. | `bool` | No | `true` |

### Output Variables

| Variable | Description | Type |
|----------|-------------|------|
| `rh_token_refresh_api_access_token` | The valid Red Hat API access token. Retrieved from cache or newly obtained from Red Hat SSO. | `string` |

## Dependencies

None.

## Obtaining an Offline Token

> **💡 How to Generate a Red Hat Offline Token**
>
> 1. Navigate to the Red Hat API Token management page: [https://access.redhat.com/management/api](https://access.redhat.com/management/api)
> 2. Click the **"Generate Token"** button.
> 3. Log in with your Red Hat customer portal credentials if prompted.
> 4. A new offline token will be generated. **Copy this token immediately**, as Red Hat notes, "Tokens are only displayed once and are not stored. They will expire after 30 days of inactivity".

## Example Playbooks

### Example 1: Basic Usage

```yaml
---
- name: Get Red Hat API Access Token
  hosts: localhost
  connection: local
  gather_facts: false

  vars:
    # Provide the token directly (Ansible Vault recommended!)
    offline_token: "YOUR_REDHAT_OFFLINE_TOKEN_HERE"

  tasks:
    - name: Retrieve Red Hat API access token
      ansible.builtin.include_role:
        name: infra.support_assist.rh_token_refresh

    - name: Display token status
      ansible.builtin.debug:
        msg: "Access token retrieved successfully"
```

### Example 2: Using Environment Variable

```shell
# Set the offline token as an environment variable
export REDHAT_OFFLINE_TOKEN="YOUR_OFFLINE_TOKEN_HERE"
```

```yaml
---
- name: Get Red Hat API Access Token (from environment)
  hosts: localhost
  connection: local
  gather_facts: false

  tasks:
    - name: Retrieve Red Hat API access token
      ansible.builtin.include_role:
        name: infra.support_assist.rh_token_refresh
      # Token automatically read from REDHAT_OFFLINE_TOKEN env var

    - name: Use the token in a subsequent task
      ansible.builtin.uri:
        url: "https://api.access.redhat.com/support/v1/user/info"
        method: GET
        headers:
          Authorization: "Bearer {{ rh_token_refresh_api_access_token }}"
      register: user_info
```

### Example 3: Custom Cache Configuration

```yaml
---
- name: Get Red Hat API Access Token with custom cache
  hosts: localhost
  connection: local
  gather_facts: false

  vars:
    offline_token: "{{ vault_offline_token }}"

  tasks:
    - name: Retrieve Red Hat API access token
      ansible.builtin.include_role:
        name: infra.support_assist.rh_token_refresh
      vars:
        rh_token_refresh_token_cache_file: "/home/ansible/.redhat_api_token.json"
        rh_token_refresh_token_max_age_seconds: 3600  # Cache for 1 hour
```

## How It Works

```text
┌─────────────────────────────────────────────────────────────────┐
│                       rh_token_refresh                          │
├─────────────────────────────────────────────────────────────────┤
│  1. Pre-validation                                              │
│     └── Verify offline_token is provided                        │
│                                                                 │
│  2. Check cache                                                 │
│     ├── If cache exists and token is fresh → Use cached token   │
│     └── If cache missing or expired → Proceed to refresh        │
│                                                                 │
│  3. Token refresh (if needed)                                   │
│     ├── POST to Red Hat SSO with offline_token                  │
│     ├── Receive new access_token                                │
│     └── Store in cache file with timestamp                      │
│                                                                 │
│  4. Set fact                                                    │
│     └── rh_token_refresh_api_access_token                       │
└─────────────────────────────────────────────────────────────────┘
```

## License

GPL-3.0-or-later

## Author Information

- **Author:** Lenny Shirley
- **Company:** Red Hat
- **Collection:** [infra.support_assist](https://github.com/redhat-cop/infra.support_assist)

## Related Roles

This role is typically used in conjunction with other roles in the `infra.support_assist` collection:

- `rh_case` – Create and update Red Hat support cases (unified role)
- `ocp_must_gather` – Gather OpenShift diagnostics
- `sos_report` – Generate SOS reports
- `aap_api_dump` – Gather diagnostic output from AAP component APIs
