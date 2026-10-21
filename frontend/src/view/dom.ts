const SVG_NAMESPACE = "http://www.w3.org/2000/svg";

export function byId<T extends HTMLElement | SVGElement = HTMLElement>(id: string): T {
  const element = document.getElementById(id);
  if (element === null) {
    throw new Error(`Elemen #${id} tidak ada di halaman`);
  }
  return element as T;
}

export function svgElement(
  name: string,
  attributes: Record<string, string | number>,
  text?: string,
): SVGElement {
  const element = document.createElementNS(SVG_NAMESPACE, name);
  for (const [key, value] of Object.entries(attributes)) {
    element.setAttribute(key, String(value));
  }
  if (text !== undefined) {
    element.textContent = text;
  }
  return element;
}

export function textElement<Tag extends keyof HTMLElementTagNameMap>(
  tag: Tag,
  text: string,
): HTMLElementTagNameMap[Tag] {
  const element = document.createElement(tag);
  element.textContent = text;
  return element;
}

export function showMessage(error: unknown): void {
  byId("note").textContent = error instanceof Error ? error.message : String(error);
}
