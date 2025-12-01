# sos_report

An Ansible role to gather SOS reports from managed hosts for Red Hat Support Cases.

## Description

This role generates an `sosreport` on one or more target hosts, fetches the resulting archives to the control node, and prepares them for upload to a Red Hat Support Case. The SOS report contains system configuration and diagnostic information commonly requested by Red Hat support engineers.

### Key Features

- **Multi-host collection** – Gather reports from multiple hosts in a single run
- **Automatic package installation** – Installs the `sos` package if not present
- **AAP containerized support** – Special handling for AAP containerized environments
- **Cleanup options** – Optionally remove reports from target hosts after fetching
- **Case-organized storage** – Reports are organized by case ID and hostname

## Requirements

- **On Target Hosts:**
  - The `sos` package (will be installed automatically by the role)
  - Root or sudo privileges for running `sos report`

## Role Variables

### Input Variables

| Variable | Description | Type | Required | Default |
|----------|-------------|------|----------|---------|
| `case_id` | Red Hat Support Case number (e.g., `01234567`). Used for naming and organization. | `string` | Yes | — |
| `sos_report_dest` | Base directory on the control node where fetched reports are stored. | `path` | No | `/tmp/sos_reports` |
| `sos_report_cleanup` | Remove the generated sosreport from target hosts after fetching. | `bool` | No | `true` (via `clean` variable) |
| `sos_report_aap_containerized` | Enable AAP containerized-specific options for the SOS report. | `bool` | No | `false` (via `containerized` variable) |

### Output Variables

| Variable | Description | Type |
|----------|-------------|------|
| `case_updates_needed` | List of objects describing the fetched files for upload by `rh_case_update`. | `list` |

### Output Directory Structure

Reports are organized on the control node as:

```text
{{ sos_report_dest }}/
└── case_{{ case_id }}/
    ├── {{ hostname_1 }}/
    │   └── sosreport-hostname1-01234567-20251027150000.tar.xz
    └── {{ hostname_2 }}/
        └── sosreport-hostname2-01234567-20251027150100.tar.xz
```

## Dependencies

None.

## Example Playbooks

### Example 1: Basic SOS Report Collection

```yaml
---
- name: Gather SOS Reports
  hosts: all
  gather_facts: false

  vars:
    case_id: "01234567"

  tasks:
    - name: Gather SOS report
      ansible.builtin.include_role:
        name: infra.support_assist.sos_report
```

### Example 2: Collect and Clean Up

```yaml
---
- name: Gather SOS Reports with cleanup
  hosts: all
  gather_facts: false

  vars:
    case_id: "01234567"
    sos_report_cleanup: true
    sos_report_dest: "/data/support_files"

  tasks:
    - name: Gather SOS report and remove from target
      ansible.builtin.include_role:
        name: infra.support_assist.sos_report
```

### Example 3: AAP Containerized Environment

```yaml
---
- name: Gather SOS Reports from AAP nodes
  hosts: aap_nodes
  gather_facts: false

  vars:
    case_id: "01234567"
    sos_report_aap_containerized: true
    sos_report_cleanup: true

  tasks:
    - name: Gather AAP-specific SOS report
      ansible.builtin.include_role:
        name: infra.support_assist.sos_report
```

### Using the Collection Playbook (Recommended)

The recommended way to use this role is via the main playbook, which handles token refresh and upload logic:

```shell
# Set your Red Hat token as an environment variable
export REDHAT_OFFLINE_TOKEN="YOUR_OFFLINE_TOKEN_HERE"

# Run the full pipeline
ansible-playbook -i inventory infra.support_assist.sos_report \
  -e case_id=01234567 \
  -e upload=true \
  -e clean=true
```

### Full Pipeline Example (with upload)

```yaml
---
- name: Gather and Upload SOS Reports
  hosts: all
  gather_facts: false

  vars:
    case_id: "01234567"
    sos_report_cleanup: true

  tasks:
    - name: Gather SOS report
      ansible.builtin.include_role:
        name: infra.support_assist.sos_report

- name: Upload Reports to Case
  hosts: localhost
  connection: local
  gather_facts: false

  vars:
    offline_token: "{{ vault_offline_token }}"

  tasks:
    - name: Refresh API token
      ansible.builtin.include_role:
        name: infra.support_assist.rh_token_refresh

    - name: Upload reports to case
      ansible.builtin.include_role:
        name: infra.support_assist.rh_case_update
```

## How It Works

```text
┌─────────────────────────────────────────────────────────────────┐
│                         sos_report                              │
├─────────────────────────────────────────────────────────────────┤
│  1. Pre-validation                                              │
│     └── Verify case_id is provided                              │
│                                                                 │
│  2. Install (if needed)                                         │
│     └── Ensure sos package is installed                         │
│                                                                 │
│  3. Generate                                                    │
│     └── Run sos report with case ID and options                 │
│                                                                 │
│  4. Fetch                                                       │
│     └── Copy report to control node organized by case/host      │
│                                                                 │
│  5. Cleanup (optional)                                          │
│     └── Remove report from target host                          │
│                                                                 │
│  6. Set facts                                                   │
│     └── Populate case_updates_needed for upload                 │
└─────────────────────────────────────────────────────────────────┘
```

## License

GPL-3.0-or-later

## Author Information

- **Author:** Lenny Shirley
- **Company:** Red Hat
- **Collection:** [infra.support_assist](https://github.com/redhat-cop/infra.support_assist)
