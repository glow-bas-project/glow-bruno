# Glow Bruno collection — agent conventions

This repo is an [OpenCollection](https://docs.usebruno.com/opencollection-yaml/structure-reference) workspace for the Glow microservices API. Follow these rules when adding, editing, or removing requests.

## Collection layout

- Root collection: `collections/glow/`
- One folder per service: `restaurant`, `user`, `order`, `cart`, `courier`, `payment`, `menu`, `seed`
- Each folder has `folder.yml` (`info.type: folder`, `request.auth: inherit`)
- Request files are sibling `*.yml` files (kebab-case names, e.g. `get-restaurant-by-id.yml`, `create-order.yml`)

## OpenCollection request shape

```yaml
info:
  name: Human-readable title
  type: http
  seq: 1
http:
  method: GET
  url: "{{restaurantServiceUrl}}/restaurants/:id"
  params:
    - name: id
      value: ""
      type: path
  auth: inherit
```

Optional top-level keys: `runtime`, `docs`. Use `info.type: http` for requests.

## URLs and environments

Never hardcode hosts. Use service URL variables:

| Variable | Resolves to |
|----------|-------------|
| `restaurantServiceUrl` | `{{baseUrl}}/api/restaurant` |
| `userServiceUrl` | `{{baseUrl}}/api/user` |
| `orderServiceUrl` | `{{baseUrl}}/api/order` |
| `cartServiceUrl` | `{{baseUrl}}/api/cart` |
| `courierServiceUrl` | `{{baseUrl}}/api/courier` |
| `paymentServiceUrl` | `{{baseUrl}}/api/payment` |
| `menuServiceUrl` | `{{baseUrl}}/api/menu` |

`.gitignore` blocks `.env*` and `*.secrets.yml` under environments.

Switch environment (`local`, `staging`, `prod`) to change target stack without editing requests.

## Authentication

Collection-level OAuth 2.0 (password grant) in `opencollection.yml`:

- Token URL: `{{authServerUrl}}/realms/{{realm}}/protocol/openid-connect/token`
- Client: `{{oauthClientId}}` (public client, credentials in body)
- User: `{{username}}` / `{{password}}` from the environment
- `settings.autoFetchToken: true` — Bruno fetches a token before protected requests

Environment files hold auth metadata (`authServerUrl`, `realm`, `oauthClientId`) and empty credential placeholders — not secret values, not request bodies, not entity IDs.

Developers create their own Keycloak user in `glow-realm` (with **CUSTOMER** role) and set credentials in Bruno only.

Run `./.githooks/install.sh` once after clone. A git **clean filter** strips credentials, IDs, and filled path params on **`git add`** (working tree unchanged). Pre-commit runs gitleaks on staged content as a backstop.

## Path parameters

- Use Postman-style segments in the URL: `:id`, `:userId`, `:restaurantId`
- Declare each URL segment in `http.params` with `type: path` and an empty default
- Do not embed literal UUIDs in URLs
- Do not store entity IDs in environment files

Body JSON IDs use an empty string in `http.body.data` (edit in the request body) or `{{name}}` with `bru.setVar` in seed steps — not path params, not environment variables.

## Request bodies

- Put full JSON in `http.body.data` with literal demo values
- Do not pull body fields from environment variables
- Add `Content-Type: application/json` on POST/PUT with JSON bodies
- Align shapes with Java request records under `$GLOW_HOME/*/src/main/java/**/application/api/model/`

## Adding a request

1. Read the controller: `$GLOW_HOME/<service>/src/main/java/**/application/api/*Controller.java`
2. Pick the matching folder under `collections/glow/`
3. Create a new kebab-case `.yml` file
4. Set `info.seq` (order within the folder)
5. Match method, path (after Traefik strip prefix), params, and body to the Java API

## Removing a request

Delete the `.yml` file. Renumber `info.seq` if needed. If `seed/` referenced the request, update those steps in the same change.

## Changing a request used by seed

When editing a request that `seed/` calls, update the corresponding `seed/` step in the same change. Keep inline demo data semantically similar unless you intentionally change the baseline.

## Source of truth

- Routes: `$GLOW_HOME/*/src/main/java/**/application/api/*Controller.java`
- Request models: `$GLOW_HOME/*/src/main/java/**/application/api/model/`
- Local routing prefixes: `$GLOW_HOME/glow-devops/compose/docker-compose.yml` (Traefik `PathPrefix`)
