from __future__ import annotations

from proof.kit import Contract, EvaluationKit, contains_item, matches_fields
from proof.kit.logs import JsonLinesAdapter, LogView
from proof.kit.test_results import JUnitAdapter, check_results

# Approve these values and required IDs before feature implementation.
ORDER_NUMBER = 'ORD-1001'
PRODUCT_SKU = 'SKU-COFFEE'
# Set to False only when the application has no suitable read API. Never retry DB after API failure.
HAS_READ_API = True
RESOURCE = 'api/get-order.json' if HAS_READ_API else 'db/order.json'
CHECKS = ('order: persisted', 'order: item present', 'order: task succeeded', 'order: refreshed list',
          'order: browser request', 'order: clean console', 'order: created event',
          'tests: no failures', 'tests: expected skips')
ARTIFACTS = (RESOURCE, 'tasks/create-order.json', 'browser/order-list.json', 'browser/order-list.png',
             'browser/request.json', 'browser/console.json', 'logs/application.jsonl',
             'tests/results.xml', 'tests/run.json')


def prove(kit: EvaluationKit) -> None:
    evidence = kit.evidence
    resource = evidence.json(RESOURCE)
    kit.check('order: persisted', matches_fields(resource, {'orderNumber': ORDER_NUMBER}), True, f'See {RESOURCE}')
    kit.check('order: item present', contains_item(resource['items'], {'sku': PRODUCT_SKU, 'quantity': 2}), True)
    kit.check('order: task succeeded', matches_fields(evidence.json('tasks/create-order.json'),
        {'state': 'Succeeded', 'resourceId': resource['id']}), True)
    ui = evidence.json('browser/order-list.json')
    kit.check('order: refreshed list', matches_fields(ui, {'reloaded': True}) and
        contains_item(ui['rows'], {'id': resource['id'], 'orderNumber': ORDER_NUMBER}), True, 'See browser/order-list.png')
    kit.check('order: browser request', matches_fields(evidence.json('browser/request.json'),
        {'method': 'POST', 'path': '/orders', 'body': {'items': [{'sku': PRODUCT_SKU, 'quantity': 2}]}}), True)
    # Completeness/scope comes from the manifest, not the absence of messages alone.
    kit.check('order: clean console', evidence.json('browser/console.json')['errors'], [])
    logs = LogView(JsonLinesAdapter().parse(evidence.text('logs/application.jsonl'), 'logs/application.jsonl'),
                   correlation_id=evidence.run_id)
    kit.check('order: created event', logs.event_exists('OrderCreated', {'orderNumber': ORDER_NUMBER}), True)
    check_results(kit, 'tests/results.xml', 'tests/run.json', JUnitAdapter(), required_ids=('order.create',))


CONTRACTS = {'order-create': Contract(prove, CHECKS, ARTIFACTS, ('web', 'api'))}
