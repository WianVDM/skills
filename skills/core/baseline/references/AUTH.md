# Authentication Handling

Many baselines require navigating an authenticated page. The `baseline` skill should handle auth when credentials or session state are available, and ask the user otherwise.

---

## Auth methods

| Method | When to use | Persistence |
|--------|-------------|-------------|
| **none** | Page is public | Nothing |
| **existing-session** | User already signed in via browser profile | Nothing |
| **session-file** | User signs in once, skill saves session | Save cookies/localStorage to `{context_dir}/baseline/sessions/` |
| **env-vars** | Credentials available as environment variables | Reference env var names only |
| **manual** | No safe persistence option | Ask user each time |

---

## Recommended flow

1. Navigate to the target page using the selected verification method.
2. Check whether the page appears authenticated (e.g., expected element present, no redirect to login).
3. If authenticated, proceed.
4. If not authenticated, check `preferences.auth.method`.
5. If `auth.method` is unset, ask the user:

> "This page requires authentication. I can:
> 1. Use an existing browser session
> 2. Save a session after you sign in manually
> 3. Use credentials from environment variables
> 4. Ask you to sign in each time
> Which do you prefer?"

6. Persist the choice.
7. Authenticate using the chosen method.
8. Save session state if applicable.

---

## Session files

Session files store cookies and localStorage so the skill can restore an authenticated state on the next run.

### Location

```text
{context_dir}/baseline/sessions/
├── default.json
└── {ticket-key}.json
```

Use a per-project default session unless different tickets require different users or roles. Use per-ticket sessions when roles differ.

### Contents

A session file should include:

- Cookies relevant to the target domain.
- LocalStorage entries required for auth.
- Optional: sessionStorage entries.

### Freshness

Re-authenticate if the session file is older than 7 days or if authentication fails. Update the `verified_at` timestamp in notes when refreshing.

---

## Env-var credentials

If the user chooses env-var credentials, store only the env var names, never the values:

```yaml
auth:
  method: env-vars
  username_env: AUTH_USERNAME
  password_env: AUTH_PASSWORD
```

The skill reads the values at runtime and uses them to authenticate. This keeps secrets out of config files.

---

## Security notes

- **Never store plaintext passwords or tokens in `{config_dir}/baseline.yaml`.**
- Prefer session files over credentials.
- Prefer env-var references over plaintext credentials.
- If credentials must be stored, warn the user and restrict file permissions.
- Do not commit session files or credential files to version control unless the project explicitly allows it.

---

## Notes examples

```yaml
notes:
  - text: "Auth session persisted to baseline/sessions/default.json after manual sign-in."
    category: workaround
  - text: "User prefers manual sign-in over env-var credentials for staging environments."
    category: preference
  - text: "Session files expire after 7 days; re-authenticate when stale."
    category: gotcha
```
