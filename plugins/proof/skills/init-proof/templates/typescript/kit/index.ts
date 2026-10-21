// The proof kit: what a proof is and the receipt that records it. It knows nothing of the app or of whatever runs it:
// everything it needs (revision, surfaces, API URL, the features map, the commands to suggest) is passed in.
export * from "./types";
export * from "./surfaces";
export * from "./features";
export * from "./receipt";
export * from "./run";
export * from "./matchers";
export * from "./evidence-types";
export * from "./evidence";
export * from "./evaluate";
export * from "./logs";
export * from "./test-results";
