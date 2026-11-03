export function toGameText(value, limit = 240) {
  return String(value ?? "")
    .replace(/[\r\n\t]/g, " ")
    .replace(/[\u0000-\u001f\u007f]/g, "")
    .replace(/[\u{10000}-\u{10ffff}]/gu, "")
    .replace(/\|/g, "")
    .trim()
    .slice(0, limit);
}

export function fromGameText(value, limit = 500) {
  return String(value ?? "")
    .replace(/\|H[^|]*\|h([^|]*)\|h/g, "$1")
    .replace(/\|T[^|]*\|t/g, "")
    .replace(/\|c[0-9a-fA-F]{8}|\|r/g, "")
    .replace(/[\r\n\t]/g, " ")
    .replace(/[\u0000-\u001f\u007f]/g, "")
    .trim()
    .slice(0, limit);
}
