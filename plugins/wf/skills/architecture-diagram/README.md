# Architecture Diagram

Presentation examples for the `architecture-diagram` skill.

## System Context Diagram Example

<details>
<summary>System Context Diagram — Order Management System</summary>

```mermaid
---
config:
  c4:
    c4ShapePadding: 20
---
C4Context
    title System Context diagram for Order Management System

    Person(customer, "Customer", "Places and tracks orders")
    Person_Ext(auditor, "External Auditor", "Third-party compliance auditor")

    System(oms, "Order Management System", "Accepts, fulfils, and reports on customer orders")

    System_Ext(mainframe, "Mainframe Banking System", "Processes payments and settlement")
    System_Ext(email_system, "E-Mail System", "Delivers order confirmations to customers")
    SystemDb_Ext(catalogue, "Partner Product Catalogue", "Master record for products and pricing")

    Rel(customer, oms, "Submits and tracks orders", "HTTPS")
    Rel(auditor, oms, "Reviews order records via", "read-only export")
    Rel(oms, mainframe, "Charges payment via", "sync/async, HTTPS")
    Rel(oms, email_system, "Sends confirmations via", "SMTP")
    Rel(oms, catalogue, "Imports products and pricing from", "nightly feed")

    UpdateElementStyle(customer, $fontColor="#c9d1d9", $bgColor="#2a2a2a", $borderColor="#4a5a8a")
    UpdateElementStyle(auditor, $fontColor="#c9d1d9", $bgColor="#1a1a1a", $borderColor="#4a5a8a")
    UpdateElementStyle(oms, $fontColor="#c9d1d9", $bgColor="#2a2a2a", $borderColor="#8b949e")
    UpdateElementStyle(mainframe, $fontColor="#c9d1d9", $bgColor="#1a1a1a", $borderColor="#8b949e")
    UpdateElementStyle(email_system, $fontColor="#c9d1d9", $bgColor="#1a1a1a", $borderColor="#8b949e")
    UpdateElementStyle(catalogue, $fontColor="#c9d1d9", $bgColor="#1a1a1a", $borderColor="#8b949e")

    UpdateRelStyle(customer, oms, $textColor="#c9d1d9", $lineColor="#8b949e", $offsetX="-70", $offsetY="-10")
    UpdateRelStyle(auditor, oms, $textColor="#c9d1d9", $lineColor="#8b949e", $offsetX="40", $offsetY="10")
    UpdateRelStyle(oms, mainframe, $textColor="#c9d1d9", $lineColor="#8b949e", $offsetX="-80", $offsetY="-20")
    UpdateRelStyle(oms, email_system, $textColor="#c9d1d9", $lineColor="#8b949e", $offsetX="30", $offsetY="-20")
    UpdateRelStyle(oms, catalogue, $textColor="#c9d1d9", $lineColor="#8b949e", $offsetX="-60", $offsetY="120")
```
</details>

## Solution Diagram Example

<details>
<summary>Solution Diagram — Order Management System</summary>

```mermaid
---
config:
  c4:
    c4ShapePadding: 20
---
C4Container
    title Container diagram for Order Management System

    Person(customer, "Customer", "Places and tracks orders")
    Person_Ext(auditor, "External Auditor", "Third-party compliance auditor")
    System_Ext(email_system, "E-Mail System", "Sends order confirmation e-mails")
    System_Ext(mainframe, "Mainframe Banking System", "Processes payments")

    System_Boundary(system, "Order Management System") {
        Container(api, "OrderController", "ASP.NET Core", "Accepts and validates order submissions")
        Container(svc, "OrderService", "C# / .NET", "Coordinates order placement and persistence")
        ContainerDb(db, "Order Database", "SQL Server", "Stores orders and line items")
        ContainerQueue(queue, "OrderExportJob", "Azure Service Bus", "Publishes fulfilled orders downstream")
    }

    Rel(customer, api, "Submits order", "HTTPS")
    Rel(api, svc, "Places order via")
    Rel(svc, db, "Reads from and writes to", "EF Core")
    Rel(svc, queue, "Publishes to", "async")
    Rel(svc, mainframe, "Charges payment via", "sync/async, HTTPS")
    Rel(svc, email_system, "Sends confirmation via", "SMTP")
    Rel(auditor, db, "Reviews order records via", "read-only export")

    UpdateElementStyle(customer, $fontColor="#c9d1d9", $bgColor="#2a2a2a", $borderColor="#4a5a8a")
    UpdateElementStyle(auditor, $fontColor="#c9d1d9", $bgColor="#1a1a1a", $borderColor="#4a5a8a")
    UpdateElementStyle(api, $fontColor="#c9d1d9", $bgColor="#2a2a2a", $borderColor="#8b949e")
    UpdateElementStyle(svc, $fontColor="#c9d1d9", $bgColor="#2a2a2a", $borderColor="#8b949e")
    UpdateElementStyle(db, $fontColor="#c9d1d9", $bgColor="#2a2a2a", $borderColor="#8b949e")
    UpdateElementStyle(queue, $fontColor="#c9d1d9", $bgColor="#2a2a2a", $borderColor="#8b949e")
    UpdateElementStyle(email_system, $fontColor="#c9d1d9", $bgColor="#1a1a1a", $borderColor="#8b949e")
    UpdateElementStyle(mainframe, $fontColor="#c9d1d9", $bgColor="#1a1a1a", $borderColor="#8b949e")
    UpdateRelStyle(customer, api, $textColor="#c9d1d9", $lineColor="#8b949e", $offsetY="-10")
    UpdateRelStyle(api, svc, $textColor="#c9d1d9", $lineColor="#8b949e")
    UpdateRelStyle(svc, db, $textColor="#c9d1d9", $lineColor="#8b949e")
    UpdateRelStyle(svc, queue, $textColor="#c9d1d9", $lineColor="#8b949e")
    UpdateRelStyle(svc, mainframe, $textColor="#c9d1d9", $lineColor="#8b949e", $offsetY="20", $offsetX="-30")
    UpdateRelStyle(svc, email_system, $textColor="#c9d1d9", $lineColor="#8b949e")
    UpdateRelStyle(auditor, db, $textColor="#c9d1d9", $lineColor="#8b949e")
```
</details>

## Container Diagram Delta Example

<details>
<summary>Order Management System — Container Delta</summary>

```mermaid
---
config:
  c4:
    c4ShapePadding: 0
---
C4Container
    title Container delta for Order Management System

    Person(customer, "Customer", "Places orders")

    System_Boundary(system, "Order Management System") {
        Container(api, "Order API", "ASP.NET Core", "Accepts order requests")
        Container(service, "Order Service", "C# / .NET", "Coordinates order processing")
        ContainerQueue(exportQueue, "Order Export Queue", "Azure Service Bus", "New asynchronous export path")
        ContainerQueue(legacyQueue, "Legacy Order Queue", "RabbitMQ", "Removed export path")
    }

    Rel(customer, api, "Submits order", "HTTPS")
    Rel(api, service, "Places order")
    Rel(service, exportQueue, "Publishes order", "async")
    Rel(service, legacyQueue, "Previously published order", "async")

    UpdateElementStyle(customer, $fontColor="#c9d1d9", $bgColor="#2a2a2a", $borderColor="#8b949e")
    UpdateElementStyle(api, $fontColor="#c9d1d9", $bgColor="#2a2a2a", $borderColor="#8b949e")
    UpdateElementStyle(service, $fontColor="#c9d1d9", $bgColor="#2a2a2a", $borderColor="#8b949e")
    UpdateElementStyle(exportQueue, $fontColor="#c9d1d9", $bgColor="#2a2a2a", $borderColor="#4a7a5a")
    UpdateElementStyle(legacyQueue, $fontColor="#c9d1d9", $bgColor="#2a2a2a", $borderColor="#8a4a4a")

    UpdateRelStyle(customer, api, $textColor="#c9d1d9", $lineColor="#8b949e")
    UpdateRelStyle(api, service, $textColor="#c9d1d9", $lineColor="#8b949e")
    UpdateRelStyle(service, exportQueue, $textColor="#c9d1d9", $lineColor="#4a7a5a")
    UpdateRelStyle(service, legacyQueue, $textColor="#c9d1d9", $lineColor="#8a4a4a")
```

**Behaviour changes**
- `+` Order Export Queue replaces the legacy export path.
- `-` Legacy Order Queue is removed.
- `~` Order Service publishes exports through Azure Service Bus.

</details>

## Deployment View Example

<details>
<summary>Internet Banking Deployment Topology</summary>

```mermaid
C4Deployment
    title Deployment diagram for Internet Banking System

    Person(customer, "Personal Banking Customer", "A customer of the bank, with personal bank accounts.")
    System_Ext(mainframe, "Mainframe Banking System", "Stores all of the core banking information about customers, accounts, transactions, etc.")

    Deployment_Node(mob, "Customer's mobile device", "Apple iOS or Android") {
        Container(mobile, "Mobile App", "Xamarin", "Provides a limited subset of the Internet Banking functionality to customers via their mobile device.")
    }

    Deployment_Node(comp, "Customer's computer", "Microsoft Windows or Apple macOS") {
        Deployment_Node(browser, "Web Browser", "Google Chrome, Mozilla Firefox, Apple Safari or Microsoft Edge") {
            Container(spa, "Single Page Application", "JavaScript and Angular", "Provides all of the Internet Banking functionality to customers via their web browser.")
        }
    }

    Deployment_Node(plc, "Big Bank plc", "Big Bank plc data center") {
        Deployment_Node(dn, "bigbank-api*** x8", "Ubuntu 16.04 LTS") {
            Deployment_Node(apache, "Apache Tomcat", "Apache Tomcat 8.x") {
                Container(api, "API Application", "Java and Spring MVC", "Provides Internet Banking functionality via a JSON/HTTPS API.")
            }
        }
        Deployment_Node(bb2, "bigbank-web*** x4", "Ubuntu 16.04 LTS") {
            Deployment_Node(apache2, "Apache Tomcat", "Apache Tomcat 8.x") {
                Container(web, "Web Application", "Java and Spring MVC", "Delivers the static content and the Internet Banking single page application.")
            }
        }
        Deployment_Node(bigbankdb01, "bigbank-db01", "Ubuntu 16.04 LTS") {
            Deployment_Node(oracle, "Oracle - Primary", "Oracle 12c") {
                ContainerDb(db, "Database", "Relational Database Schema", "Stores user registration information, hashed authentication credentials, access logs, etc.")
            }
        }
        Deployment_Node(bigbankdb02, "bigbank-db02", "Ubuntu 16.04 LTS") {
            Deployment_Node(oracle2, "Oracle - Secondary", "Oracle 12c") {
                ContainerDb(db2, "Database", "Relational Database Schema", "Stores user registration information, hashed authentication credentials, access logs, etc.")
            }
        }
    }

    Rel(customer, mobile, "Uses")
    Rel(customer, spa, "Uses")
    Rel(mobile, api, "Makes API calls to", "json/HTTPS")
    Rel(spa, api, "Makes API calls to", "json/HTTPS")
    Rel_U(web, spa, "Delivers to the customer's web browser")
    Rel(api, db, "Reads from and writes to", "JDBC")
    Rel(api, db2, "Reads from and writes to", "JDBC")
    Rel_R(db, db2, "Replicates data to")
    Rel(api, mainframe, "Makes API calls to", "XML/HTTPS")

    UpdateElementStyle(customer, $fontColor="#c9d1d9", $bgColor="#2a2a2a", $borderColor="#4a5a8a")
    UpdateElementStyle(mobile, $fontColor="#c9d1d9", $bgColor="#2a2a2a", $borderColor="#8b949e")
    UpdateElementStyle(spa, $fontColor="#c9d1d9", $bgColor="#2a2a2a", $borderColor="#8b949e")
    UpdateElementStyle(api, $fontColor="#c9d1d9", $bgColor="#2a2a2a", $borderColor="#8b949e")
    UpdateElementStyle(web, $fontColor="#c9d1d9", $bgColor="#2a2a2a", $borderColor="#8b949e")
    UpdateElementStyle(db, $fontColor="#c9d1d9", $bgColor="#2a2a2a", $borderColor="#8b949e")
    UpdateElementStyle(db2, $fontColor="#c9d1d9", $bgColor="#2a2a2a", $borderColor="#8b949e")
    UpdateElementStyle(mainframe, $fontColor="#c9d1d9", $bgColor="#1a1a1a", $borderColor="#8b949e")

    UpdateRelStyle(customer, mobile, $textColor="#c9d1d9", $lineColor="#8b949e")
    UpdateRelStyle(customer, spa, $textColor="#c9d1d9", $lineColor="#8b949e")
    UpdateRelStyle(mobile, api, $textColor="#c9d1d9", $lineColor="#8b949e")
    UpdateRelStyle(spa, api, $textColor="#c9d1d9", $lineColor="#8b949e", $offsetY="-40")
    UpdateRelStyle(web, spa, $textColor="#c9d1d9", $lineColor="#8b949e", $offsetY="-40")
    UpdateRelStyle(api, db, $textColor="#c9d1d9", $lineColor="#8b949e", $offsetY="-20", $offsetX="5")
    UpdateRelStyle(api, db2, $textColor="#c9d1d9", $lineColor="#8b949e", $offsetX="-40", $offsetY="-20")
    UpdateRelStyle(db, db2, $textColor="#c9d1d9", $lineColor="#8b949e", $offsetY="-10")
    UpdateRelStyle(api, mainframe, $textColor="#c9d1d9", $lineColor="#8b949e")
```
</details>

## Deployment View Delta Example

<details>
<summary>Order Management System — Deployment Delta</summary>

```mermaid
---
config:
  c4:
    c4ShapePadding: 20
---
C4Deployment
    title Deployment delta for Order Management System

    Deployment_Node(cluster, "Order Cluster", "Kubernetes") {
        Deployment_Node(node1, "order-api*** x4", "Ubuntu 22.04 LTS") {
            Container(api, "API Application", "ASP.NET Core", "Accepts and validates order submissions")
        }
        Deployment_Node(node2, "order-worker*** x2", "Ubuntu 22.04 LTS") {
            Container(worker, "Fraud Check Worker", "ASP.NET Core", "New background fraud-check process")
        }
        Deployment_Node(node3, "order-legacy01", "Ubuntu 18.04 LTS") {
            Container(legacy, "Legacy Batch Job", ".NET Framework", "Removed nightly export job")
        }
    }

    Rel(api, worker, "Publishes order for review", "async")
    Rel(api, legacy, "Previously exported orders to", "async")

    UpdateElementStyle(api, $fontColor="#c9d1d9", $bgColor="#2a2a2a", $borderColor="#8b949e")
    UpdateElementStyle(worker, $fontColor="#c9d1d9", $bgColor="#2a2a2a", $borderColor="#4a7a5a")
    UpdateElementStyle(legacy, $fontColor="#c9d1d9", $bgColor="#2a2a2a", $borderColor="#8a4a4a")

    UpdateRelStyle(api, worker, $textColor="#c9d1d9", $lineColor="#4a7a5a")
    UpdateRelStyle(api, legacy, $textColor="#c9d1d9", $lineColor="#8a4a4a")
```

**Behaviour changes**
- `+` Fraud Check Worker node added to run asynchronous fraud review.
- `-` Legacy Batch Job node and its host are being decommissioned.

</details>
