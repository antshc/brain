# To Diagram

Presentation examples for the `to-diagram` skill.

## Solution Diagram Example

<details>
<summary>Solution Diagram — Order Management System</summary>

```mermaid
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

    classDef default fill:#2a2a2a,stroke:#8b949e,color:#c9d1d9,stroke-width:2px
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

  classDef default fill:#242424,stroke:#8b949e,color:#c9d1d9,stroke-width:2px
```
</details>

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

    classDef default fill:#2a2a2a,stroke:#8b949e,color:#c9d1d9,stroke-width:2px
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

    classDef default fill:#2a2a2a,stroke:#8b949e,color:#c9d1d9,stroke-width:2px
    classDef added stroke:#4a7a5a,stroke-width:2px
    classDef removed stroke:#8a4a4a,stroke-width:2px
    classDef memberChanged stroke:#8b949e,stroke-width:2px,stroke-dasharray:5 5
```
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

## Deployment View Example

<details>
<summary>Internet Banking Deployment Topology</summary>

```mermaid
C4Container
    title Deployment diagram for Internet Banking System

    Person(customer, "Personal Banking Customer", "A customer of the bank, with personal bank accounts.")
    System_Ext(mainframe, "Mainframe Banking System", "Stores all of the core banking information about customers, accounts, transactions, etc.")

    Container_Boundary(mob, "Customer's mobile device", "Apple iOS or Android") {
        Container(mobile, "Mobile App", "Xamarin", "Provides a limited subset of the Internet Banking functionality to customers via their mobile device.")
    }

    Container_Boundary(comp, "Customer's computer", "Microsoft Windows or Apple macOS") {
        Boundary(browser, "Web Browser", "Google Chrome, Mozilla Firefox, Apple Safari or Microsoft Edge") {
            Container(spa, "Single Page Application", "JavaScript and Angular", "Provides all of the Internet Banking functionality to customers via their web browser.")
        }
    }

    Container_Boundary(plc, "Big Bank plc", "Big Bank plc data center") {
        Boundary(dn, "bigbank-api*** x8", "Ubuntu 16.04 LTS") {
            Boundary(apache, "Apache Tomcat", "Apache Tomcat 8.x") {
                Container(api, "API Application", "Java and Spring MVC", "Provides Internet Banking functionality via a JSON/HTTPS API.")
            }
        }
        Boundary(bb2, "bigbank-web*** x4", "Ubuntu 16.04 LTS") {
            Boundary(apache2, "Apache Tomcat", "Apache Tomcat 8.x") {
                Container(web, "Web Application", "Java and Spring MVC", "Delivers the static content and the Internet Banking single page application.")
            }
        }
        Boundary(bigbankdb01, "bigbank-db01", "Ubuntu 16.04 LTS") {
            Boundary(oracle, "Oracle - Primary", "Oracle 12c") {
                ContainerDb(db, "Database", "Relational Database Schema", "Stores user registration information, hashed authentication credentials, access logs, etc.")
            }
        }
        Boundary(bigbankdb02, "bigbank-db02", "Ubuntu 16.04 LTS") {
            Boundary(oracle2, "Oracle - Secondary", "Oracle 12c") {
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
