# aap_api_token

An Ansible role to obtain and manage OAuth2 API tokens for Ansible Automation Platform (AAP).

## Description

This role automates the process of authenticating with Ansible Automation Platform and obtaining an OAuth2 token for API operations. It intelligently detects the AAP Controller version and uses the appropriate Ansible collection (`ansible.controller` for legacy versions or `ansible.platform` for newer versions) to handle token management.

### Key Features

- **Automatic version detection** – Probes the AAP API to determine whether legacy or modern API paths are needed
- **Multi-platform support** – Works with both AAP Gateway (2.5+) and standalone Automation Controller
- **Environment variable integration** – Reads credentials from environment variables by default
- **Token lifecycle management** – Create tokens for operations and clean them up afterwards
- **Secure by design** – Sensitive data is protected with `no_log` options

## Requirements

- Ansible >= 2.15.0
- One of the following collections:
  - `ansible.controller` – For AAP Controller versions < 4.6.0
  - `ansible.platform` – For AAP Controller versions >= 4.6.0

## Role Variables

### Connection Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `aap_gateway_url` | Full URL to the AAP Gateway (e.g., `https://gateway.example.com`) | `$AAP_GATEWAY_URL` | One of gateway/controller URL |
| `aap_controller_url` | Full URL to the AAP Controller (e.g., `https://controller.example.com`) | `$AAP_CONTROLLER_URL` | One of gateway/controller URL |
| `aap_hostname` | Hostname extracted from the provided URL | Auto-derived | No |
| `aap_validate_certs` | Whether to validate SSL/TLS certificates | `true` (or `$AAP_VALIDATE_CERTS`) | No |

> **Note:** Provide either `aap_gateway_url` OR `aap_controller_url`, but not both.

### Authentication Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `aap_username` | Username for AAP authentication | `$AAP_USERNAME` | Yes (if no token) |
| `aap_password` | Password for AAP authentication | `$AAP_PASSWORD` | Yes (if no token) |
| `aap_token` | Existing OAuth2 token (skips token creation if provided) | `$AAP_TOKEN` | No |

> **Note:** Either provide `aap_token` OR both `aap_username` and `aap_password`.

### Behavior Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `aap_api_token_no_log` | Suppress sensitive output in logs (actually used in tasks) | `true` |
| `aap_controller_full_version` | AAP Controller version (auto-detected if not set) | Auto-detected |

## Entry Points

### `main` (default)

Obtains an OAuth2 token from AAP using username/password credentials.

**Sets the following facts:**

- `aap_token` – The OAuth2 token for API operations
- `controller_oauthtoken` – Alias for compatibility with `ansible.controller` collection
- `aap_controller_full_version` – Detected AAP Controller version
- `aap_controller_needs_legacy_paths` – Boolean indicating if legacy API paths are required

### `clear_token`

Revokes/deletes the OAuth2 token created during the session.

**Usage:** Include this entry point at the end of your playbook to clean up temporary tokens.

## Dependencies

This role requires one of the following collections based on your AAP version:

```yaml
# For AAP 2.5+ (Gateway)
collections:
  - ansible.platform

# For Automation Controller < 4.6.0
collections:
  - ansible.controller
```

## Example Playbooks

### Basic Usage with Environment Variables

Set environment variables before running:

```bash
export AAP_GATEWAY_URL="https://gateway.example.com"
export AAP_USERNAME="admin"
export AAP_PASSWORD="secretpassword"
```

```yaml
---
- name: Get AAP API Token
  hosts: localhost
  connection: local
  gather_facts: false

  tasks:
    - name: Obtain API token
      ansible.builtin.include_role:
        name: infra.support_assist.aap_api_token

    - name: Use the token for API operations
      ansible.builtin.debug:
        msg: "Token obtained successfully. Controller version: {{ aap_controller_full_version }}"

    - name: Clean up token when done
      ansible.builtin.include_role:
        name: infra.support_assist.aap_api_token
        tasks_from: clear_token.yml
```

### Explicit Variables

```yaml
---
- name: Get AAP API Token with explicit variables
  hosts: localhost
  connection: local
  gather_facts: false

  vars:
    aap_controller_url: "https://controller.example.com"
    aap_username: "admin"
    aap_password: "{{ vault_aap_password }}"
    aap_validate_certs: true

  tasks:
    - name: Obtain API token
      ansible.builtin.include_role:
        name: infra.support_assist.aap_api_token

    - name: Perform operations with token
      ansible.builtin.uri:
        url: "{{ aap_controller_url }}/api/v2/job_templates/"
        method: GET
        headers:
          Authorization: "Bearer {{ aap_token }}"
        validate_certs: "{{ aap_validate_certs }}"
      register: job_templates

    - name: Clean up token
      ansible.builtin.include_role:
        name: infra.support_assist.aap_api_token
        tasks_from: clear_token.yml
```

### Using with AAP Gateway (AAP 2.5+)

```yaml
---
- name: Get token via AAP Gateway
  hosts: localhost
  connection: local
  gather_facts: false

  vars:
    aap_gateway_url: "https://gateway.example.com"
    aap_username: "admin"
    aap_password: "{{ vault_aap_password }}"

  tasks:
    - name: Obtain API token from Gateway
      ansible.builtin.include_role:
        name: infra.support_assist.aap_api_token

    - name: Display token info
      ansible.builtin.debug:
        msg: |
          Token created successfully!
          AAP Version: {{ aap_controller_full_version }}
          Uses legacy paths: {{ aap_controller_needs_legacy_paths }}
```

## How It Works

```text
┌─────────────────────────────────────────────────────────────────┐
│                        aap_api_token                            │
├─────────────────────────────────────────────────────────────────┤
│  1. Pre-validation                                              │
│     └── Verify required variables are set                       │
│                                                                 │
│  2. Version Detection                                           │
│     ├── Try: /api/controller/v2/ping/ (new path)                │
│     └── Fallback: /api/v2/ping/ (legacy path)                   │
│                                                                 │
│  3. Token Creation                                              │
│     ├── If version >= 4.6.0 → ansible.platform.token            │
│     └── If version < 4.6.0  → ansible.controller.token          │
│                                                                 │
│  4. Set Facts                                                   │
│     └── aap_token, controller_oauthtoken, version info          │
└─────────────────────────────────────────────────────────────────┘
```

## Troubleshooting

### Common Issues

**"Either 'aap_gateway_url' or 'aap_controller_url' must be provided"**

- Ensure you set one (and only one) of these variables
- Check that your environment variables are exported correctly

**"Either 'aap_token' must be provided, or both 'aap_username' and 'aap_password'"**

- Provide complete credentials: both username AND password
- Or provide an existing token via `aap_token`

**"Could not determine AAP Controller version"**

- Verify the URL is correct and reachable
- Check network connectivity and firewall rules
- Ensure SSL certificates are valid (or set `aap_validate_certs: false` for testing)

### Debug Mode

Enable verbose output for troubleshooting:

```yaml
aap_api_token_no_log: false  # Show sensitive data in logs (use only for debugging!)
```

## License

GPL-3.0-or-later

## Author Information

- **Author:** Lenny Shirley
- **Company:** Red Hat
- **Collection:** [infra.support_assist](https://github.com/redhat-cop/infra.support_assist)

## Related Roles

This role is typically used in conjunction with other roles in the `infra.support_assist` collection:

- `aap_api_gather` – Gather diagnostic output from AAP component APIs (Controller, Hub, Gateway, EDA)
- `rh_case` – Create and update Red Hat support cases (unified role)
- `rh_token_refresh` – Handle Red Hat API token authentication and caching
- `ocp_must_gather` – Gather OpenShift diagnostics
- `sos_report` – Generate SOS reports
