import { matchesFields, countMatches, type CountBounds } from "./matchers";
const time = (value: string) => {
  const n = Date.parse(value);
  if (!Number.isFinite(n)) throw new Error("Invalid log timestamp");
  return n;
};
export type LogRecord = { timestamp: string; level: string; event?: string; template?: string; message?: string; traceId?: string; correlationId?: string; fields: Record<string, unknown>; source: string; offset: number };
export interface LogAdapter { parse(input: string, source: string): LogRecord[] }
export type LogScope = { complete: boolean; correlationId?: string; traceId?: string; start?: string; end?: string };
function record(value: any, source: string, offset: number): LogRecord {
  if (!value || typeof value !== "object" || typeof value.timestamp !== "string" || typeof value.level !== "string" || !value.fields || typeof value.fields !== "object" || Array.isArray(value.fields)) throw new Error("Invalid normalized log record");
  time(value.timestamp);
  if (!/^(trace|debug|info|information|warn|warning|error|fatal|critical|verbose)(?:[0-9]+)?$/i.test(value.level)) throw new Error("Unknown log severity");
  return { ...value, source, offset };
}
export class JsonlLogAdapter implements LogAdapter {
  parse(input: string, source: string): LogRecord[] {
    return input.split(/\r?\n/).flatMap((line, offset) => line.trim() ? [record(JSON.parse(line), source, offset)] : []);
  }
}
function otelValue(value: any): unknown {
  for (const key of ["stringValue", "boolValue", "doubleValue"]) if (key in value) return value[key];
  if ("intValue" in value) { const n = Number(value.intValue); if (!Number.isSafeInteger(n)) throw new Error("Unsafe OTel integer"); return n; }
  if (value.arrayValue) return (value.arrayValue.values ?? []).map(otelValue);
  if (value.kvlistValue) return attributes(value.kvlistValue.values ?? []);
  throw new Error("Unsupported OTel value");
}
function attributes(values: any[]): Record<string, unknown> {
  const pairs = values.map(a => [a.key, otelValue(a.value)] as const);
  if (pairs.some(([k]) => typeof k !== "string") || new Set(pairs.map(([k]) => k)).size !== pairs.length) throw new Error("Invalid OTel attributes");
  return Object.fromEntries(pairs);
}
export class OtelLogAdapter implements LogAdapter {
  parse(input: string, source: string): LogRecord[] {
    const data = JSON.parse(input);
    if (!Array.isArray(data.resourceLogs)) throw new Error("Invalid OTel export");
    let offset = 0;
    return data.resourceLogs.flatMap((resource: any) => {
      if (!Array.isArray(resource.scopeLogs)) throw new Error("Missing OTel scope logs");
      return resource.scopeLogs.flatMap((scope: any) => {
        if (!Array.isArray(scope.logRecords)) throw new Error("Missing OTel records");
        return scope.logRecords.map((r: any) => {
          const fields = attributes(r.attributes ?? []);
          const level = r.severityText ?? (Number(r.severityNumber) >= 17 ? "ERROR" : Number(r.severityNumber) >= 13 ? "WARN" : "INFO");
          if (Number(r.severityNumber) >= 17 && !/^(error|fatal|critical)(?:[0-9]+)?$/i.test(level)) throw new Error("Conflicting OTel severity");
          return record({ timestamp: new Date(Number(BigInt(r.timeUnixNano) / 1000000n)).toISOString(), level,
            event: fields["event.name"], fields, message: r.body ? String(otelValue(r.body)) : undefined,
            traceId: r.traceId, correlationId: fields["correlation.id"] }, source, offset++);
        });
      });
    });
  }
}
/** The regex is project-reviewed policy, never taken from captured logs. Bound input before matching. */
export class TextLogAdapter implements LogAdapter {
  constructor(private readonly parseLine: (line: string) => Omit<LogRecord, "source" | "offset">) {}
  parse(input: string, source: string): LogRecord[] {
    return input.split(/\r?\n/).flatMap((line, offset) => line.trim() ? [record(this.parseLine(line), source, offset)] : []);
  }
}
const scopes = new WeakSet<readonly LogRecord[]>();
export type ScopedLogs = readonly LogRecord[] & { readonly __scopedLogs: unique symbol };
function requireScope(records: readonly LogRecord[]): asserts records is ScopedLogs {
  if (!scopes.has(records)) throw new Error("Use scopedLogs with complete capture before checking logs");
}
export function scopedLogs(records: readonly LogRecord[], scope: LogScope): ScopedLogs {
  if (scope.complete !== true || (!scope.correlationId && !scope.traceId && !(scope.start && scope.end)) ||
    (!!scope.start !== !!scope.end) || (scope.start && scope.end && time(scope.start) > time(scope.end))) throw new Error("Incomplete/unscoped log capture");
  const selected = records.filter(r => (!scope.correlationId || r.correlationId === scope.correlationId) && (!scope.traceId || r.traceId === scope.traceId) &&
    (!scope.start || time(r.timestamp) >= time(scope.start)) && (!scope.end || time(r.timestamp) <= time(scope.end)));
  scopes.add(selected);
  return Object.freeze(selected) as unknown as ScopedLogs;
}
export const logs = {
  eventExists(records: ScopedLogs, event: string, fields: Record<string, unknown> = {}) {
    requireScope(records); return records.some(r => r.event === event && matchesFields(r.fields, fields));
  },
  fieldsMatch: (record: LogRecord, fields: Record<string, unknown>) => matchesFields(record.fields, fields),
  noErrors(records: ScopedLogs, allowed: (r: LogRecord) => boolean = () => false) {
    requireScope(records); return records.every(r => !/^(error|fatal|critical)(?:[0-9]+)?$/i.test(r.level) || allowed(r));
  },
  count(records: ScopedLogs, event: string, bounds: CountBounds) {
    requireScope(records); return countMatches(records, r => r.event === event, bounds);
  },
  messageContains(records: ScopedLogs, query: string | RegExp) {
    requireScope(records);
    return records.some(r => {
      const message = r.message ?? r.template ?? "";
      if (message.length > 16384) throw new Error("Legacy log message too long");
      if (typeof query === "string") return message.includes(query);
      query.lastIndex = 0;
      return query.test(message);
    });
  },
};
