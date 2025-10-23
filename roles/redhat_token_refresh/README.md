infra.support_assist.redhat_token_refresh
=========

The `infra.support_assist.redhat_token_refresh` Ansible role is designed to **retrieve an access token for the Red Hat API using an offline token**. This token is then cached locally to manage its lifecycle and avoid unnecessary API calls.

Requirements
------------

The sources do not explicitly list any pre-requisites that may not be covered by Ansible itself. This means that no specific Python packages (like `boto` for EC2 modules) or other external software are explicitly required beyond a standard Ansible installation.

Role Variables
--------------

The behavior of the `redhat_token_refresh` role is controlled by the following variables, which can be set in your playbook, inventory, or `vars` files:

*   **`redhat_token_refresh_api_offline_token`**
    *   **(Required)** A string representing your **Red Hat offline token**. This token is used by the role to acquire the necessary access token for the Red Hat API. It is crucial for authentication. This variable does not have a default value and must be provided.

*   **`redhat_token_refresh_token_cache_file`**
    *   **(Optional)** The **full path to a file** where the obtained access token and its timestamp will be cached locally.
    *   **Default:** `"/tmp/ansible_refresh_token.json"`

*   **`redhat_token_refresh_token_max_age_seconds`**
    *   **(Optional)** An integer defining the **maximum age (in seconds)** of a cached access token before it is considered invalid and a new one needs to be retrieved.
    *   **Default:** `900` (which is 15 minutes * 60 seconds)

*   **`redhat_token_refresh_api_base_url`**
    *   **(Optional)** The **base URL for the Red Hat API**. This variable is used internally, although not directly in the token retrieval task shown, it provides a consistent base.
    *   **Default:** `"https://api.access.redhat.com"`

*   **`redhat_token_refresh_api_token_url`**
    *   **(Optional)** The **full URL for the Red Hat SSO token endpoint**. This is where the role sends the POST request to exchange the offline token for an access token.
    *   **Default:** `"https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token"`

Output Variables
----------------

This role sets the following fact, which can be used by subsequent tasks or roles in your playbook:

*   **`redhat_token_refresh_api_access_token`**
    *   This variable will contain the **valid Red Hat API access token** after the role has successfully run. This token is either retrieved from the local cache or newly obtained from the Red Hat SSO service.

Example Playbook
----------------

Here's an example of how to use the `infra.support_assist.redhat_token_refresh` role in your Ansible playbook:

```yaml
- name: Get Red Hat API Access Token
  hosts: localhost # This role typically runs on the control node
  connection: local # If running on the control node
  gather_facts: false # Not strictly required for this role

  tasks:
    - name: Retrieve Red Hat API access token
      ansible.builtin.import_role:
        name: infra.support_assist.redhat_token_refresh
      vars:
        # It's highly recommended to manage this with Ansible Vault
        # For example: redhat_token_refresh_api_offline_token: "{{ vault_redhat_offline_token }}"
        redhat_token_refresh_api_offline_token: "YOUR_REDHAT_OFFLINE_TOKEN_HERE"

        # Optional: Customize cache file location or token validity
        # redhat_token_refresh_token_cache_file: "/home/ansible_user/.redhat_api_token.json"
        # redhat_token_refresh_token_max_age_seconds: 3600 # Cache for 1 hour

    - name: Use the retrieved access token in a subsequent task
      ansible.builtin.uri:
        url: "https://api.access.redhat.com/path/to/some/redhat/api"
        headers:
          Authorization: "Bearer {{ redhat_token_refresh_api_access_token }}"
        method: GET
        status_code: 200
      delegate_to: localhost
      run_once: true
```

## License

This role is licensed under **GPL-2.0-or-later**.

## Author Information

*   Lenny Shirley