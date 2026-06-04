export function getParentId() {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("jaz_parent_id");
}

export function getChildId() {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("jaz_child_id");
}

export function setChildId(childId: number | string) {
  if (typeof window === "undefined") return;
  localStorage.setItem("jaz_child_id", String(childId));
}

export function getToken() {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("jaz_token");
}

export function logout() {
  localStorage.removeItem("jaz_token");
  localStorage.removeItem("jaz_parent_id");
  localStorage.removeItem("jaz_child_id");
}
