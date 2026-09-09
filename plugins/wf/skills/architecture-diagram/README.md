# Architecture Diagram

Presentation examples for the `architecture-diagram` skill.

## Solution Diagram Example

```mermaid
---
config:
  c4:
    c4ShapePadding: 20
---
C4Container
    title Container diagram for Order Management System

    Person(customer, "Customer", "Places and tracks orders")
    System_Ext(email_system, "E-Mail System", "Sends confirmations")

    System_Boundary(system, "Order Management System") {
        Container(api, "Order API", "ASP.NET Core", "Accepts order requests")
        Container(svc, "Order Service", "C# / .NET", "Coordinates order processing")
        ContainerDb(db, "Order Database", "SQL Server", "Stores orders")
    }

    Rel(customer, api, "Submits order", "HTTPS")
    Rel(api, svc, "Places order")
    Rel(svc, db, "Reads and writes", "EF Core")
    Rel(svc, email_system, "Sends confirmation", "SMTP")

    UpdateElementStyle(customer, $fontColor="#c9d1d9", $bgColor="#2a2a2a", $borderColor="#4a5a8a")
    UpdateElementStyle(api, $fontColor="#c9d1d9", $bgColor="#2a2a2a", $borderColor="#8b949e")
    UpdateElementStyle(svc, $fontColor="#c9d1d9", $bgColor="#2a2a2a", $borderColor="#8b949e")
    UpdateElementStyle(db, $fontColor="#c9d1d9", $bgColor="#2a2a2a", $borderColor="#8b949e")
    UpdateElementStyle(email_system, $fontColor="#c9d1d9", $bgColor="#1a1a1a", $borderColor="#8b949e")
    UpdateRelStyle(customer, api, $textColor="#c9d1d9", $lineColor="#8b949e")
    UpdateRelStyle(api, svc, $textColor="#c9d1d9", $lineColor="#8b949e")
    UpdateRelStyle(svc, db, $textColor="#c9d1d9", $lineColor="#8b949e")
    UpdateRelStyle(svc, email_system, $textColor="#c9d1d9", $lineColor="#8b949e")
```

## Container Diagram Delta Example

```mermaid
C4Container
    title Container delta for Order Management System

    System_Boundary(system, "Order Management System") {
        Container(service, "Order Service", "C# / .NET", "Coordinates order processing")
        ContainerQueue(exportQueue, "Order Export Queue", "Azure Service Bus", "New export path")
        ContainerQueue(legacyQueue, "Legacy Order Queue", "RabbitMQ", "Removed export path")
    }

    Rel(service, exportQueue, "Publishes order", "async")
    Rel(service, legacyQueue, "Previously published order", "async")

    UpdateElementStyle(service, $fontColor="#c9d1d9", $bgColor="#2a2a2a", $borderColor="#8b949e")
    UpdateElementStyle(exportQueue, $fontColor="#c9d1d9", $bgColor="#2a2a2a", $borderColor="#4a7a5a")
    UpdateElementStyle(legacyQueue, $fontColor="#c9d1d9", $bgColor="#2a2a2a", $borderColor="#8a4a4a")
    UpdateRelStyle(service, exportQueue, $textColor="#c9d1d9", $lineColor="#4a7a5a")
    UpdateRelStyle(service, legacyQueue, $textColor="#c9d1d9", $lineColor="#8a4a4a")
```

**Behaviour changes**
- `+` Order Export Queue replaces the legacy export path.
- `-` Legacy Order Queue is removed.

## Deployment View Example

```mermaid
C4Container
    title Deployment diagram for Order Management System

    Container_Boundary(cluster, "Order Cluster") {
        Boundary(apiNode, "order-api*** x4", "Ubuntu 22.04 LTS") {
            Container(api, "API Application", "ASP.NET Core", "Accepts orders")
        }
        Boundary(dbNode, "order-db01", "Ubuntu 22.04 LTS") {
            ContainerDb(db, "Order Database", "PostgreSQL", "Stores orders")
        }
    }

    Rel(api, db, "Reads and writes", "TCP")
    UpdateElementStyle(api, $fontColor="#c9d1d9", $bgColor="#2a2a2a", $borderColor="#8b949e")
    UpdateElementStyle(db, $fontColor="#c9d1d9", $bgColor="#2a2a2a", $borderColor="#8b949e")
    UpdateRelStyle(api, db, $textColor="#c9d1d9", $lineColor="#8b949e")
```

## Deployment View Delta Example

```mermaid
C4Container
    title Deployment delta for Order Management System

    Container_Boundary(cluster, "Order Cluster") {
        Boundary(node1, "order-api*** x4", "Ubuntu 22.04 LTS") {
            Container(api, "API Application", "ASP.NET Core", "Accepts orders")
        }
        Boundary(node2, "order-worker*** x2", "Ubuntu 22.04 LTS") {
            Container(worker, "Fraud Check Worker", "ASP.NET Core", "New fraud-check process")
        }
        Boundary(node3, "order-legacy01", "Ubuntu 18.04 LTS") {
            Container(legacy, "Legacy Batch Job", ".NET Framework", "Removed export job")
        }
    }

    Rel(api, worker, "Publishes for review", "async")
    Rel(api, legacy, "Previously exported to", "async")

    UpdateElementStyle(api, $fontColor="#c9d1d9", $bgColor="#2a2a2a", $borderColor="#8b949e")
    UpdateElementStyle(worker, $fontColor="#c9d1d9", $bgColor="#2a2a2a", $borderColor="#4a7a5a")
    UpdateElementStyle(legacy, $fontColor="#c9d1d9", $bgColor="#2a2a2a", $borderColor="#8a4a4a")
    UpdateRelStyle(api, worker, $textColor="#c9d1d9", $lineColor="#4a7a5a")
    UpdateRelStyle(api, legacy, $textColor="#c9d1d9", $lineColor="#8a4a4a")
```
