# infra.support_assist.rh_case_update

This role updates a Red Hat Support Case by uploading attachments or adding comments. It is designed to run on `localhost` and iterates over a list of updates defined in the `case_updates_needed` variable.

This role uses `curl` via `ansible.builtin.shell` for file uploads to ensure support for large files and streaming.

## Requirements

* **On Control Node:**
    * `curl`: The `curl` command-line utility must be installed and in the system's `PATH`.

## Role Variables

### Input Variables

* `case_id`:
    * **(Required)** The Red Hat Support Case number (e.g., `01234567`).
    * Type: `string`

* `rh_token_refresh_api_access_token`:
    * **(Required)** A valid Red Hat API access token. This is typically provided by running the `infra.support_assist.rh_token_refresh` role first.
    * Type: `string`

* `rh_case_update_timeout`:
    * The timeout in seconds for each `curl` file upload command.
    * Default: `{{ upload_timeout | default(1800) }}` (Inherits `upload_timeout` var, defaults to 1800 seconds / 30 minutes)
    * Type: `int`

* `case_updates_needed`:
    * **(Required)** A list of objects, where each object defines either an attachment to upload or a comment to add.
    * Type: `list`
    * **Object Structure:**
        * `attachment`: (Optional) The full path to the local file to be uploaded.
        * `attachmentDescription`: (Optional) A description for the file being attached.
        * `comment`: (Optional) The text of the comment to add to the case.
        * `commentType`: (Optional) The format of the comment. Can be `markdown` (default) or `plaintext`.

## Dependencies

* This role **must** be run after `infra.support_assist.rh_token_refresh` to populate the required `rh_token_refresh_api_access_token` fact.

## Example Playbook

### Example 1: Add a comment

```yaml
- name: Add comment to Red Hat Case
  hosts: localhost
  connection: local
  gather_facts: false

  vars:
    case_id: "01234567"
    offline_token: "YOUR_OFFLINE_TOKEN_HERE" # Used by rh_token_refresh
    case_updates_needed:
      - comment: "This is a test comment added via Ansible."
        commentType: "plaintext"

  tasks:
    - name: Call rh_token_refresh role
      ansible.builtin.include_role:
        name: infra.support_assist.rh_token_refresh

    - name: Call rh_case_update role
      ansible.builtin.include_role:
        name: infra.support_assist.rh_case_update
```

### Example 2: Upload a local file

```yaml
- name: Upload file to Red Hat Case
  hosts: localhost
  connection: local
  gather_facts: false

  vars:
    case_id: "01234567"
    offline_token: "YOUR_OFFLINE_TOKEN_HERE"
    case_updates_needed:
      - attachment: "/var/log/my-custom-app.log"
        attachmentDescription: "Custom log file from my-server-01"

  tasks:
    - name: Call rh_token_refresh role
      ansible.builtin.include_role:
        name: infra.support_assist.rh_token_refresh

    - name: Call rh_case_update role
      ansible.builtin.include_role:
        name: infra.support_assist.rh_case_update
```

### Example 3: Upload multiple files and add a comment

```yaml
- name: Perform multiple case updates
  hosts: localhost
  connection: local
  gather_facts: false

  vars:
    case_id: "01234567"
    offline_token: "YOUR_OFFLINE_TOKEN_HERE"
    case_updates_needed:
      - attachment: "/tmp/sos_reports/case_01234567/server1/sosreport-server1.tar.xz"
        attachmentDescription: "SOS Report from server1"
      - attachment: "/tmp/sos_reports/case_01234567/server2/sosreport-server2.tar.xz"
        attachmentDescription: "SOS Report from server2"
      - comment: |
          ### Automation Complete
          Attached are the `sosreport` files from `server1` and `server2`.
          
          * `server1.example.com`
          * `server2.example.com`
        commentType: "markdown"

  tasks:
    - name: Call rh_token_refresh role
      ansible.builtin.include_role:
        name: infra.support_assist.rh_token_refresh

    - name: Call rh_case_update role
      ansible.builtin.include_role:
        name: infra.support_assist.rh_case_update
```

## License

GPL-3.0-or-later

## Author Information

- Lenny Shirley
