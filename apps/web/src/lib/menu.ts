/**
 * Role-based menu visibility (menu hiding only — the API enforces every
 * permission server-side). Role names are the seeded role names from the
 * RBAC table in BUILD_PLAN.md.
 */

export interface MenuItem {
  href: string;
  label: string;
  /** "all" = every authenticated role; otherwise the roles that see the item. */
  roles: "all" | string[];
}

export const MENU_ITEMS: MenuItem[] = [
  { href: "/dashboard", label: "Dashboard", roles: "all" },
  { href: "/branches", label: "Branches", roles: "all" },
  {
    href: "/users",
    label: "Users",
    roles: ["Super Admin", "Branch Admin", "Viewer / Auditor"],
  },
  { href: "/masters", label: "Masters", roles: "all" },
  { href: "/settings", label: "Settings", roles: "all" },
  {
    href: "/audit",
    label: "Audit Log",
    roles: [
      "Super Admin",
      "Branch Admin",
      "Medical Officer",
      "Lab In-charge",
      "Viewer / Auditor",
    ],
  },
];

export function visibleMenuItems(role: string | null): MenuItem[] {
  if (!role) return [];
  return MENU_ITEMS.filter(
    (item) => item.roles === "all" || item.roles.includes(role),
  );
}

export function canSee(role: string | null, href: string): boolean {
  return visibleMenuItems(role).some((item) => item.href === href);
}
