from __future__ import annotations

from proof.kit import Contract, EvaluationKit, contains_item, matches_fields
from proof.kit.logs import JsonLinesAdapter, LogView
from proof.kit.test_results import JUnitAdapter, check_results

# Approve these values and required IDs before feature implementation.
VPG_NAME = 'TestVpg'
VM_NAME = 'TestVm'
# Set to False only when the application has no suitable read API. Never retry DB after API failure.
HAS_READ_API = True
RESOURCE = 'api/get-vpg.json' if HAS_READ_API else 'db/vpg.json'
CHECKS = ('vpg: persisted', 'vpg: VM present', 'vpg: task succeeded', 'vpg: refreshed list',
          'vpg: browser request', 'vpg: clean console', 'vpg: created event',
          'tests: no failures', 'tests: expected skips')
ARTIFACTS = (RESOURCE, 'tasks/create-vpg.json', 'browser/vpg-list.json', 'browser/vpg-list.png',
             'browser/request.json', 'browser/console.json', 'logs/application.jsonl',
             'tests/results.xml', 'tests/run.json')


def prove(kit: EvaluationKit) -> None:
    evidence = kit.evidence
    resource = evidence.json(RESOURCE)
    kit.check('vpg: persisted', matches_fields(resource, {'name': VPG_NAME}), True, f'See {RESOURCE}')
    kit.check('vpg: VM present', contains_item(resource['vms'], {'name': VM_NAME}), True)
    kit.check('vpg: task succeeded', matches_fields(evidence.json('tasks/create-vpg.json'),
        {'state': 'Succeeded', 'resourceId': resource['id']}), True)
    ui = evidence.json('browser/vpg-list.json')
    kit.check('vpg: refreshed list', matches_fields(ui, {'reloaded': True}) and
        contains_item(ui['rows'], {'id': resource['id'], 'name': VPG_NAME}), True, 'See browser/vpg-list.png')
    kit.check('vpg: browser request', matches_fields(evidence.json('browser/request.json'),
        {'method': 'POST', 'path': '/vpgs', 'body': {'name': VPG_NAME}}), True)
    # Completeness/scope comes from the manifest, not the absence of messages alone.
    kit.check('vpg: clean console', evidence.json('browser/console.json')['errors'], [])
    logs = LogView(JsonLinesAdapter().parse(evidence.text('logs/application.jsonl'), 'logs/application.jsonl'),
                   correlation_id=evidence.run_id)
    kit.check('vpg: created event', logs.event_exists('VpgCreated', {'vpgName': VPG_NAME}), True)
    check_results(kit, 'tests/results.xml', 'tests/run.json', JUnitAdapter(), required_ids=('vpg.create',))


CONTRACTS = {'vpg-create': Contract(prove, CHECKS, ARTIFACTS, ('web', 'api'))}
