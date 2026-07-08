# Requirement Output Examples

Worked examples of a complete requirement set produced by /to-requirements. Written in plain business language, solution-agnostic, and ready to hand to /to-story.

## Example — deleted file recovery

**Input idea:** *Let administrators restore files that were accidentally deleted.*

```
Recover accidentally deleted files

### Stakeholder Requirement
Administrators need to restore accidentally deleted files without contacting support, so content is recovered quickly and support load drops.

### Functional Requirements
- The system must retain deleted files for 30 days before permanent deletion.
- The system must let an administrator review the files available for recovery.
- The system must restore a selected file to its original location.
- The system must require the administrator to choose a new location when the original location no longer exists.
- The system must prevent users without restore permission from restoring files.
- The system must record an audit event when a file is restored.

### Business Rules
- A deleted file may only be restored within 30 days of deletion.
- Only users with the restore permission may restore a file.
- A file that no longer exists in storage must not be offered for recovery.

### Edge Cases
- Retention window expired → the file is not offered for recovery and the reason is explained.
- Original location removed → the administrator must choose a new destination before restore proceeds.
- Restore requested without permission → the action is denied.
```

## Example — real-time availability in the catalog

**Input idea:** *Show real-time banana stock in the catalog.*

```
Show real-time availability in the catalog

### Stakeholder Requirement
Customers need to know whether an item is currently available before adding it to the cart, so they avoid ordering products that cannot be fulfilled.

### Functional Requirements
- The system must retrieve current availability for each item shown on the catalog page.
- The system must display an availability status beside every visible item.
- The system must keep rendering the catalog when availability retrieval partially fails.

### Business Rules
- If availability is Available, show "In Stock".
- If availability is Unavailable, show "Out of Stock".
- If availability is missing or unknown, show "Availability Unknown".
- If an item no longer exists in the source system, its availability must not be shown.

### Edge Cases
- Availability source slow or unavailable → the catalog still renders and affected items show "Availability Unknown".
- Item absent from the source system → no availability status is displayed for it.
```
