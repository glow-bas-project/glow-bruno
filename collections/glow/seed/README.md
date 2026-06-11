# Seed workflow

Run these requests in order from the **seed/** folder (collection runner or manually). Assumes an **empty database** (schema only).

| Step | Request | Notes |
|------|---------|-------|
| 1 | **01 — Create Restaurant** | Creates **Glow Kitchen**; sets `restaurantId` from the response |
| 2 | **02 — Create Menu Item (Burger)** | Uses `restaurantId` from step 1 when run as a collection |
| 3 | **03 — Create Menu Item (Salad)** | Same restaurant |

Set `username` and `password` in your Bruno environment before running. Collection OAuth2 (password grant) fetches a token automatically when a protected service needs it.

## Menu service

Steps 2–3 fail if `glow-menu` is not enabled in local compose (commented out by default in glow-devops). Enable it there first, or run step 1 only.

## Skipped for now

Users, cart, orders, payments — not needed for restaurant/menu UI demos.
