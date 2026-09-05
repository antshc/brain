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
        class OrderLineItem:::memberChanged {
            -sku : string
            +getSubtotal() decimal
            +[add] getTax() decimal
        }
        class IOrderRepository {
            +save(order) bool
        }
        class OrderExportJob:::added {
            +run()
        }
    }
    namespace Infrastructure {
        class SqlOrderRepository:::memberChanged {
            -connectionString : string
            -[rem] legacyConnectionString : string
            +save(order) bool
        }
        class LegacyOrderQueue:::removed {
            -queueName : string
        }
    }

    OrderController --|> BaseController
    OrderController *-- OrderLineItem
    OrderService o-- IOrderRepository
    SqlOrderRepository ..|> IOrderRepository
    OrderController ..> OrderService

    note for OrderService "Coordinates order use cases; delegates persistence to IOrderRepository"

    classDef default fill:#2a2a2a,stroke:#8b949e,color:#c9d1d9,stroke-width:2px
    classDef added stroke:#4a7a5a,stroke-width:2px
    classDef removed stroke:#8a4a4a,stroke-width:2px
    classDef memberChanged stroke:#8b949e,stroke-width:2px,stroke-dasharray: 4 3
```
</details>
