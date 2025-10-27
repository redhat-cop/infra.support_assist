# infra.support_assist.ocp_must_gather

This role runs `oc adm must-gather` against a target OpenShift cluster, compresses the resulting directory into a `.tar.gz` archive, and prepares it for upload to a Red Hat Support Case.

This role is designed to run on `localhost` (or wherever the `oc` CLI is installed and configured).

## Requirements

* **On Control Node (Execution Host):**
    * The **OpenShift CLI (`oc`)** must be installed and in the system's `PATH`.
    * Must be logged in to the target OpenShift cluster. The role attempts to log in using the provided token.

* **Ansible Collections:**
    * `community.general`: Required for the `community.general.archive` module to compress the must-gather output.

## Role Variables

### Input Variables

The following variables control the behavior of this role:

* `case_id`:
    * **(Required)** The Red Hat Support Case number (e.g., `01234567`).
    * Type: `string`

* `cluster_name`:
    * **(Required)** A short, descriptive name for your cluster (e.g., `my-ocp-cluster`). This is used to name the final archive.
    * Type: `string`

* `ocp_must_gather_token`:
    * **(Required)** The OpenShift API token for logging in (e.g., `sha256~...`).
    * Type: `string`

* `ocp_must_gather_server_url`:
    * **(Required)** The URL of the OpenShift API server (e.g., `https://api.my-ocp-cluster.com:6443`).
    * Type: `string`

* `ocp_must_gather_dest_dir`:
    * A temporary directory on the execution host where `oc adm must-gather` will write its output. This directory is also where the final `.tar.gz` archive will be created.
    * Default: `"/tmp/must-gather-output"`
    * Type: `path`

* `ocp_must_gather_clean`:
    * Whether to remove the temporary `ocp_must_gather_dest_dir` from the execution host after the archive is created.
    * Default: `{{ clean | default(false) | bool }}` (Inherits `clean` var, defaults to `false`)
    * Type: `bool`
    * *Note: This feature is not yet fully implemented in the tasks.*

* `ocp_must_gather_image`:
    * A custom must-gather image to use (e.g., `registry.redhat.io/openshift-service-mesh/servicemesh-must-gather-rhel8:1.2`).
    * Default: `""` (Uses the cluster's default must-gather image)
    * Type: `string`

* `ocp_must_gather_options`:
    * A string of any additional options to pass to the `oc adm must-gather` command (e.g., `-- /usr/bin/gather_metrics`).
    * Default: `""`
    * Type: `string`

### Output Variables

This role generates the following fact, which is used by the `rh_case_update` role:

* `case_updates_needed`:
    * A list containing an object that describes the fetched archive to be uploaded.
    * Example:
        ```yaml
        case_updates_needed:
          - attachment: /tmp/must-gather-output/must-gather-my-ocp-cluster-2025-10-27-150000.tar.gz
            attachmentDescription: "OpenShift must-gather collected from 'my-ocp-cluster' cluster accessed via execution host control-node.example.com using the 'infra.support_assist' collection."
            hostname: "my-ocp-cluster"
        ```

## Dependencies

None.

## Example Playbook

### Simple example (running just the role)

```yaml
- name: Gather OpenShift Must Gather
  hosts: localhost
  connection: local
  gather_facts: false

  vars:
    case_id: "01234567"
    cluster_name: "my-ocp-cluster"
    ocp_must_gather_server_url: "https://api.my-ocp-cluster.com:6443"
    ocp_must_gather_token: "sha256~..."  # Use Ansible Vault!
    ocp_must_gather_options: "-- /usr/bin/gather_network_info"

  tasks:
    - name: Call ocp_must_gather role
      ansible.builtin.include_role:
        name: infra.support_assist.ocp_must_gather
```

### Recommended example (using the main collection playbook)

The recommended way to use this role is via the main `ocp_must_gather` playbook, which handles token refresh and upload logic.

```shell
# Set your Red Hat token as an environment variable
export REDHAT_OFFLINE_TOKEN="YOUR_OFFLINE_TOKEN_HERE"

# Run the main playbook
ansible-playbook infra.support_assist.ocp_must_gather \
  -e case_id=01234567 \
  -e cluster_name=my-ocp-cluster \
  -e ocp_must_gather_server_url="https://api.my-ocp-cluster.com:6443" \
  -e ocp_must_gather_token="sha256~..." \
  -e upload=true
```

## License

GPL-3.0-or-later

## Author Information

- Lenny Shirley