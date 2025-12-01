# rh_case_create

An Ansible role to create new Red Hat Support Cases via the API.

## Description

This role creates a **new Red Hat Support Case** via the Red Hat API, sets the mandatory fields (`Product`, `Severity`, `Summary`, `Description`), and retrieves the newly generated Case ID. This role is a foundational step for full automation pipelines that need to programmatically open support cases.

### Key Features

- **Automated case creation** – Creates support cases via the Red Hat Support API
- **Case ID retrieval** – Returns the newly created case ID for use in subsequent tasks
- **Template-based comments** – Supports Jinja2 templates for customizable initial case comments
- **Account validation** – Retrieves and validates account information from the API token

## Requirements

- **On Control Node (Execution Host):**
  - Network access to the **Red Hat API endpoint** (`https://api.access.redhat.com`)
  - A valid Red Hat API access token (provided by the `rh_token_refresh` role)

## Role Variables

### Input Variables

| Variable | Description | Type | Required | Default |
|----------|-------------|------|----------|---------|
| `rh_token_refresh_api_access_token` | A valid, current Red Hat API access token. Typically provided as a fact by the `rh_token_refresh` role. | `string` | Yes | Supplied as fact |
| `case_summary` | The mandatory title/summary for the new support case. | `string` | Yes | — |
| `case_description` | The detailed description of the issue. | `string` | Yes | — |
| `case_product` | The exact, valid name of the Red Hat product (e.g., `"OpenShift Container Platform"`). | `string` | Yes | — |
| `case_product_version` | The normalized base version string for the product (e.g., `"4.16"` for OpenShift, `"8.9"` for RHEL). | `string` | Yes | — |
| `case_type` | The mandatory type of issue (e.g., `"Configuration Issue"`). | `string` | Yes | — |
| `case_severity` | The severity level (e.g., `"3 (Normal)"`). | `string` | Yes | — |
| `cluster_id` | Optional cluster ID to associate with the case. | `string` | No | — |

### Output Variables

| Variable | Description | Type |
|----------|-------------|------|
| `case_id` | The ID of the newly created support case (e.g., `00000000`). Set as a global fact for subsequent roles. | `string` |
| `account_name` | The name of the organization associated with the API token. | `string` |
| `accountNumberRef` | The numeric account ID required for API submission. | `string` |

### Advanced Configuration Variables

| Variable | Description | Type | Required | Default |
|----------|-------------|------|----------|---------|
| `rh_case_create_http_proxy` | HTTP/HTTPS proxy URL for API requests (e.g., `http://proxy.example.com:8080`). | `string` | No | `""` |
| `rh_case_create_use_proxy` | Whether to use proxy for this role (falls back to `use_proxy`). | `bool` | No | `false` |
| `rh_case_create_no_log` | Suppress sensitive output in logs. | `bool` | No | `true` |

## Dependencies

- This role **must** be run after `infra.support_assist.rh_token_refresh` to populate the required `rh_token_refresh_api_access_token` fact.

## Valid Input Options

For the fields **`case_product`**, **`case_type`**, and **`case_severity`**, the acceptable values must exactly match the Red Hat Support API's lookup tables.

Please consult the dedicated documentation file for the full list of valid options:

**[Full Case Option Lists: `docs/CASE_OPTIONS.md`](docs/CASE_OPTIONS.md)**

## Example Playbooks

### Example 1: Create a Support Case (Typical Pipeline Use)

```yaml
---
- name: Create New Red Hat Support Case
  hosts: localhost
  connection: local
  gather_facts: false

  vars:
    # --- REQUIRED AUTHENTICATION INPUTS ---
    offline_token: "YOUR_OFFLINE_TOKEN_HERE"  # Use Ansible Vault!

    # --- REQUIRED CASE INPUTS ---
    case_summary: "Example Support Case Created via Ansible Automation"
    case_description: |
      This is an example support case created via the
      infra.support_assist.rh_case_create role in Ansible.
    case_product: "Red Hat Enterprise Linux"
    case_product_version: "8.9"
    case_type: "Defect / Bug"
    case_severity: "2 (High)"

  tasks:
    - name: Ensure API Access Token is fresh
      ansible.builtin.include_role:
        name: infra.support_assist.rh_token_refresh

    - name: Create the support case
      ansible.builtin.include_role:
        name: infra.support_assist.rh_case_create

    - name: Display the new case ID
      ansible.builtin.debug:
        msg: "Created case: {{ case_id }}"
```

### Example 2: Create a Case for OpenShift

```yaml
---
- name: Create OpenShift Support Case
  hosts: localhost
  connection: local
  gather_facts: false

  vars:
    offline_token: "{{ vault_offline_token }}"
    case_summary: "Pod scheduling issues after upgrade"
    case_description: |
      After upgrading from OCP 4.15 to 4.16, pods are failing to schedule
      on worker nodes. The scheduler reports resource constraints but
      nodes show available capacity.
    case_product: "OpenShift Container Platform"
    case_product_version: "4.16"
    case_type: "Defect / Bug"
    case_severity: "2 (High)"

  tasks:
    - name: Refresh API token
      ansible.builtin.include_role:
        name: infra.support_assist.rh_token_refresh

    - name: Create support case
      ansible.builtin.include_role:
        name: infra.support_assist.rh_case_create
```

### Using the Collection Playbook

You can also use the provided collection playbook directly:

```shell
# Set your offline token as an environment variable
export REDHAT_OFFLINE_TOKEN="YOUR_OFFLINE_TOKEN_HERE"

# Run the playbook
ansible-playbook infra.support_assist.rh_case_create_only \
  -e case_summary="Request for documentation update" \
  -e case_description="Need clarification on X." \
  -e case_severity="4 (Low)" \
  -e case_product="Red Hat Ansible Automation Platform" \
  -e case_product_version="2.4" \
  -e case_type="Documentation Issue"
```

See the example playbook: [`playbooks/rh_case_create_only.yml`](../../playbooks/rh_case_create_only.yml)

## Customizing the Case Comment Template

The content of the automatic comment posted after case creation can be customized via the Jinja2 template:

**[`templates/support_case_create.j2`](templates/support_case_create.j2)**

## License

GPL-3.0-or-later

## Author Information

- **Author:** Diego Felipe Mateus
- **Company:** Red Hat
- **Collection:** [infra.support_assist](https://github.com/redhat-cop/infra.support_assist)
