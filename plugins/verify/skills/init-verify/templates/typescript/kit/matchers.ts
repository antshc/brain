import { isDeepStrictEqual } from "node:util";

const own = (value: object, key: PropertyKey) => Object.prototype.hasOwnProperty.call(value, key);
/** Named properties only. Arrays remain exact; use containsItem for membership. */
export function matchesFields(actual: unknown, expected: unknown): boolean {
  if (expected === null || typeof expected !== "object" || Array.isArray(expected)) return isDeepStrictEqual(actual, expected);
  if (actual === null || typeof actual !== "object" || Array.isArray(actual)) return false;
  return Object.keys(expected).every(key => own(actual, key) && matchesFields(
    (actual as Record<string, unknown>)[key], (expected as Record<string, unknown>)[key]));
}
export function containsItem(items: readonly unknown[], subset: unknown): boolean {
  if (!Array.isArray(items)) throw new Error("Expected a collection");
  return items.some(item => matchesFields(item, subset));
}
export type CountBounds = { equals?: number; min?: number; max?: number };
export function countMatches<T>(items: readonly T[], predicate: (item: T) => boolean, bounds: CountBounds): boolean {
  if (!Array.isArray(items) || !Object.keys(bounds).length || Object.keys(bounds).some(k => !["equals", "min", "max"].includes(k)) ||
    Object.values(bounds).some(n => !Number.isSafeInteger(n) || n < 0) ||
    (bounds.equals !== undefined && (bounds.min !== undefined || bounds.max !== undefined)) ||
    (bounds.min !== undefined && bounds.max !== undefined && bounds.min > bounds.max)) throw new Error("Invalid count bounds");
  const n = items.filter(predicate).length;
  return (bounds.equals === undefined || n === bounds.equals) && (bounds.min === undefined || n >= bounds.min) && (bounds.max === undefined || n <= bounds.max);
}
export function fieldSatisfies(actual: unknown, path: readonly string[], predicate: (value: unknown) => boolean): boolean {
  if (!path.length || path.some(k => !k || ["__proto__", "prototype", "constructor"].includes(k))) throw new Error("Unsafe field path");
  let value = actual;
  for (const key of path) {
    if (value === null || typeof value !== "object" || !own(value, key)) return false;
    value = (value as Record<string, unknown>)[key];
  }
  return predicate(value);
}
