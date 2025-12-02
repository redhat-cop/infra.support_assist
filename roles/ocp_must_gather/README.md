# ocp_must_gather

An Ansible role to gather OpenShift cluster diagnostics using `oc adm must-gather`.

## Description

This role runs **`oc adm must-gather`** against a target OpenShift cluster, compresses the resulting directory into a `.tar.gz` archive, and prepares it for upload to a Red Hat Support Case. It is designed to run on `localhost` (or wherever the `oc` CLI is installed and configured).

### Key Features

- **Automatic version detection** – Works with various OpenShift versions
- **Custom feature collections** – Select specialized component collectors (AAP, ODF, CNV, OSSM, etc.)
- **Time window filtering** – Limit log collection to a specific time range (`--since`)
- **Disconnected environment support** – Works in air-gapped environments with mirror registries
- **Safety checks** – Validates cluster-admin privileges and disk space before execution
- **Cluster name extraction** – Automatically extracts cluster name from API URL for accurate identification

## Requirements

- **On Control Node (Execution Host):**
  - The **OpenShift CLI (`oc`)** must be installed and in the system's `PATH`
  - Network access to the target OpenShift API server
  - Sufficient disk space for the must-gather output (20-30 GiB recommended)

- **Ansible Collections:**
  - `community.general`: Required for the `community.general.archive` module

## Role Variables

### Connection Variables

| Variable | Description | Type | Required | Default |
|----------|-------------|------|----------|---------|
| `ocp_must_gather_server_url` | URL of the OpenShift API server (e.g., `https://api.my-cluster.com:6443`). | `string` | Yes | — |
| `ocp_must_gather_token` | OpenShift API token for authentication (e.g., `sha256~...`). | `string` | Yes | — |
| `ocp_must_gather_validate_ssl` | Whether to validate SSL/TLS certificates during `oc login`. | `bool` | No | `true` |

### Must-Gather Execution Variables

| Variable | Description | Type | Required | Default |
|----------|-------------|------|----------|---------|
| `ocp_must_gather_dest_dir` | Temporary directory for must-gather output and archive. | `path` | No | `/tmp/must-gather-output` |
| `ocp_must_gather_image` | Acronym for the component collection profile to run. | `string` | No | `DEFAULT` |
| `ocp_must_gather_since` | Limits log collection to a time window (e.g., `6h`, `7d`). | `string` | No | `""` (full history) |
| `ocp_must_gather_options` | Additional options for the `oc adm must-gather` command. | `string` | No | `""` |

### Disconnected Environment Variables

| Variable | Description | Type | Required | Default |
|----------|-------------|------|----------|---------|
| `ocp_disconnected_mode` | Enable disconnected/air-gapped environment mode. | `bool` | No | `false` |
| `ocp_disconnected_registry` | Mirror registry address (e.g., `myregistry.local/ocp/mirror`). Required if `ocp_disconnected_mode` is `true`. | `string` | Conditional | `""` |

### Case Variables

| Variable | Description | Type | Required | Default |
|----------|-------------|------|----------|---------|
| `case_id` | Red Hat Support Case number (e.g., `01234567`). Only needed for automatic upload. | `string` | No | — |

### Output Variables

| Variable | Description | Type |
|----------|-------------|------|
| `case_updates_needed` | List containing the generated archive path and description for upload by `rh_case`. | `list` |

## Component Collection Options

The `ocp_must_gather_image` variable accepts acronyms for specialized collections:

| Acronym | Component | Description |
|---------|-----------|-------------|
| `DEFAULT` | Core OpenShift | Standard must-gather collection |
| `AAP` | Ansible Automation Platform | AAP-specific diagnostics |
| `ODF` | OpenShift Data Foundation | Storage-related diagnostics |
| `CNV` | Container Native Virtualization | Virtualization diagnostics |
| `OSSM` | OpenShift Service Mesh | Service mesh diagnostics |

> **Full list of options:** [docs/MUST_GATHER_IMAGE_OPTIONS.md](docs/MUST_GATHER_IMAGE_OPTIONS.md)

## Time Window Options

The `ocp_must_gather_since` variable accepts:

- `1h`, `3h`, `6h`, `12h`, `24h` – Hours
- `3d`, `7d`, `14d`, `30d` – Days
- `""` (empty) – Full history

## Dependencies

- `community.general`: Required for the `archive` module

## Safety Checks

The role includes built-in safety checks:

1. **Privilege Pre-Check** – Verifies the authenticated user/Service Account has `cluster-admin` privileges before executing the long-running must-gather command
2. **Disk Space Check** – Validates available disk space on the execution host filesystem to prevent mid-execution failures

## Example Playbooks

### Example 1: Basic Must-Gather

```yaml
---
- name: Gather OpenShift Must-Gather
  hosts: localhost
  connection: local
  gather_facts: false

  vars:
    ocp_must_gather_server_url: "https://api.my-ocp-cluster.com:6443"
    ocp_must_gather_token: "sha256~..."  # Use Ansible Vault!

  tasks:
    - name: Run must-gather
      ansible.builtin.include_role:
        name: infra.support_assist.ocp_must_gather
```

### Example 2: AAP Collection with Time Window

```yaml
---
- name: Gather AAP-specific diagnostics
  hosts: localhost
  connection: local
  gather_facts: false

  vars:
    ocp_must_gather_server_url: "https://api.my-ocp-cluster.com:6443"
    ocp_must_gather_token: "{{ vault_ocp_token }}"
    ocp_must_gather_image: "AAP"
    ocp_must_gather_since: "6h"

  tasks:
    - name: Run AAP must-gather
      ansible.builtin.include_role:
        name: infra.support_assist.ocp_must_gather
```

### Example 3: Disconnected Environment

```yaml
---
- name: Gather from disconnected cluster
  hosts: localhost
  connection: local
  gather_facts: false

  vars:
    ocp_must_gather_server_url: "https://api.my-ocp-cluster.com:6443"
    ocp_must_gather_token: "{{ vault_ocp_token }}"
    ocp_disconnected_mode: true
    ocp_disconnected_registry: "registry.local/must-gather-mirror"
    ocp_must_gather_validate_ssl: false

  tasks:
    - name: Run must-gather in disconnected mode
      ansible.builtin.include_role:
        name: infra.support_assist.ocp_must_gather
```

### Using the Collection Playbook (Recommended)

The recommended way to use this role is via the main playbook, which handles token refresh and upload logic:

```shell
# Set your Red Hat token as an environment variable
export REDHAT_OFFLINE_TOKEN="YOUR_OFFLINE_TOKEN_HERE"

# Run the full pipeline
ansible-playbook infra.support_assist.ocp_must_gather \
  -e case_id=00000000 \
  -e ocp_must_gather_server_url="https://api.my-ocp-cluster.com:6443" \
  -e ocp_must_gather_token="sha256~..." \
  -e ocp_must_gather_image="AAP" \
  -e ocp_must_gather_since="6h" \
  -e upload=true
```

See the example playbook: [`playbooks/ocp-case-mustgather-pipeline.yml`](../../playbooks/ocp-case-mustgather-pipeline.yml)

## Customizing the Case Comment Template

The content of the automatic comment posted after must-gather upload can be customized via the Jinja2 template:

**[`templates/support_case_comment.j2`](templates/support_case_comment.j2)**

## Disconnected Environment Reference

For more information on running must-gather in disconnected environments, see:

- [Red Hat KCS: How to run must-gather in a disconnected environment](https://access.redhat.com/solutions/4647561)

## License

GPL-3.0-or-later

## Author Information

- **Authors:** Lenny Shirley, Diego Felipe Mateus
- **Company:** Red Hat
- **Collection:** [infra.support_assist](https://github.com/redhat-cop/infra.support_assist)
