# Code Diagram

Presentation examples for the `code-diagram` skill.

## Class Diagram Example

<details>
<summary>Order Management Domain Classes</summary>

```mermaid
%%{init: {'themeVariables': {'lineColor': '#8b949e'}}}%%
classDiagram
    namespace Api {
        class BaseController {
            #logger : ILogger
        }
        class OrderController {
            -orderService : OrderService
            +submit(order) bool
        }
    }
    namespace Domain {
        class OrderService {
            -repository : IOrderRepository
            ~cache : OrderCache
            +placeOrder(order) bool
            +getInstance() OrderService$
        }
        class OrderLineItem {
            -sku : string
            +getSubtotal() decimal
            +getTax() decimal
        }
        class IOrderRepository {
            +save(order) bool
        }
        class OrderExportJob {
            +run()
        }
    }
    namespace Infrastructure {
        class SqlOrderRepository {
            -connectionString : string
            +save(order) bool
        }
        class LegacyOrderQueue {
            -queueName : string
        }
    }

    OrderController --|> BaseController
    OrderController *-- OrderLineItem
    OrderService o-- IOrderRepository
    SqlOrderRepository ..|> IOrderRepository
    OrderController ..> OrderService

    note for OrderService "Coordinates order use cases; delegates persistence to IOrderRepository"

    classDef default fill:#242424,stroke:#8b949e,color:#c9d1d9,stroke-width:1px
```
</details>

## Class Diagram Delta Example

<details>
<summary>Order Processing — Class Delta</summary>

```mermaid
%%{init: {'themeVariables': {'lineColor': '#8b949e'}}}%%
classDiagram
    namespace Domain {
        class OrderService
        class OrderLineItem:::memberChanged {
            +[add] getTax() decimal
        }
        class OrderExportJob:::added {
            +run()
        }
    }
    namespace Infrastructure {
        class LegacyOrderQueue:::removed {
            -queueName : string
        }
    }

    OrderService *-- OrderLineItem
    OrderService ..> OrderExportJob : Use
    OrderService ..> LegacyOrderQueue : Use

    classDef default fill:#242424,stroke:#8b949e,color:#c9d1d9,stroke-width:1px
    classDef added stroke:#4a7a5a,stroke-width:1px
    classDef removed stroke:#8a4a4a,stroke-width:1px
    classDef memberChanged stroke:#8b949e,stroke-width:1px,stroke-dasharray:5 5
```
</details>
