# rh_case_update

An Ansible role to update Red Hat Support Cases by uploading attachments or adding comments.

## Description

This role updates an existing Red Hat Support Case by uploading file attachments or adding comments. It is designed to run on `localhost` and iterates over a list of updates defined in the `case_updates_needed` variable.

### Key Features

- **File uploads** – Uploads files of any size using `curl` for robust streaming support
- **Comment support** – Adds comments in either `markdown` or `plaintext` format
- **Batch operations** – Process multiple attachments and comments in a single run
- **Flexible input** – Works with manually specified files or output from other roles

## Requirements

- **On Control Node:**
  - `curl`: The `curl` command-line utility must be installed and in the system's `PATH`
  - Network access to the Red Hat API endpoint

## Role Variables

### Input Variables

| Variable | Description | Type | Required | Default |
|----------|-------------|------|----------|---------|
| `case_id` | The Red Hat Support Case number (e.g., `01234567`). | `string` | Yes | — |
| `rh_token_refresh_api_access_token` | A valid Red Hat API access token. Typically provided by the `rh_token_refresh` role. | `string` | Yes | Supplied as fact |
| `case_updates_needed` | A list of objects defining attachments to upload or comments to add. | `list` | Yes | — |
| `rh_case_update_timeout` | Timeout in seconds for each `curl` file upload command. | `int` | No | `1800` (30 min) |

### Advanced Configuration Variables

| Variable | Description | Type | Required | Default |
|----------|-------------|------|----------|---------|
| `rh_case_update_use_proxy` | Whether to use a proxy for API requests. | `bool` | No | `false` |
| `rh_case_update_http_proxy` | HTTP/HTTPS proxy URL for API requests (e.g., `http://proxy.example.com:8080`). | `string` | No | `""` |
| `rh_case_update_no_log` | Suppress sensitive output in logs. | `bool` | No | `true` |

### `case_updates_needed` Object Structure

Each item in the `case_updates_needed` list can contain:

| Field | Description | Type | Required |
|-------|-------------|------|----------|
| `attachment` | Full path to the local file to upload. | `string` | No* |
| `attachmentDescription` | Description for the file being attached. | `string` | No |
| `comment` | Text of the comment to add to the case. | `string` | No* |
| `commentType` | Format of the comment: `markdown` (default) or `plaintext`. | `string` | No |

> **\*** Each object must contain either `attachment` or `comment` (or both).

## Dependencies

- This role **must** be run after `infra.support_assist.rh_token_refresh` to populate the required `rh_token_refresh_api_access_token` fact.

## Example Playbooks

### Example 1: Add a Comment

```yaml
---
- name: Add comment to Red Hat Case
  hosts: localhost
  connection: local
  gather_facts: false

  vars:
    case_id: "01234567"
    offline_token: "YOUR_OFFLINE_TOKEN_HERE"  # Use Ansible Vault!
    case_updates_needed:
      - comment: "This is a test comment added via Ansible."
        commentType: "plaintext"

  tasks:
    - name: Refresh API token
      ansible.builtin.include_role:
        name: infra.support_assist.rh_token_refresh

    - name: Update the case
      ansible.builtin.include_role:
        name: infra.support_assist.rh_case_update
```

### Example 2: Upload a Local File

```yaml
---
- name: Upload file to Red Hat Case
  hosts: localhost
  connection: local
  gather_facts: false

  vars:
    case_id: "01234567"
    offline_token: "{{ vault_offline_token }}"
    case_updates_needed:
      - attachment: "/var/log/my-custom-app.log"
        attachmentDescription: "Custom log file from my-server-01"

  tasks:
    - name: Refresh API token
      ansible.builtin.include_role:
        name: infra.support_assist.rh_token_refresh

    - name: Upload file to case
      ansible.builtin.include_role:
        name: infra.support_assist.rh_case_update
```

### Example 3: Upload Multiple Files and Add a Comment

```yaml
---
- name: Perform multiple case updates
  hosts: localhost
  connection: local
  gather_facts: false

  vars:
    case_id: "01234567"
    offline_token: "{{ vault_offline_token }}"
    case_updates_needed:
      - attachment: "/tmp/sos_reports/case_01234567/server1/sosreport-server1.tar.xz"
        attachmentDescription: "SOS Report from server1"
      - attachment: "/tmp/sos_reports/case_01234567/server2/sosreport-server2.tar.xz"
        attachmentDescription: "SOS Report from server2"
      - comment: |
          ### Automation Complete

          Attached are the `sosreport` files from the following hosts:

          * `server1.example.com`
          * `server2.example.com`
        commentType: "markdown"

  tasks:
    - name: Refresh API token
      ansible.builtin.include_role:
        name: infra.support_assist.rh_token_refresh

    - name: Update case with files and comment
      ansible.builtin.include_role:
        name: infra.support_assist.rh_case_update
```

### Using the Collection Playbook

```shell
# Set your offline token as an environment variable
export REDHAT_OFFLINE_TOKEN="YOUR_OFFLINE_TOKEN_HERE"

# Upload a file
ansible-playbook infra.support_assist.rh_case_update \
  -e case_id=01234567 \
  -e "case_updates_needed=[{'attachment': '/path/to/file.log', 'attachmentDescription': 'Manual log upload'}]"

# Add a comment
ansible-playbook infra.support_assist.rh_case_update \
  -e case_id=01234567 \
  -e "case_updates_needed=[{'comment': 'Adding a comment via playbook.', 'commentType': 'plaintext'}]"
```

## How It Works

```text
┌─────────────────────────────────────────────────────────────────┐
│                        rh_case_update                           │
├─────────────────────────────────────────────────────────────────┤
│  1. Pre-validation                                              │
│     └── Verify case_id and access token are set                 │
│                                                                 │
│  2. Loop through case_updates_needed                            │
│     ├── If attachment → Upload file via curl                    │
│     └── If comment → POST comment via API                       │
│                                                                 │
│  3. Report results                                              │
│     └── Display success/failure for each update                 │
└─────────────────────────────────────────────────────────────────┘
```

## License

GPL-3.0-or-later

## Author Information

- **Author:** Lenny Shirley
- **Company:** Red Hat
- **Collection:** [infra.support_assist](https://github.com/redhat-cop/infra.support_assist)
