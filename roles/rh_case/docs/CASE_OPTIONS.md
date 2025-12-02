# Red Hat Support Case Creation Options

This document lists the currently valid string values for the mandatory `case_type`, `case_severity`, and `case_product` variables when creating a new support case via the Red Hat API.

These lists reflect the options available in the Red Hat Customer Portal.

***

## 1. Case Type Options (`case_type`)

These are the valid string values for defining the nature of the support issue.

| Value | Description |
| :--- | :--- |
| **`Defect / Bug`** | Used for issues that indicate a product error or flaw. |
| **`Usage / Documentation Help`** | For questions on how to use the product or documentation errors. |
| **`Configuration Issue`** | Issues related to initial setup or changes in configuration. |
| **`Feature / Enhancement Request`** | Used to submit new feature ideas. |
| **`Account / Customer Service Request`** | Non-technical questions related to subscriptions or billing. |
| **`Certification`** | For certification-related queries. |
| **`RCA Only`** | Requesting a Root Cause Analysis. |
| **`Other`** | Used when no other category fits the issue. |

***

## 2. Case Severity Options (`case_severity`)

These are the valid abbreviated string values for defining the priority based on business impact.

| Value | Impact Level |
| :--- | :--- |
| **`1 (Urgent)`** | Severe impact to critical systems, requiring immediate attention. |
| **`2 (High)`** | Critical systems significantly degraded, actively impacting business. |
| **`3 (Normal)`** | Partial, non-critical loss of usage or performance degradation. |
| **`4 (Low)`** | A non-urgent query or documentation request. |

***

## 3. Red Hat Product Options (`case_product`)

This is the comprehensive list of valid product names as accepted by the Red Hat Support API. Users must choose one exact string from this list.

| Product Name |
| :--- |
| .NET Core |
| Ansible Automation Analytics |
| Ansible Automation Hub |
| Ansible Collections |
| Ansible Tower by Red Hat |
| Atomic Enterprise Platform |
| Azure Red Hat OpenShift |
| Cloud Management Services for Red Hat Enterprise Linux |
| Convert2RHEL |
| CoreOS Container Linux |
| CoreOS Tectonic |
| Enterprise Virtualization Management Suite (EVM) |
| Fuse ESB |
| Fuse IDE |
| Fuse Management Console |
| Fuse Mediation Router |
| Fuse Message Broker |
| Fuse Services Framework |
| GFS |
| Hybrid Committed Spend |
| Inktank Ceph Enterprise |
| JBoss A-MQ |
| JBoss Communications Platform |
| JBoss Enterprise Application Platform |
| JBoss Enterprise Application Platform expansion pack |
| JBoss Enterprise Web Platform |
| JBoss Fuse |
| JBoss jBPM |
| JBoss Rules |
| JBoss Site Publisher |
| JBoss Web Framework Kit |
| MetaMatrix Enterprise Data Services Platform |
| Migration Toolkit for Applications |
| Migration Toolkit for Containers |
| Migration Toolkit for Runtimes |
| Migration Toolkit for Virtualization |
| Mirror Registry for OpenShift |
| mirror registry for Red Hat OpenShift |
| Open Liberty |
| OpenJDK |
| OpenShift |
| OpenShift API for Data Protection |
| OpenShift Container Platform |
| OpenShift Dedicated |
| OpenShift Online |
| OpenShift Service Mesh |
| OpenShift virtualization |
| Other |
| product discovery tool |
| Quay.io |
| Quickstart Cloud Installer |
| Red Hat 3scale API Management |
| Red Hat Advanced Cluster Management for Kubernetes |
| Red Hat Advanced Cluster Security Cloud Service |
| Red Hat Advanced Cluster Security for Kubernetes |
| Red Hat AI Inference Server |
| Red Hat AMQ |
| Red Hat AMQ Clients |
| Red Hat AMQ Interconnect |
| Red Hat AMQ Online |
| Red Hat Ansible Automation Platform |
| Red Hat Ansible Automation Platform On Clouds |
| Red Hat Ansible Automation Services Catalog |
| Red Hat Ansible Engine |
| Red Hat Ansible Engine Networking Add-on |
| Red Hat Ansible Inside |
| Red Hat Application Interconnect |
| Red Hat Application Runtimes for Openshift |
| Red Hat Application Stack |
| Red Hat build of Apache Camel for Quarkus |
| Red Hat build of Apache Camel for Spring Boot |
| Red Hat build of Apache Camel-Camel K |
| Red Hat build of Apicurio Registry |
| Red Hat build of Debezium |
| Red Hat build of Eclipse Vertx |
| Red Hat build of Keycloak |
| Red Hat build of Node js |
| Red Hat build of OptaPlanner |
| Red Hat build of Quarkus |
| Red Hat build of Thorntail |
| Red Hat Ceph Storage |
| Red Hat Certificate System |
| Red Hat Cloud Data Federation for IBM Spectrum Scale |
| Red Hat CloudForms |
| Red Hat Cluster Suite |
| Red Hat CodeReady Studio - EOL |
| Red Hat CodeReady Workspaces |
| Red Hat Connectivity Link |
| Red Hat Cost Management |
| Red Hat Customer Portal |
| Red Hat Data Grid |
| Red Hat Decision Manager |
| Red Hat Developer Hub |
| Red Hat Developer Toolset |
| Red Hat Device Edge |
| Red Hat Directory Server |
| Red Hat Edge Management |
| Red Hat Enterprise IPA |
| Red Hat Enterprise Linux |
| Red Hat Enterprise Linux AI |
| Red Hat Enterprise Linux Atomic Host |
| Red Hat Enterprise Linux for ARM |
| Red Hat Enterprise Linux for IBM System z (Structure A) |
| Red Hat Enterprise Linux for Power LE (POWER9) |
| Red Hat Enterprise Linux for Real Time |
| Red Hat Enterprise Linux for SAP Applications |
| Red Hat Enterprise Linux for SAP HANA |
| Red Hat Enterprise Linux for SAP Solutions |
| Red Hat Enterprise MRG Grid |
| Red Hat Enterprise MRG Messaging |
| Red Hat Enterprise MRG Realtime |
| Red Hat Enterprise Virtualization |
| Red Hat Fuse |
| Red Hat Gluster Storage |
| Red Hat HPC |
| Red Hat Hyperconverged Infrastructure |
| Red Hat Hyperconverged Infrastructure for Cloud |
| Red Hat Infrastructure Migration Solution |
| Red Hat Insights |
| Red Hat Integration-Camel Kafka Connector |
| Red Hat Integration-Camel Quarkus |
| Red Hat Integration-Data Virtualization |
| Red Hat Integration-Operator |
| Red Hat JBoss AMQ 7 |
| Red Hat JBoss BPM Suite |
| Red Hat JBoss BRMS |
| Red Hat JBoss Data Services |
| Red Hat JBoss Data Virtualization |
| Red Hat JBoss Enterprise Application Platform |
| Red Hat JBoss Fuse Service Works |
| Red Hat JBoss Mobile Add-on |
| Red Hat JBoss Operations Network |
| Red Hat JBoss Portal |
| Red Hat JBoss SOA Platform |
| Red Hat JBoss Web Platform |
| Red Hat JBoss Web Server |
| Red Hat Managed Integration |
| Red Hat Migration Analytics |
| Red Hat Mobile Application Platform |
| Red Hat Network |
| Red Hat Offline Knowledge Portal |
| Red Hat Online Learning |
| Red Hat OpenShift AI Cloud Service |
| Red Hat OpenShift AI Self-Managed |
| Red Hat OpenShift API Management |
| Red Hat OpenShift Service on AWS |
| Red Hat OpenShift Service on AWS Hosted Control Planes |
| Red Hat OpenShift Service Registry |
| Red Hat OpenShift Streams for Apache Kafka |
| Red Hat OpenShift Support for Windows Containers |
| Red Hat OpenStack Platform |
| Red Hat Openstack Services on OpenShift |
| Red Hat Plug-Ins for Backstage |
| Red Hat Process Automation Manager |
| Red Hat Quay |
| Red Hat Satellite |
| Red Hat Service Interconnect |
| Red Hat Single Sign-On |
| Red Hat Software Collections |
| Red Hat Storage Software Appliance |
| Red Hat support for Spring Boot |
| Red Hat Trusted Application Pipeline |
| Red Hat Trusted Artifact Signer |
| Red Hat Trusted Profile Analyzer |
| Red Hat Update Infrastructure |
| Red Hat Virtualization |
| RedHat build of Apache Camel-Camel K |
| Streams for Apache Kafka |
| Subscription Asset Manager |
| Subscription Watch |

## License

GPL-3.0-or-later

## Author Information

- **Diego Felipe Mateus**