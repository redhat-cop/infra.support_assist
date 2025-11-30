infra.support_assist.openshift_must_gather
==========================================

This role executes oc adm must-gather against a target OpenShift cluster and retrieves the diagnostic archive to the Ansible control node.

Requirements
------------

oc CLI: The oc command-line tool must be installed on the host where this role executes (typically the Ansible control node or a designated bastion host).

OpenShift Authentication: The oc CLI must be logged into the target OpenShift cluster before running this role. Authentication is typically handled via the KUBECONFIG environment variable or the default ~/.kube/config file. This role does not handle oc login.

Execution Context
-----------------

This role is designed to run on a host that has access to the target OpenShift cluster's API, usually localhost (the Ansible control node) using delegate_to: localhost.

Role Variables
--------------

case_id: (Required) The Red Hat Support Case number. Used for organizing fetched files.

openshift_must_gather_dest_dir: (Optional) A temporary directory on the execution host (where oc runs) to store the must-gather output before archiving and fetching.

Default: /tmp/must-gather-output

openshift_must_gather_image: (Optional) Specify a custom container image for oc adm must-gather.

Default: Not set (uses OpenShift's default image).

openshift_must_gather_options: (Optional) A string containing any additional command-line options to pass directly to oc adm must-gather (e.g., -- /usr/bin/gather_audit_logs).

Default: ""

openshift_must_gather_clean: (Optional) Set to true to remove the temporary openshift_must_gather_dest_dir from the execution host after fetching the archive. Inherits the global clean variable by default.

Default: {{ clean | default(false) | bool }}

sos_report_dest: (Required, inherited) The base directory on the Ansible control node where the final fetched archive will be placed (under case_{{ case_id }}/{{ inventory_hostname }}-must_gather/). This variable is typically set globally or by the calling playbook and reused from the sos_report role's defaults.

Default (from sos_report role): /tmp/sos_reports

Dependencies
------------

None.

Example Playbook
----------------

```yaml
- name: Gather OpenShift Must Gather
  # Run this play against a host that has oc CLI and is logged in
  hosts: localhost
  connection: local
  gather_facts: false

  vars:
    case_id: "04288106"
    # sos_report_dest: "/tmp/my_support_files" # Optional override
    # openshift_must_gather_image: "[registry.example.com/my-must-gather:latest](https://registry.example.com/my-must-gather:latest)" # Optional custom image
    # openshift_must_gather_options: "-- /usr/bin/gather_network_info" # Optional extra args
    clean: true # Set to true to clean up temp dir on execution host

  tasks:
    - name: Include the openshift_must_gather role
      ansible.builtin.include_role:
        name: infra.support_assist.openshift_must_gather
      # Use delegate_to if running the play against a different host group
      # delegate_to: localhost

# --- Subsequent Play to Upload ---
# This assumes the 'case_updates_needed' fact was populated by the role above
- name: Upload Files to Red Hat Support Case Portal
  hosts: localhost
  connection: local
  gather_facts: false
  # vars: # Ensure api token and case_id are available
  tasks:
    - name: Aggregate 'case_updates_needed' data from all sources (if needed)
      ansible.builtin.set_fact:
        case_updates_needed: |
          {% set combined_list = [] %}
          {% for host in groups['all'] %} # Or specific group must-gather ran against
          {%   if hostvars[host].case_updates_needed is defined %}
          {%     set _ = combined_list.extend(hostvars[host].case_updates_needed) %}
          {%   endif %}
          {% endfor %}
          {{ combined_list }}
      run_once: true # Aggregation only needed once

    # Include token refresh and case update roles here...
    - name: Include rh_token_refresh role...
    - name: Include rh_case_update role...
```

OutputThe role fetches a compressed archive (.tar.gz) of the must-gather output to the control node under:{{ sos_report_dest }}/case_{{ case_id }}/{{ inventory_hostname }}-must_gather/must-gather.local.<timestamp>.tar.gzIt also populates the case_updates_needed fact with the path to this archive for use with the rh_case_update role.LicenseGPL-3.0-or-laterAuthor InformationLenny Shirley