# sos_report

An Ansible role to gather SOS reports from managed hosts and OCP/RHCOS nodes for Red Hat Support Cases.

## Description

This role generates an `sosreport` on one or more target hosts, fetches the resulting archives to the control node, and prepares them for upload to a Red Hat Support Case. The SOS report contains system configuration and diagnostic information commonly requested by Red Hat support engineers.

### Key Features

- **Multi-host / multi-node collection** – Gather reports from multiple RHEL hosts or OCP nodes in a single run; each report is stored in its own subdirectory and tracked for upload
- **OCP/RHCOS node support** – Collect SOS reports from OpenShift CoreOS nodes via SSH (`ocp_ssh`) or `oc debug` (`ocp_debug`) without requiring SSH access
- **Flexible node targeting** – Provide an explicit node list, use Kubernetes label selectors (e.g., `node-role.kubernetes.io/worker=`), or auto-discover all cluster nodes
- **Automatic package installation** – Installs the `sos` package if not present (standard mode)
- **AAP containerized support** – Special handling for AAP containerized environments
- **Cleanup options** – Optionally remove reports from target hosts/nodes after fetching
- **Case-organized storage** – Reports are organized by case ID and hostname/node name
- **Pipeline-ready** – Populates `case_updates_needed` with all collected reports for seamless upload via `rh_case`

### Collection Modes

The role supports three collection modes via the `sos_report_mode` variable:

| Mode | Description | Target | Use When |
|------|-------------|--------|----------|
| `standard` | Direct `sos report` on RHEL hosts (default) | Inventory hosts | Standard RHEL/Fedora/CentOS systems |
| `ocp_ssh` | SSH to RHCOS nodes, run via support-tools container | Inventory hosts (OCP nodes) | SSH access to OCP nodes is available |
| `ocp_debug` | `oc debug node/` from execution host | localhost → OCP API | No SSH access; only API/oc access |

> **Important:** SOS Reports from OCP/RHCOS nodes are different from standard Linux hosts.
> OCP modes use the `registry.redhat.io/rhel9/support-tools` container image and enable
> OpenShift-specific plugins (`openshift`, `openshift_ovn`, `openvswitch`, `podman`, `crio`).

**Reference KCS Articles:**
- [Method 1 - SSH: Generate a sos report in RHCOS with SSH access](https://access.redhat.com/solutions/3820762)
- [Method 2 - oc debug: Generate a sos report in RHCOS with oc debug node](https://access.redhat.com/solutions/5065411)

## Requirements

- **Standard Mode - On Target Hosts:**
  - The `sos` package (will be installed automatically by the role)
  - Root or sudo privileges for running `sos report`

- **OCP SSH Mode - On Target Hosts (OCP Nodes):**
  - SSH access to RHCOS nodes (using the SSH key from `install-config.yaml`)
  - `ansible_user: core` in inventory
  - Root or sudo privileges (for running `podman` with privileged containers)
  - Access to `registry.redhat.io/rhel9/support-tools` image (or mirror for disconnected environments)

- **OCP Debug Mode - On Execution Host:**
  - `oc` CLI installed and in PATH
  - Valid OpenShift API token with permissions to run `oc debug node/`
  - Access to `registry.redhat.io/rhel9/support-tools` image from the cluster nodes

## Role Variables

### Common Variables (All Modes)

| Variable | Description | Type | Required | Default |
|----------|-------------|------|----------|---------|
| `case_id` | Red Hat Support Case number (e.g., `01234567`). Used for naming and organization. | `string` | Yes | — |
| `sos_report_dest` | Base directory on the control node where fetched reports are stored. | `path` | No | `/tmp/sos_reports` |
| `sos_report_cleanup` | Remove the generated sosreport from target hosts after fetching. | `bool` | No | `true` (via `clean` variable) |
| `sos_report_mode` | Collection mode: `standard`, `ocp_ssh`, or `ocp_debug`. | `string` | No | `standard` |

### Standard Mode Variables

| Variable | Description | Type | Required | Default |
|----------|-------------|------|----------|---------|
| `sos_report_aap_containerized` | Enable AAP containerized-specific options for the SOS report. | `bool` | No | `false` (via `containerized` variable) |

### OCP Variables (Both OCP Modes)

| Variable | Description | Type | Required | Default |
|----------|-------------|------|----------|---------|
| `sos_report_ocp_support_tools_image` | Support-tools container image. Override for disconnected environments. | `string` | No | `registry.redhat.io/rhel9/support-tools` |
| `sos_report_ocp_authfile` | Path to container registry auth file on the RHCOS node for pulling the image. | `string` | No | `/var/lib/kubelet/config.json` |
| `sos_report_ocp_all_logs` | Include `--all-logs` flag. Set to `false` if reports become too large. | `bool` | No | `true` |
| `sos_report_ocp_plugin_timeout` | Plugin timeout in seconds. | `int` | No | `600` |

### OCP Debug Mode Variables

| Variable | Description | Type | Required | Default |
|----------|-------------|------|----------|---------|
| `sos_report_ocp_token` | OpenShift API token. Falls back to `ocp_must_gather_token`. | `string` | Yes (debug mode) | — |
| `sos_report_ocp_server_url` | OpenShift API server URL. Falls back to `ocp_must_gather_server_url`. | `string` | Yes (debug mode) | — |
| `sos_report_ocp_validate_ssl` | Validate SSL certificates for OpenShift connection. | `bool` | No | `true` |
| `sos_report_ocp_nodes` | List of specific node names to collect from. Takes priority over `sos_report_ocp_node_selector`. | `list` | No | `[]` |
| `sos_report_ocp_node_selector` | Kubernetes label selector to filter nodes during auto-discovery. Used when `sos_report_ocp_nodes` is empty. | `string` | No | `""` |

> **Tip:** If you are already using the `ocp_must_gather` role in the same playbook,
> the `sos_report_ocp_token` and `sos_report_ocp_server_url` variables will automatically
> fall back to `ocp_must_gather_token` and `ocp_must_gather_server_url` respectively.

#### Node Selection Priority

The role determines which nodes to collect SOS reports from using this priority:

1. **Explicit list** (`sos_report_ocp_nodes`) — If provided, only these exact nodes are targeted. Each node name is validated against the cluster before collection.
2. **Label selector** (`sos_report_ocp_node_selector`) — If `sos_report_ocp_nodes` is empty and a selector is set, nodes matching the label are discovered via `oc get nodes -l <selector>`.
3. **All nodes** — If both are empty, all nodes in the cluster are discovered via `oc get nodes`.

Common label selectors:

| Selector | Description |
|----------|-------------|
| `node-role.kubernetes.io/worker=` | Only worker nodes |
| `node-role.kubernetes.io/master=` | Only master/control-plane nodes |
| `node-role.kubernetes.io/infra=` | Only infrastructure nodes |
| `kubernetes.io/os=linux` | All Linux nodes |
| `topology.kubernetes.io/zone=us-east-1a` | Nodes in a specific availability zone |
| `node-role.kubernetes.io/worker=,topology.kubernetes.io/zone=us-east-1a` | Workers in a specific zone |

### Output Variables

| Variable | Description | Type |
|----------|-------------|------|
| `case_updates_needed` | List of objects describing the fetched files for upload by `rh_case`. | `list` |

### Output Directory Structure

Reports are organized on the control node as:

```text
{{ sos_report_dest }}/
├── {{ hostname_1 }}/
│   └── sosreport-hostname1-20251027150000.tar.xz
├── {{ hostname_2 }}/
│   └── sosreport-hostname2-20251027150100.tar.xz
├── {{ ocp_worker_0 }}/
│   └── sosreport-worker-0-20251027150200.tar.xz
└── {{ ocp_master_0 }}/
    └── sosreport-master-0-20251027150300.tar.xz
```

## Dependencies

None.

## Example Playbooks

### Example 1: Basic SOS Report Collection (Standard RHEL)

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

### Example 2: OCP Nodes via SSH (Method 1)

Requires OCP nodes in inventory with SSH access configured.

**Inventory example:**

```ini
[ocp_nodes]
worker-0.ocp.example.com ansible_user=core ansible_ssh_private_key_file=~/.ssh/ocp-key
worker-1.ocp.example.com ansible_user=core ansible_ssh_private_key_file=~/.ssh/ocp-key
master-0.ocp.example.com ansible_user=core ansible_ssh_private_key_file=~/.ssh/ocp-key
```

**Playbook:**

```yaml
---
- name: Gather SOS Reports from OCP nodes via SSH
  hosts: ocp_nodes
  gather_facts: false

  vars:
    case_id: "01234567"
    sos_report_mode: "ocp_ssh"

  tasks:
    - name: Gather OCP node SOS report via SSH
      ansible.builtin.include_role:
        name: infra.support_assist.sos_report
```

**CLI:**

```shell
ansible-playbook -i inventory playbook.yml \
  -e case_id=01234567 \
  -e sos_report_mode=ocp_ssh
```

### Example 3: OCP Nodes via oc debug (Method 2)

Runs from localhost using the `oc` CLI. No SSH access to nodes required.

```yaml
---
- name: Gather SOS Reports from OCP nodes via oc debug
  hosts: localhost
  connection: local
  gather_facts: false

  vars:
    case_id: "01234567"
    sos_report_mode: "ocp_debug"
    sos_report_ocp_token: "sha256~xxxxx"
    sos_report_ocp_server_url: "https://api.ocp.example.com:6443"

  tasks:
    - name: Gather OCP node SOS report via oc debug
      ansible.builtin.include_role:
        name: infra.support_assist.sos_report
```

**CLI (auto-discover all nodes):**

```shell
ansible-playbook -i localhost, playbook.yml \
  -e case_id=01234567 \
  -e sos_report_mode=ocp_debug \
  -e sos_report_ocp_token="sha256~xxxxx" \
  -e sos_report_ocp_server_url="https://api.ocp.example.com:6443"
```

**CLI (specific nodes by name):**

```shell
ansible-playbook -i localhost, playbook.yml \
  -e case_id=01234567 \
  -e sos_report_mode=ocp_debug \
  -e sos_report_ocp_token="sha256~xxxxx" \
  -e sos_report_ocp_server_url="https://api.ocp.example.com:6443" \
  -e '{"sos_report_ocp_nodes": ["worker-0.ocp.example.com", "worker-1.ocp.example.com"]}'
```

**CLI (only worker nodes via label selector):**

```shell
ansible-playbook -i localhost, playbook.yml \
  -e case_id=01234567 \
  -e sos_report_mode=ocp_debug \
  -e sos_report_ocp_token="sha256~xxxxx" \
  -e sos_report_ocp_server_url="https://api.ocp.example.com:6443" \
  -e sos_report_ocp_node_selector="node-role.kubernetes.io/worker="
```

**CLI (only master/control-plane nodes):**

```shell
ansible-playbook -i localhost, playbook.yml \
  -e case_id=01234567 \
  -e sos_report_mode=ocp_debug \
  -e sos_report_ocp_token="sha256~xxxxx" \
  -e sos_report_ocp_server_url="https://api.ocp.example.com:6443" \
  -e sos_report_ocp_node_selector="node-role.kubernetes.io/master="
```

### Example 4: OCP Nodes via oc debug (Reusing ocp_must_gather variables)

If you are running both `ocp_must_gather` and `sos_report` in the same playbook, the OCP connection variables are shared automatically.

```yaml
---
- name: Full OCP Diagnostics Pipeline
  hosts: localhost
  connection: local
  gather_facts: false

  vars:
    case_id: "01234567"
    ocp_must_gather_token: "sha256~xxxxx"
    ocp_must_gather_server_url: "https://api.ocp.example.com:6443"

  tasks:
    - name: Run must-gather
      ansible.builtin.include_role:
        name: infra.support_assist.ocp_must_gather

    - name: Gather node SOS reports via oc debug
      ansible.builtin.include_role:
        name: infra.support_assist.sos_report
      vars:
        sos_report_mode: "ocp_debug"
```

### Example 5: Disconnected/Air-Gapped OCP Environment

```yaml
---
- name: Gather SOS Reports from disconnected OCP cluster
  hosts: ocp_nodes
  gather_facts: false

  vars:
    case_id: "01234567"
    sos_report_mode: "ocp_ssh"
    sos_report_ocp_support_tools_image: "mirror-registry.example.com:5000/rhel9/support-tools"

  tasks:
    - name: Gather OCP node SOS report from disconnected cluster
      ansible.builtin.include_role:
        name: infra.support_assist.sos_report
```

### AAP Containerized Environment (Standard Mode)

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

The recommended way to use this role is via the mode-specific playbooks, which handle token refresh and upload logic:

```shell
# Set your Red Hat token as an environment variable
export REDHAT_OFFLINE_TOKEN="YOUR_OFFLINE_TOKEN_HERE"

# RHEL hosts (standard mode)
ansible-playbook -i inventory infra.support_assist.sos_report_rhel \
  -e case_id=01234567 \
  -e upload=true \
  -e clean=true

# OCP nodes via oc debug
ansible-playbook infra.support_assist.sos_report_ocp \
  -e sos_report_ocp_token_file=/path/to/kubeconfig \
  -e case_id=01234567 \
  -e upload=true
```

> **Deprecated:** `infra.support_assist.sos_report` is kept as a backward-compatible alias for this release. Update job templates and automation to use `sos_report_rhel` or `sos_report_ocp` before the next major version.

## How It Works

### Standard Mode

```text
┌─────────────────────────────────────────────────────────────────┐
│                    sos_report (standard)                         │
├─────────────────────────────────────────────────────────────────┤
│  1. Install (if needed)                                         │
│     └── Ensure sos package is installed                         │
│                                                                 │
│  2. Generate                                                    │
│     └── Run sos report --batch with options                     │
│                                                                 │
│  3. Fetch                                                       │
│     └── Copy report to control node organized by host           │
│                                                                 │
│  4. Cleanup (optional)                                          │
│     └── Remove report from target host                          │
│                                                                 │
│  5. Set facts                                                   │
│     └── Populate case_updates_needed for upload                 │
└─────────────────────────────────────────────────────────────────┘
```

### OCP SSH Mode

```text
┌─────────────────────────────────────────────────────────────────┐
│                    sos_report (ocp_ssh)                          │
├─────────────────────────────────────────────────────────────────┤
│  1. Assert OCP prerequisites                                    │
│     └── Validate support-tools image is configured               │
│                                                                 │
│  2. Generate via support-tools container                         │
│     └── podman run ... support-tools sos report --batch         │
│         with OCP plugins (-e openshift, crio, podman, etc.)     │
│                                                                 │
│  3. Fetch                                                       │
│     └── Copy report to control node (from /var/tmp/)            │
│                                                                 │
│  4. Cleanup (optional)                                          │
│     └── Remove report from target node                          │
│                                                                 │
│  5. Set facts                                                   │
│     └── Populate case_updates_needed for upload                 │
└─────────────────────────────────────────────────────────────────┘
```

### OCP Debug Mode

```text
┌─────────────────────────────────────────────────────────────────┐
│                    sos_report (ocp_debug)                        │
├─────────────────────────────────────────────────────────────────┤
│  1. Assert OCP prerequisites                                    │
│     └── Validate oc CLI, API token, server URL                   │
│                                                                 │
│  2. Login to OpenShift cluster                                   │
│     └── oc login --token=... --server=...                        │
│                                                                 │
│  3. Discover or validate node list                               │
│     └── oc get nodes (auto) or validate user-provided list       │
│                                                                 │
│  4. Per-node collection (loop):                                  │
│     ├── Generate: oc debug node/<name> -- chroot /host           │
│     │             podman run ... support-tools sos report ...     │
│     ├── Find: oc debug node/<name> -- ls /host/var/tmp/...       │
│     ├── Fetch: oc debug node/<name> -- cat ... > local_path      │
│     └── Cleanup: oc debug node/<name> -- rm ... (optional)       │
│                                                                 │
│  5. Set facts                                                   │
│     └── Populate case_updates_needed for upload                 │
└─────────────────────────────────────────────────────────────────┘
```

## Security Considerations

### SSH Fallback (ocp_debug mode)

The SSH fallback path in `ocp_debug` mode (`sos_report_ocp_fallback_ssh: true`) connects
from the control node directly to RHCOS node internal IPs using `StrictHostKeyChecking=no`
and `UserKnownHostsFile=/dev/null`. This disables host key verification.

**Risk:** An attacker with network access between the control node and the OCP nodes could
perform a man-in-the-middle attack during the SSH connection. The SOS report (which may
contain sensitive cluster configuration, logs, and credentials) could be intercepted.

**Mitigations in common deployments:**

- OCP node internal IPs are typically reachable only from within the cluster's private
  network (VPN, VNET peering, or a dedicated management network). MITM attacks require
  an attacker already inside that network boundary.
- In AAP environments, the Execution Environment connects through a bastion/jump host
  (configured via `sos_report_ocp_ssh_extra_args`), which adds another trust boundary.

**For regulated or high-security environments:**

- Use `ocp_debug` mode without SSH fallback (`sos_report_ocp_fallback_ssh: false`,
  the default) — no SSH connection is made.
- If SSH fallback is required, ensure the control node and OCP nodes share a private,
  monitored network segment and rely on VPN or private peering rather than public IPs.
- Consider setting `sos_report_ocp_ssh_extra_args` to enforce a specific known-hosts
  file or certificate-based verification if your RHCOS provisioning populates node
  host keys into a trusted store.

## License

GPL-3.0-or-later

## Author Information

- **Author:** Lenny Shirley
- **Company:** Red Hat
- **Collection:** [infra.support_assist](https://github.com/redhat-cop/infra.support_assist)

## Related Roles

This role is typically used in conjunction with other roles in the `infra.support_assist` collection:

- `ocp_must_gather` – Collect must-gather data from OpenShift clusters
- `rh_case` – Create and update Red Hat support cases (unified role)
- `rh_token_refresh` – Handle Red Hat API token authentication and caching
