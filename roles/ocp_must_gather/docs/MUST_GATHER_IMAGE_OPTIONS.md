# Specialized Must-Gather Component Options

The `ocp_must_gather_image` variable allows users to select a specialized component collection. This is highly recommended for targeted debugging as it runs a specific Must-Gather image tailored to the component's namespace, reducing the archive size and collection time compared to the default baseline collection.

The acronyms below must be used exactly as shown in your Ansible variable (e.g., `-e ocp_must_gather_image="AAP"`).

For more details on collecting specific component data, refer to the Red Hat Knowledgebase solutions: **[Collect must-gather with more details for specific components in OpenShift](https://access.redhat.com/solutions/5459251)**.

| Acronym | Purpose / Component | Notes |
| :--- | :--- | :--- |
| **DEFAULT** | General OpenShift Baseline (Cluster Wide) | Collects OCP components only: baseline, nodes, operators, networking, and main openshift namespaces/projects only. |
| **AAP** | Red Hat Ansible Automation Platform | Targeted collection for AAP components/namespaces. |
| **OSSM** | Red Hat OpenShift Service Mesh | Targeted collection for Service Mesh/Istio components. |
| **CNV** | OpenShift Container Native Virtualization | Targeted collection for Kubevirt and CNV components. |
| **ODF** | Red Hat OpenShift Data Foundation | Targeted collection for ODF/Ceph storage components. |
| **GITOPS** | Red Hat OpenShift GitOps | Targeted collection for Argo CD and GitOps components. |
| **LOG** | Red Hat OpenShift Logging | Targeted collection for Fluentd, Loki, or Vector components. |
| **RHOAI** | Red Hat OpenShift AI | Targeted collection for AI/ML components (ODH). |
| **RHACM** | Red Hat Advanced Cluster Management for Kubernetes | Targeted collection for ACM components and managed clusters. |
| **LVM** | LVM Operator | Targeted collection for Logical Volume Manager components. |
| **SVLS** | OpenShift Serverless | Targeted collection for Knative components. |
| **OADP** | OpenShift APIs for Data Protection | Targeted collection for OADP Application backup and restore |
| **MTC** | Migration Toolkit for Containers | Targeted collection for MTC components. |
| **LSO** | Local Storage Operator | Targeted collection for LSO components. |
| **PTP** | PTP Operator | Targeted collection for Precision Time Protocol components. |
| **SEC** | Secrets Store CSI Driver Operator | Targeted collection for CSI driver components. |
| **NRO** | NUMA Resources Operator | Targeted collection for NUMA and resource topology components. |
| **COMP** | Compliance Operator | Targeted collection for security and compliance audit data. |

## License

GPL-3.0-or-later

## Author Information

- Diego Felipe Mateus