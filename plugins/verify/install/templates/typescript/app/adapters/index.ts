import type { EvidenceAdapter } from "../kit";
// <surface: api>
import { apiResponse } from "./api";
// </surface: api>

// Evidence sources this repo adds to the kit's (dom-assertion, screenshot, api-response, network, console, storage).
// A source with the same id replaces the kit's. Add a database, log or test-result adapter here, then name it in a map's proof clause.
export const ADAPTERS: EvidenceAdapter[] = [
  // <surface: api>
  apiResponse,
  // </surface: api>
];
