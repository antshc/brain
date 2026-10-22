from __future__ import annotations

from proof.kit import Assessment, Observations, ProofCheck
# <surface: web>
from proof.kit import NetworkLog
# </surface: web>
# <surface: api>
from proof.kit import ApiResponse
# </surface: api>


# Observes only: reads the evidence the runner captured for this check and judges it. It never navigates or mutates.
def app_answers() -> ProofCheck:
    def assess(observed: Observations) -> Assessment:
        answers: list[bool] = []
        statuses: list[int] = []
        # <surface: web>
        pages = [entry["status"] for entry in observed["network-log"]["responses"] if entry["resource"] == "document"]
        statuses.extend(pages)
        answers.append(bool(pages))
        answers.extend(0 < status < 400 for status in pages)
        # </surface: web>
        # <surface: api>
        status = observed["api-response"]["status"]
        statuses.append(status)
        answers.append(0 < status < 500)
        # </surface: api>
        return Assessment(bool(answers) and all(answers), "the page loads below 400 and the API answers below 500", statuses, "The app did not answer well. Is the app up and the build fresh?")

    return ProofCheck(
        "app-answers",
        (
            # <surface: web>
            NetworkLog(),
            # </surface: web>
            # <surface: api>
            ApiResponse("/"),
            # </surface: api>
        ),
        assess,
    )
