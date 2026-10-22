// The proof kit: what a proof is (features, scenarios, flows, checks, evidence) and the receipt that records it. It knows nothing
// of the app or of whatever runs it: everything it needs (revision, surfaces, API URL, the artifact store, the maps) is passed in.
export * from "./types";
export * from "./surfaces";
export * from "./evidence";
export * from "./features";
export * from "./map";
export * from "./receipt";
export * from "./run";
