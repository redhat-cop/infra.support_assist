# aap_api_gather

An Ansible role to gather diagnostic output from Ansible Automation Platform (AAP) component APIs (Controller, Hub, Gateway, EDA) and create compressed archives for Red Hat Support Case upload.

## Description

This role gathers diagnostic output from Ansible Automation Platform (AAP) component APIs (Controller, Hub, EDA) and saves them as JSON files. The role can then create a compressed archive of all collected data and prepare it for upload to a Red Hat Support Case via the `rh_case` role.

### Key Features

- **Multi-component support** – Query Controller, Hub, and EDA APIs in a single run
- **Automatic archive creation** – Creates compressed tarball of all collected data
- **Case integration** – Automatically prepares `case_updates_needed` for `rh_case` role
- **Safe filename handling** – Automatically sanitizes endpoint paths for filesystem safety
- **Error resilience** – Failed API requests are logged but don't stop collection

## Requirements

- **On Control Node:**
  - `community.general` collection (for the `archive` module used to create the tarball)

- **AAP API Access:**
  - Valid AAP API token (obtained via `aap_api_token` role or provided directly)
  - Network access to AAP component URLs (Controller, Hub, EDA)

## Role Variables

### Input Variables

| Variable | Description | Type | Required | Default |
|----------|-------------|------|----------|---------|
| `aap_token` | A valid AAP API access token. This is typically provided by running the `infra.support_assist.aap_api_token` role first. Can also be provided via extra-var or environment variable (`AAP_TOKEN` or `aap_token`). | `string` | Yes | — |
| `aap_gateway_url` | The base URL for the AAP Gateway. If provided, this will be used as a fallback for component URLs that are not explicitly set. Can be provided via extra-var or environment variable (`AAP_GATEWAY_URL`). | `string` | No | — |
| `aap_controller_url` | The base URL for the AAP Controller API. If not provided, will default to `aap_gateway_url` if available. Can be provided via extra-var or environment variable (`AAP_CONTROLLER_URL`). | `string` | Conditional* | — |
| `aap_hub_url` | The base URL for the AAP Hub API. If not provided, will default to `aap_gateway_url` if available. Can be provided via extra-var or environment variable (`AAP_HUB_URL`). | `string` | Conditional* | — |
| `aap_eda_url` | The base URL for the AAP EDA API. If not provided, will default to `aap_gateway_url` if available. Can be provided via extra-var or environment variable (`AAP_EDA_URL`). | `string` | Conditional* | — |
| `aap_api_gather_components` | List of AAP components to query. Valid options: `controller`, `hub`, `gateway`, `eda`. | `list` | No | `['controller', 'hub', 'gateway', 'eda']` |
| `aap_api_gather_dest` | Destination directory on the control node where API outputs will be saved. | `string` | No | `/tmp/aap_api_gathers` |
| `aap_validate_certs` | Whether to validate SSL/TLS certificates when making API requests. | `bool` | No | `true` |

\* Required if the corresponding component is in `aap_api_gather_components`

### Output Variables

| Variable | Description | Type |
|----------|-------------|------|
| `case_updates_needed` | This fact is set after successful API collection and archive creation. Contains a list with one dictionary entry: `attachment` (full path to tarball) and `attachmentDescription` (description including hostname, FQDN, and components queried). Ready for use with the `infra.support_assist.rh_case` role. | `list` |

## Dependencies

- This role **should** be run after `infra.support_assist.aap_api_token` to populate the required `aap_token` fact.
- This role **can** be followed by `infra.support_assist.rh_case` to upload the created archive to a Red Hat Support Case.

## Example Playbooks

### Example 1: Basic API Dump (Standalone)

```yaml
---
- name: Gather AAP API Data
  hosts: localhost
  connection: local
  gather_facts: false

  tasks:
    - name: Get AAP API Token
      ansible.builtin.include_role:
        name: infra.support_assist.aap_api_token

    - name: Gather API Data
      ansible.builtin.include_role:
        name: infra.support_assist.aap_api_gather
      vars:
        aap_controller_url: "https://aap-controller.example.com"
        aap_hub_url: "https://aap-hub.example.com"
        aap_api_gather_components:
          - controller
          - hub
```

### Example 2: Full Pipeline (Dump + Case Upload)

```yaml
---
- name: AAP API Dump and Case Upload
  hosts: localhost
  connection: local
  gather_facts: false

  tasks:
    - name: AAP API Dump Block
      block:
        - name: Get AAP API Token
          ansible.builtin.include_role:
            name: infra.support_assist.aap_api_token

        - name: Gather API Data
          ansible.builtin.include_role:
            name: infra.support_assist.aap_api_gather
          vars:
            aap_controller_url: "https://aap-controller.example.com"
            aap_hub_url: "https://aap-hub.example.com"

      always:
        - name: Clear AAP Token
          ansible.builtin.include_role:
            name: infra.support_assist.aap_api_token
            tasks_from: clear_token.yml

    - name: Case Upload Block
      when:
        - upload | default(true) | bool
        - case_updates_needed is defined
        - case_updates_needed | length > 0
      block:
        - name: Get Red Hat API Token
          ansible.builtin.include_role:
            name: infra.support_assist.rh_token_refresh

        - name: Upload to Case
          ansible.builtin.include_role:
            name: infra.support_assist.rh_case
          vars:
            case_id: "01234567"
```

### Example 3: Using Environment Variables

```bash
export AAP_CONTROLLER_URL="https://aap-controller.example.com"
export AAP_HUB_URL="https://aap-hub.example.com"
export AAP_TOKEN="your-token-here"

ansible-playbook playbook.yml
```

### Using the Collection Playbook (Recommended)

The recommended way to use this role is via the main playbook, which handles token management and upload logic:

```shell
# Set your tokens as environment variables
export REDHAT_OFFLINE_TOKEN="YOUR_OFFLINE_TOKEN_HERE"
export AAP_CONTROLLER_URL="https://aap-controller.example.com"
export AAP_HUB_URL="https://aap-hub.example.com"

# Run the full pipeline
ansible-playbook playbooks/aap_api_gather.yml \
  -e case_id=01234567 \
  -e upload=true
```

## Output

The role creates the following structure on the control node:

```text
{{ aap_api_gather_dest }}/{{ inventory_hostname }}/{{ component_name }}/{{ sanitized_endpoint_path }}.json
```

For example:
```text
/tmp/aap_api_gathers/localhost/controller/api_controller_v2_ping_.json
/tmp/aap_api_gathers/localhost/controller/api_controller_v2_instances_.json
/tmp/aap_api_gathers/localhost/hub/pulp_api_v3_status_.json
```

After collection, the role creates a compressed tarball:
```text
{{ aap_api_gather_dest }}/aap-api-gather-{{ hostname }}-{{ date }}-{{ time }}.tar.gz
```

The tarball contains all JSON files from the collection and is automatically added to `case_updates_needed` for upload via the `rh_case` role.

## API Endpoints

The role queries predefined API endpoints for each component. These are defined in `vars/main.yml`:

| Component | Endpoints |
|-----------|-----------|
| **Controller** | `/api/controller/v2/ping/`, `/api/controller/v2/instances/`, `/api/controller/v2/settings/all/` |
| **Hub** | `/pulp/api/v3/status/`, `/pulp/api/v3/tasks/` |
| **EDA** | (Currently empty - can be customized) |

## How It Works

```text
┌─────────────────────────────────────────────────────────────────┐
│                      aap_api_gather                             │
├─────────────────────────────────────────────────────────────────┤
│  1. Pre-validation                                              │
│     ├── Verify API token is available                           │
│     └── Verify component URLs are provided                      │
│                                                                 │
│  2. Gather API Data                                             │
│     └── Loop through selected components                        │
│         └── Query each endpoint and save as JSON                │
│                                                                 │
│  3. Create Archive                                              │
│     ├── Compress all collected JSON files                       │
│     └── Set case_updates_needed fact                            │
└─────────────────────────────────────────────────────────────────┘
```

## Notes

- The role automatically sanitizes endpoint paths to create safe filenames (replacing `/`, `?`, `&`, `=` with `_`).
- Failed API requests are logged but do not stop the collection process (the role uses `ignore_errors: true`).
- The archive creation step only runs if the source directory exists and contains files.
- All operations run on `localhost` (control node) using `delegate_to: localhost` and `run_once: true`.

## License

GPL-3.0-or-later

## Author Information

- **Author:** Lenny Shirley
- **Company:** Red Hat
- **Collection:** [infra.support_assist](https://github.com/redhat-cop/infra.support_assist)

## Related Roles

This role is typically used in conjunction with other roles in the `infra.support_assist` collection:

- `aap_api_token` – Obtain and manage OAuth2 API tokens for AAP
- `rh_case` – Create and update Red Hat support cases (unified role)
- `rh_token_refresh` – Handle Red Hat API token authentication and caching
