Capability → Feature → Functional Slice → Functional Requirement → Acceptance Criteria / Business Rules

Example
```
Capability: Customer Account Management
│
├── Feature: User Authentication
│   │
│   ├── Functional Slice: User Login
│   │   ├── Functional Requirement: The system shall allow registered users to log in.
│   │   ├── Functional Requirement: The system shall validate user credentials.
│   │   └── Functional Requirement: The system shall display an error for invalid credentials.
│   │
│   └── Functional Slice: Password Reset
│       ├── Functional Requirement: The system shall allow users to request a password reset.
│       └── Functional Requirement: The system shall send a password-reset link.
│
└── Feature: User Profile Management
    │
    └── Functional Slice: Update Profile
        ├── Functional Requirement: The system shall allow users to update their name.
        ├── Functional Requirement: The system shall allow users to update their contact details.
        └── Functional Requirement: The system shall validate mandatory profile information.
```

Hierarchy Levels

Level| Meaning| Example
Capability| Broad business or organizational ability| Customer Account Management
Feature| Significant system functionality that supports the capability| User Authentication
Functional Slice| A specific end-to-end user or business flow within a feature| User Login
Functional Requirement| Specific, testable behavior the system must provide| The system shall validate login credentials
Acceptance Criteria / Business Rules| Conditions defining how the requirement should behave and when it is considered complete| Invalid password displays an error

Conceptual Structure

Business Capability
      ↓
Feature
      ↓
Functional Slice
      ↓
Functional Requirement
      ↓
Acceptance Criteria / Business Rules

A useful distinction is that capabilities describe what the business needs to be able to do, while features, functional slices, and functional requirements progressively describe how the system enables that capability.
