import type { TestResultAdapter } from "./kit/test-results";
import type { EvidencePolicy } from "./kit/evidence-types";

// Project-owned approval/trust boundary. Load pins from protected reviewer/CI configuration,
// outside the run folder. Never derive these values from evidence.json.
export const EVIDENCE_APP = {{APP_NAME_JSON}};
export const EVIDENCE_POLICY: EvidencePolicy = {
  revision: "", build: "", contractDigest: "", approvedAt: "", modules: [],
  tests: { report: "tests/results.xml", metadata: "tests/run.json", format: "junit",
    requiredIds: [], requiredSuites: [], allowedSkips: [] },
  async authorize(_manifest, _rawManifest) {
    // Verify an external CI attestation/signature and authorized run ID, including
    // clean final source/build, report provenance, capture completeness and scope.
    // Return true only after validation. A self-written manifest/hash is insufficient.
    return false;
  },
};

// Optional read-only parser for an approved project/Playwright JSON report schema.
export const EVIDENCE_JSON_ADAPTER: TestResultAdapter | undefined = undefined;
