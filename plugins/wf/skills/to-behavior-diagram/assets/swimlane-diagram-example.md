## Swimlane Diagram Example

<details>
<summary>Order Fulfillment Swimlane</summary>

```mermaid
%%{init: {'themeVariables': {'lineColor': '#8b949e'}}}%%
swimlane-beta TB
  subgraph frontend [Web Portal - GUI]
    submit[Customer clicks Place Order]
    showResult([Show confirmation / error])
  end

  subgraph restApi [Order Service - REST API]
    validate{Order valid and in stock?}
    placeOrder[OrderService.placeOrder]
    respond200[Respond 200 + order id]
    respond400[Respond 400 + error]
  end

  subgraph database [Order Database - Database]
    persistOrder[Persist order with state Placed]
  end

  submit -->|POST orders with order payload| validate
  validate -->|No| respond400
  validate -->|Yes| placeOrder
  placeOrder -->|save order| persistOrder
  persistOrder -->|order id| respond200
  respond200 -->|200 OK with order id| showResult
  respond400 -->|400 Bad Request| showResult

  classDef default fill:#242424,stroke:#8b949e,color:#c9d1d9,stroke-width:2px
```
</details>
