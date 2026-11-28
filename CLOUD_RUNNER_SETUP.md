# Free cloud runner setup for Dzen Editorial Engine

The public repository `dzen-editorial-public` hosts the scheduled GitHub Actions workflows.
The application source remains in the private repository `SitnerVS/dzen-editorial-engine`.

## Required one-time setup

Open **Settings → Secrets and variables → Actions → New repository secret** in:
https://github.com/SitnerVS/dzen-editorial-public/settings/secrets/actions

Add the following repository secrets. Copy the corresponding values from the private repository's existing secrets; never put secret values in source files, issues, or chat.

| Secret name | Required | Purpose |
|---|---:|---|
| `DZEN_SOURCE_TOKEN` | Yes | Fine-grained PAT used to checkout and update the private source repository |
| `GEMINI_API_KEY` | Yes, if Gemini is used | Primary text generation provider |
| `GROQ_API_KEY` | Yes | Fallback text generation provider |
| `TAVILY_API_KEY` | Optional | Search/source discovery |
| `WORDSTAT_OAUTH_TOKEN` | Optional | Yandex Wordstat data source |
| `DZEN_COOKIES_JSON` | Yes | Dzen authenticated session |
| `DZEN_CSRF_TOKEN` | Yes | Dzen request validation |
| `DZEN_PUBLISHER_ID` | Yes | Dzen publisher/account identifier |
| `DZEN_FP_TOKEN` | Yes | Dzen fingerprint token |
| `OSINT_TELEGRAM_NOTIFY_SECRET` | Optional but recommended | Telegram notification gateway authentication |

### Create DZEN_SOURCE_TOKEN

1. Open https://github.com/settings/personal-access-tokens/new
2. Choose **Fine-grained token**.
3. Set a descriptive name such as `dzen-editorial-public-runner`.
4. Set resource owner to `SitnerVS`.
5. Under repository access choose **Only select repositories** and select only `dzen-editorial-engine`.
6. Grant **Contents: Read and write**. Leave other repository permissions at their minimum/default values (Metadata read-only).
7. Create the token and copy it immediately into the `DZEN_SOURCE_TOKEN` secret in the public repository.
8. Do not paste the token into chat or commit it to either repository.

The token is needed because the automation saves the daily topic plan, generated articles, and publication state back to the private repository. Set a reminder to renew it before its expiration.

## Workflows

- `editorial-cloud.yml`: daily 08:00 Moscow demand analysis; hourly publication 09:00–23:00 Moscow; half-hour recovery watchdog.
- `tests-private-source.yml`: daily tests at 07:45 Moscow and manual dispatch.
- The private repository's old scheduled workflow is disabled to prevent duplicate blocked runs. Its manual dispatch remains.

## Privacy and security

This repository is public, so workflow logs and workflow definitions are publicly visible. The automation suppresses raw generator and publisher logs to reduce accidental disclosure. Do not add credentials or private article drafts to this repository. Keep all credentials in Actions repository secrets. The private application source and generated article/state files remain in `dzen-editorial-engine`.

## Billing

The scheduled workflows use GitHub-hosted runners from this public repository. Public-repository standard hosted runner usage is free under GitHub's published Actions policy. This does not require setting a paid Actions budget for the private repository.
