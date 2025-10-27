# infra.support_assist.sos_report

This role generates an `sosreport` on one or more target hosts, fetches it to the control node, and prepares it for upload to a Red Hat Support Case.

## Requirements

* **On Target Hosts:**
    * The `sos` package is required. This role will attempt to install it using the `ansible.builtin.package` module.

## Role Variables

### Input Variables

The following variables control the behavior of this role:

* `case_id`:
    * **(Required)** The Red Hat Support Case number (e.g., `01234567`). This is used to name the `sosreport` and for validation.
    * Type: `string`

* `sos_report_cleanup`:
    * Whether to remove the generated `sosreport` from the target host after fetching it.
    * Default: `{{ clean | default(false) | bool }}` (Inherits `clean` var, defaults to `false`)
    * Type: `bool`

* `sos_report_dest`:
    * The base directory on the Ansible control node where fetched reports will be stored. The role will create a subdirectory structure: `{{ sos_report_dest }}/case_{{ case_id }}/{{ inventory_hostname | lower | regex_replace('[^a-zA-Z0-9_-]', '-') }}/`
    * Default: `"/tmp/sos_reports"`
    * Type: `path`

* `sos_report_aap_containerized`:
    * Passes container-specific options to the `sos report` command (e.g., `-k aap_containerized.username={{ ansible_user_id }}`).
    * Default: `{{ containerized | default(false) | bool }}` (Inherits `containerized` var, defaults to `false`)
    * Type: `bool`

### Output Variables

This role generates the following fact, which is used by the `rh_case_update` role:

* `case_updates_needed`:
    * A list containing an object that describes the fetched file to be uploaded.
    * Example:
        ```yaml
        case_updates_needed:
          - attachment: /tmp/sos_reports/case_01234567/my-server.example.com/sosreport-my-server-01234567-20251027150000.tar.xz
            attachmentDescription: "Gathered from 'my-server.example.com' using the 'infra.support_assist' Ansible Collection. Inventory Hostname: 'my-server'"
        ```

## Dependencies

None.

## Example Playbook

### Simple example (running just the role)

```yaml
- name: Gather SOS Report
  hosts: all
  gather_facts: false
  vars:
    case_id: "01234567"
    sos_report_cleanup: true

  tasks:
    - name: Call sos_report role
      ansible.builtin.include_role:
        name: infra.support_assist.sos_report
```

### Recommended example (using the main collection playbook)

The recommended way to use this role is via the main playbook, which handles token refresh and upload logic.

```shell
# Set your token as an environment variable
export REDHAT_OFFLINE_TOKEN="YOUR_OFFLINE_TOKEN_HERE"

# Run the main playbook
ansible-playbook -i inventory infra.support_assist.sos_report \
  -e case_id=01234567 \
  -e upload=true \
  -e clean=true
```

## License

GPL-3.0-or-later

## Author Information

- Lenny Shirley
