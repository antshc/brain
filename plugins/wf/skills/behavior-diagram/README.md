# Behavior Diagram

Presentation examples for the `behavior-diagram` skill.

## Flowchart Example

```mermaid
%%{init: {'themeVariables': {'lineColor': '#8b949e'}}}%%
flowchart TD
    User(["User"])
    Api["OrderController"]
    Svc["OrderService"]
    Repo[("IOrderRepository")]

    User --> Api
    Api --> Svc
    Svc --> Repo

    classDef default fill:#242424,stroke:#8b949e,color:#c9d1d9,stroke-width:1px
```

## Flowchart Delta Example

```mermaid
%%{init: {'themeVariables': {'lineColor': '#8b949e'}}}%%
flowchart TD
    Svc["OrderService"]
    Fraud["FraudCheckService"]:::added
    Legacy["LegacyOrderQueue"]:::removed

    Svc -- new check --> Fraud
    Svc -. deprecated .-> Legacy

    classDef default fill:#242424,stroke:#8b949e,color:#c9d1d9,stroke-width:1px
    classDef added stroke:#4a7a5a,stroke-width:1px
    classDef removed stroke:#8a4a4a,stroke-width:1px
```

## Swimlane Diagram Example

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
  end

  subgraph database [Order Database - Database]
    persistOrder[Persist order with state Placed]
  end

  submit -->|1. POST order| validate
  validate -->|2a. No| showResult
  validate -->|2b. Yes| placeOrder
  placeOrder -->|3b. save order| persistOrder

  classDef default fill:#242424,stroke:#8b949e,color:#c9d1d9,stroke-width:1px
```

## Swimlane Diagram Delta Example

```mermaid
%%{init: {'themeVariables': {'lineColor': '#8b949e'}}}%%
swimlane-beta TB
  subgraph restApi [Order Service - REST API]
    placeOrder[OrderService.placeOrder]
    fraudCheck[OrderService.checkFraud]
  end

  subgraph legacyQueue [Legacy Order Queue - Queue]
    notifyLegacy[Notify legacy queue]
  end

  placeOrder -->|1. new fraud check| fraudCheck
  placeOrder -.->|deprecated notify| notifyLegacy

  classDef default fill:#242424,stroke:#8b949e,color:#c9d1d9,stroke-width:1px
  classDef added stroke:#4a7a5a,stroke-width:1px
  classDef removed stroke:#8a4a4a,stroke-width:1px
  class fraudCheck added
  class notifyLegacy removed
```

## Sequence Diagram Example

```mermaid
%%{init: {'themeVariables': {
    'lineColor': '#8b949e',
    'actorBkg': '#2a2a2a', 'actorBorder': '#8b949e', 'actorTextColor': '#c9d1d9',
    'signalColor': '#8b949e', 'signalTextColor': '#c9d1d9'
}}}%%
sequenceDiagram
    autonumber
    actor User
    participant Api as OrderController
    participant Svc as OrderService
    participant Repo as IOrderRepository

    User->>Api: submit(order)
    Api->>Svc: placeOrder(order)
    Svc->>Repo: save(order)
    Repo-->>Svc: bool
    Svc-->>Api: bool
    Api-->>User: 200 OK
```

## Sequence Diagram Delta Example

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Api as OrderController
    participant Svc as OrderService
    participant Fraud as FraudCheckService
    participant Legacy as LegacyOrderQueue

    User->>Api: submit(order)
    Api->>Svc: placeOrder(order)
    note over Svc,Fraud: NEW: fraud check runs before persistence
    Svc->>Fraud: check(order)
    Fraud-->>Svc: riskScore
    note over Svc,Legacy: REMOVED: OrderService no longer notifies LegacyOrderQueue
```
