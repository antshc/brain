import { apiResponseAdapter } from "../kit";

// Everything about the HTTP wire that a check should not know: auth headers, a base path, versioning.
// TODO(proof): add the headers a request needs (a test token read from the environment), or remove this file's headers.
export const apiResponse = apiResponseAdapter({ headers: {} });
