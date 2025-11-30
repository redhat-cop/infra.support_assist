# infra.support_assist.rh_case_create

This role creates a **new Red Hat Support Case** via the API, sets the mandatory fields (`Product`, `Severity`, `Summary`), and retrieves the newly generated Case ID. This role is a foundational step for full automation pipelines.

## Requirements

* **On Control Node (Execution Host):**
    * The control node must have network access to the **Red Hat API endpoint** (and the necessary proxy configured if running in QA/Staging environments).

## Role Variables

### Input Variables

| Variable | Description | Type | Required | Notes |
| :--- | :--- | :--- | :--- | :--- |
| `rh_token_refresh_api_access_token` | **(Required)** A valid, current Red Hat API access token. This is typically provided as a fact by the `infra.support_assist.rh_token_refresh` role. | `string` | Yes | Supplied as a fact. |
| `case_summary` | **(Required)** The mandatory title/summary for the new support case. | `string` | Yes | |
| `case_description` | **(Required)** The detailed description of the issue. | `string` | Yes | |
| `case_product` | **(Required)** The exact, valid name of the Red Hat product (e.g., `"OpenShift Container Platform"`). | `string` | Yes | **See valid options below.** |
| `case_product_version` | **(Required)** The normalized base version string for the product (e.g., `"4.16"` for OpenShift, or `"8.9"` for RHEL). | `string` | Yes | |
| `case_type` | **(Required)** The mandatory type of issue (e.g., `"Configuration Issue"`). | `string` | Yes | **See valid options below.** |
| `case_severity` | **(Required)** The severity level (e.g., `"3 (Normal)"`). | `string` | Yes | **See valid options below.** |

### Output Variables

| Variable | Description | Type |
| :--- | :--- | :--- |
| `case_id` | The ID of the newly created support case (e.g., `00000000`). Set as a global fact for subsequent roles (`rh_case_update`). | `string` |
| `account_name` | The name of the organization associated with the API token. | `string` |
| `accountNumberRef` | The numeric account ID required for API submission. | `string` |

## Dependencies

* This role **must** be run after `infra.support_assist.rh_token_refresh` to populate the required `rh_token_refresh_api_access_token` fact.

## Valid Input Options

For the fields **`case_product`**, **`case_type`**, and **`case_severity`**, the acceptable values must exactly match the Red Hat Support API's lookup tables.

Please consult the dedicated documentation file for the full list of valid options:

[**Full Case Option Lists:** `rh_case_create/docs/CASE_OPTIONS.md`](../rh_case_create/docs/CASE_OPTIONS.md)

## Example Playbook

### Example 1: Create a case for a cluster (typical pipeline use)

~~~yaml
- name: Create New Red Hat Support Case 
  hosts: localhost
  connection: local
  gather_facts: false

  vars:
    # --- REQUIRED AUTHENTICATION INPUTS ---
    offline_token: "YOUR_OFFLINE_TOKEN_HERE" 

    # --- REQUIRED CASE INPUTS ---
    case_summary: "Example Support Case Created via Ansible Automation"
    case_description: "This is an example support case created via the infra.support_assist.rh_case_create role in Ansible."
    case_product: "Red Hat Enterprise Linux"
    case_product_version: "8.9"
    case_type: "Defect / Bug"
    case_severity: "2 (High)"

  tasks:
    - name: Ensure API Access Token is fresh
      ansible.builtin.include_role:
        name: infra.support_assist.rh_token_refresh

    - name: Call rh_case_create role
      ansible.builtin.include_role:
        name: infra.support_assist.rh_case_create
~~~

You can use a playbook as an example as [playbooks/rh_case_create_only.yml](../../playbooks/rh_case_create_only.yml)

## License

GPL-3.0-or-later

## Author Information

- Diego Felipe Mateus