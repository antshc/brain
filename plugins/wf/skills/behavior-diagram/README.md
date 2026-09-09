# Behavior Diagram

Presentation examples for the `behavior-diagram` skill.

## Flowchart Example

<details>
<summary>Order Processing Flowchart</summary>

```mermaid
%%{init: {'themeVariables': {'lineColor': '#8b949e'}}}%%
flowchart TD
    User(["User"])
    Api["OrderController"]
    Svc["OrderService"]
    Repo[("IOrderRepository")]
    Queue["OrderExportJob"]
    Legacy["LegacyOrderQueue"]

    User --> Api
    Api --> Svc
    Svc --> Repo
    Svc -- valid order --> Queue
    Svc -. deprecated .-> Legacy

    subgraph Infrastructure
        Repo
        Legacy
    end

    classDef default fill:#242424,stroke:#8b949e,color:#c9d1d9,stroke-width:1px
```
</details>

## Flowchart Delta Example

<details>
<summary>Order Processing — Flowchart Delta</summary>

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
</details>

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

  submit -->|1. POST orders with order payload| validate
  validate -->|2a. No| respond400
  validate -->|2b. Yes| placeOrder
  respond400 -->|3a. 400 Bad Request| showResult
  placeOrder -->|3b. save order| persistOrder
  persistOrder -->|4b. order id| respond200
  respond200 -->|5b. 200 OK with order id| showResult

  classDef default fill:#242424,stroke:#8b949e,color:#c9d1d9,stroke-width:1px
```
</details>

## Swimlane Diagram Delta Example

<details>
<summary>Order Fulfillment — Swimlane Delta</summary>

```mermaid
%%{init: {'themeVariables': {'lineColor': '#8b949e'}}}%%
swimlane-beta TB
  subgraph restApi [Order Service - REST API]
    placeOrder[OrderService.placeOrder]
    fraudCheck[OrderService.checkFraud]
  end

  subgraph database [Order Database - Database]
    persistOrder[Persist order with state Placed]
  end

  subgraph legacyQueue [Legacy Order Queue - Queue]
    notifyLegacy[Notify legacy queue]
  end

  placeOrder -->|1. new fraud check| fraudCheck
  fraudCheck -->|2. save order| persistOrder
  placeOrder -.->|deprecated notify| notifyLegacy

  classDef default fill:#242424,stroke:#8b949e,color:#c9d1d9,stroke-width:1px
  classDef added stroke:#4a7a5a,stroke-width:1px
  classDef removed stroke:#8a4a4a,stroke-width:1px
  class fraudCheck added
  class notifyLegacy removed
```

**Behaviour changes**
- `-` The entire "Legacy Order Queue" lane is being removed; Mermaid's `subgraph` has no supported border-color hook, so the removal is called out here in prose.

</details>

## Sequence Diagram Example

<details>
<summary>Order Submission Sequence</summary>

```mermaid
%%{init: {'themeVariables': {
    'lineColor': '#8b949e',
    'actorBkg': '#2a2a2a', 'actorBorder': '#8b949e', 'actorTextColor': '#c9d1d9', 'actorLineColor': '#8b949e',
    'signalColor': '#8b949e', 'signalTextColor': '#c9d1d9',
    'labelBoxBkgColor': '#2a2a2a', 'labelBoxBorderColor': '#8b949e', 'labelTextColor': '#c9d1d9',
    'loopTextColor': '#c9d1d9',
    'noteBkgColor': '#2a2a2a', 'noteBorderColor': '#8b949e', 'noteTextColor': '#c9d1d9',
    'activationBorderColor': '#8b949e', 'activationBkgColor': '#2a2a2a',
    'sequenceNumberColor': '#c9d1d9'
}}}%%
sequenceDiagram
    autonumber
    actor User
    participant Api as OrderController
    participant Svc as OrderService
    participant Repo as IOrderRepository
    participant Queue as OrderExportJob

    User->>Api: submit(order)
    activate Api
    Api->>Svc: placeOrder(order)
    activate Svc
    Svc->>Repo: save(order)
    activate Repo
    Repo-->>Svc: bool
    deactivate Repo
    alt order valid
        Svc->>Queue: run()
        Queue-->>Svc: ack
    else order invalid
        Svc-->>Api: throws ValidationError
    end
    Svc-->>Api: bool
    deactivate Svc
    Api-->>User: 200 OK
    deactivate Api

    note over Svc,Repo: persistence is transactional
```
</details>

## Sequence Diagram Delta Example

<details>
<summary>Order Submission — Sequence Delta</summary>

```mermaid
%%{init: {'themeVariables': {
    'lineColor': '#8b949e',
    'actorBkg': '#2a2a2a', 'actorBorder': '#8b949e', 'actorTextColor': '#c9d1d9', 'actorLineColor': '#8b949e',
    'signalColor': '#8b949e', 'signalTextColor': '#c9d1d9',
    'labelBoxBkgColor': '#2a2a2a', 'labelBoxBorderColor': '#8b949e', 'labelTextColor': '#c9d1d9',
    'loopTextColor': '#c9d1d9',
    'noteBkgColor': '#2a2a2a', 'noteBorderColor': '#8b949e', 'noteTextColor': '#c9d1d9',
    'activationBorderColor': '#8b949e', 'activationBkgColor': '#2a2a2a',
    'sequenceNumberColor': '#c9d1d9'
}}}%%
sequenceDiagram
    autonumber
    actor User
    participant Api as OrderController
    participant Svc as OrderService
    participant Fraud as FraudCheckService
    participant Legacy as LegacyOrderQueue

    User->>Api: submit(order)
    activate Api
    Api->>Svc: placeOrder(order)
    activate Svc
    note over Svc,Fraud: NEW: fraud check runs before persistence
    Svc->>Fraud: check(order)
    Fraud-->>Svc: riskScore
    Svc-->>Api: bool
    deactivate Svc
    Api-->>User: 200 OK
    deactivate Api

    note over Svc,Legacy: REMOVED: OrderService no longer notifies LegacyOrderQueue
```
</details>
