# Dependencies

## Required skills

- `pr-adapter-contract` — adapter interface contract.
- `worker-contract` — return contract format.
- `token-resolver` — token resolution.

## Required environment

- Network access to the SonarCloud API.
- Python 3.x or equivalent for API calls.

## Environment variables

The token is resolved by `token-resolver`. Commonly referenced:

- `SONAR_TOKEN`
- `SONARQUBE_TOKEN`
- `SONARCLOUD_TOKEN`
