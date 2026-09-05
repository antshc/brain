## Container Diagram Delta Example

<details>
<summary>Order Management System — Container Delta</summary>

```mermaid
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
</details>

**Behaviour changes**
- `+` Order Export Queue replaces the legacy export path.
- `-` Legacy Order Queue is removed.
- `~` Order Service publishes exports through Azure Service Bus.
