# Lift-the-Widget Reference

Detailed rules for keeping requirement statements and acceptance criteria solution-agnostic.

## Lift-the-widget rule
If the statement names a UI artifact or component (screen, service, table), it is describing the solution. Raise it one level to the behavior it enables, and move the artifact into design.
- Reject: *Display a cart badge in the page header.* (names a widget + placement)
- Prefer: *Keep shoppers aware of the number of items in their cart so they can proceed to purchase without leaving their current view.* (names behavior, entity, scope, value)

## Solution-agnostic test
If changing the UI or technology (badge → banner, poll → push) would force you to reword the statement, it is over-specified — rewrite it.

## De-lifting reference
Raise the named artifact to the behavior it enables:

| Leaked artifact | Behavior to state instead |
| --- | --- |
| badge / icon | make the user aware that … |
| header / sidebar / placement | keep the user aware during their workflow |
| button / link / "click X" | let the user act on … in a single step |
| banner / toast / popup | inform the user when … |
| dropdown / picker | let the user choose one option from the available set |
| table / grid | let the user review list of records ..|
| counter / number display | keep the count of … current for the user |

## Criteria obey lift-the-widget too
A criterion states an observable outcome, not the control that produces it. Write what the user perceives or can do, not what they tap.
- Reject: *Selecting the cart badge opens the cart panel.* (names widget + interaction)
- Prefer: *The shopper can reach the full cart contents in a single step from the notification.*

## Verb → Component Hints
persist → repository/accessor · validate → validator · create → provisioner · external API → client/gateway · emit alert → alert service · process async → worker · expose API → controller
