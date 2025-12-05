# API Endpoints Requiring Dynamic IDs

This document lists AAP API endpoints that were requested in support cases but require dynamic IDs (object IDs, job IDs, etc.) to be queried. These endpoints cannot be automatically added to the `aap_api_gather` role without additional logic to discover and iterate over the required IDs.

## Controller Endpoints

### Instance Endpoints
- `/api/controller/v2/instances/<ID>/health_check`
- `/api/controller/v2/instances/<ID>/install_bundle`
- `/api/controller/v2/instances/<ID>/instance_groups`
- `/api/controller/v2/instances/<ID>/jobs`
- `/api/controller/v2/instances/<ID>/peers`
- `/api/controller/v2/instances/<ID>/receptor_addresses`
- `/api/v2/instances/<ID>/instance_groups`
- `/api/v2/instances/<ID>/jobs`

### Job Endpoints
- `/api/controller/v2/jobs/<ID>/activity_stream`
- `/api/controller/v2/jobs/<ID>/cancel`
- `/api/controller/v2/jobs/<ID>/create_schedule`
- `/api/controller/v2/jobs/<ID>/credentials`
- `/api/controller/v2/jobs/<ID>/job_events`
- `/api/controller/v2/jobs/<ID>/job_host_summaries`
- `/api/controller/v2/jobs/<ID>/labels`
- `/api/controller/v2/jobs/<ID>/notifications`
- `/api/controller/v2/jobs/<ID>/relaunch`
- `/api/controller/v2/jobs/<ID>/stdout`
- `/api/v2/jobs/<ID>/activity_stream`
- `/api/v2/jobs/<ID>/cancel`
- `/api/v2/jobs/<ID>/create_schedule`
- `/api/v2/jobs/<ID>/credentials`
- `/api/v2/jobs/<ID>/extra_credentials`
- `/api/v2/jobs/<ID>/job_events`
- `/api/v2/jobs/<ID>/job_host_summaries`
- `/api/v2/jobs/<ID>/labels`
- `/api/v2/jobs/<ID>/notifications`
- `/api/v2/jobs/<ID>/relaunch`
- `/api/v2/jobs/<ID>/stdout`

### Credential Endpoints
- `/api/v2/credentials/<ID>/access_list`
- `/api/v2/credentials/<ID>/activity_stream`
- `/api/v2/credentials/<ID>/copy`
- `/api/v2/credentials/<ID>/input_sources`
- `/api/v2/credentials/<ID>/object_roles`
- `/api/v2/credentials/<ID>/owner_teams`
- `/api/v2/credentials/<ID>/owner_users`

### Execution Environment Endpoints
- `/api/v2/execution_environments/<ID>/activity_stream`
- `/api/v2/execution_environments/<ID>/copy`
- `/api/v2/execution_environments/<ID>/unified_job_templates`

### Host Endpoints
- `/api/v2/hosts/<ID>/ansible_facts`

### Inventory Endpoints
- `/api/v2/inventories/<ID>/access_list`
- `/api/v2/inventories/<ID>/activity_stream`
- `/api/v2/inventories/<ID>/ad_hoc_commands`
- `/api/v2/inventories/<ID>/copy`
- `/api/v2/inventories/<ID>/groups`
- `/api/v2/inventories/<ID>/hosts`
- `/api/v2/inventories/<ID>/instance_groups`
- `/api/v2/inventories/<ID>/inventory_sources`
- `/api/v2/inventories/<ID>/job_templates`
- `/api/v2/inventories/<ID>/labels`
- `/api/v2/inventories/<ID>/object_roles`
- `/api/v2/inventories/<ID>/root_groups`
- `/api/v2/inventories/<ID>/script`
- `/api/v2/inventories/<ID>/tree`
- `/api/v2/inventories/<ID>/update_inventory_sources`
- `/api/v2/inventories/<ID>/variable_data`

### Inventory Source Endpoints
- `/api/v2/inventory_sources/<ID>/activity_stream`
- `/api/v2/inventory_sources/<ID>/groups`
- `/api/v2/inventory_sources/<ID>/hosts`
- `/api/v2/inventory_sources/<ID>/inventory_updates`
- `/api/v2/inventory_sources/<ID>/notification_templates_error`
- `/api/v2/inventory_sources/<ID>/notification_templates_started`
- `/api/v2/inventory_sources/<ID>/notification_templates_success`
- `/api/v2/inventory_sources/<ID>/schedules`
- `/api/v2/inventory_sources/<ID>/update`

### Inventory Update Endpoints
- `/api/v2/inventory_updates/<ID>/stdout`

### Job Template Endpoints
- `/api/v2/job_templates/<ID>/access_list`
- `/api/v2/job_templates/<ID>/activity_stream`
- `/api/v2/job_templates/<ID>/copy`
- `/api/v2/job_templates/<ID>/credentials`
- `/api/v2/job_templates/<ID>/extra_credentials`
- `/api/v2/job_templates/<ID>/instance_groups`
- `/api/v2/job_templates/<ID>/jobs`
- `/api/v2/job_templates/<ID>/labels`
- `/api/v2/job_templates/<ID>/launch`
- `/api/v2/job_templates/<ID>/notification_templates_any`
- `/api/v2/job_templates/<ID>/notification_templates_error`
- `/api/v2/job_templates/<ID>/notification_templates_success`
- `/api/v2/job_templates/<ID>/object_roles`
- `/api/v2/job_templates/<ID>/schedules`
- `/api/v2/job_templates/<ID>/slice_workflow_jobs`
- `/api/v2/job_templates/<ID>/survey_spec`

### Project Endpoints
- `/api/v2/projects/<ID>/access_list`
- `/api/v2/projects/<ID>/activity_stream`
- `/api/v2/projects/<ID>/copy`
- `/api/v2/projects/<ID>/inventories`
- `/api/v2/projects/<ID>/notification_templates_any`
- `/api/v2/projects/<ID>/notification_templates_error`
- `/api/v2/projects/<ID>/notification_templates_success`
- `/api/v2/projects/<ID>/object_roles`
- `/api/v2/projects/<ID>/playbooks`
- `/api/v2/projects/<ID>/project_updates`
- `/api/v2/projects/<ID>/schedules`
- `/api/v2/projects/<ID>/scm_inventory_sources`
- `/api/v2/projects/<ID>/teams`
- `/api/v2/projects/<ID>/update`

### Project Update Endpoints
- `/api/v2/project_updates/<ID>/cancel`
- `/api/v2/project_updates/<ID>/events`
- `/api/v2/project_updates/<ID>/notifications`
- `/api/v2/project_updates/<ID>/scm_inventory_updates`
- `/api/v2/project_updates/<ID>/stdout`

### Token Endpoints
- `/api/v2/tokens/<ID>/activity_stream`

### User Endpoints
- `/api/v2/users/<ID>/access_list`
- `/api/v2/users/<ID>/activity_stream`
- `/api/v2/users/<ID>/admin_of_organizations`
- `/api/v2/users/<ID>/authorized_tokens`
- `/api/v2/users/<ID>/credentials`
- `/api/v2/users/<ID>/organizations`
- `/api/v2/users/<ID>/personal_tokens`
- `/api/v2/users/<ID>/projects`
- `/api/v2/users/<ID>/roles`
- `/api/v2/users/<ID>/teams`
- `/api/v2/users/<ID>/tokens`

### Workflow Job Template Endpoints
- `/api/v2/workflow_job_templates/<ID>/schedules`
- `/api/v2/workflow_job_templates/<ID>/workflow_jobs`

## Gateway Endpoints

### Role Definition Endpoints
- `/api/gateway/v1/role_definitions/<ID>/team_assignments`
- `/api/gateway/v1/role_definitions/<ID>/user_assignments`

## Notes

These endpoints were extracted from 200+ Ansible support cases. To add these endpoints to the `aap_api_gather` role in the future, the following approach would be needed:

1. **Discovery Phase**: Query list endpoints (e.g., `/api/v2/jobs/`, `/api/v2/job_templates/`) to get IDs
2. **Iteration Phase**: Loop through discovered IDs and query the detail endpoints
3. **Configuration**: Add options to control which object types to dump (jobs, job_templates, inventories, etc.)
4. **Filtering**: Add options to limit the number of objects dumped (e.g., latest 10 jobs, all failed jobs, etc.)

## Example Implementation Approach

```yaml
# Pseudo-code for future implementation
- name: Get list of job IDs
  uri:
    url: "https://{{ aap_hostname }}/api/v2/jobs/?page_size=100"
  register: jobs_list

- name: Dump individual job details
  loop: "{{ jobs_list.json.results | map(attribute='id') | list }}"
  uri:
    url: "https://{{ aap_hostname }}/api/v2/jobs/{{ item }}/"
  register: job_detail
```

## Source

This list was generated by analyzing 200+ Ansible support cases from the Red Hat Support Portal. The cases were processed to extract API endpoint requests made by support engineers.

