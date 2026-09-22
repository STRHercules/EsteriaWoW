# Esteria launcher news and announcements

News and forum announcements are optional integrations. The default build has
both URLs blank, so the launcher returns an empty news list and no forum
announcement request. This keeps the launcher usable while Esteria's web
endpoints are not configured.

## News endpoint

Set `MAIN_VITE_NEWS_URL` to an HTTPS endpoint returning:

```json
{
  "items": [
    {
      "id": "2026-09-21-launch",
      "title": "Welcome to Esteria",
      "date": "2026-09-21",
      "body": "Plain-text announcement body.",
      "author": "Esteria team",
      "url": "https://example.invalid/news/launch"
    }
  ]
}
```

`id`, `title`, `date`, and `body` are required. `author` and `url` are
optional; `url` must be an absolute URL. The launcher validates the response
and renders the body as plain text.

## Forum announcement endpoint

Set `MAIN_VITE_FORUM_URL` to an HTTPS endpoint returning one announcement:

```json
{
  "id": "welcome",
  "title": "Welcome to Esteria",
  "author": "Esteria team",
  "date": "2026-09-21",
  "url": "https://example.invalid/forum/welcome",
  "html": "<p>Welcome to Esteria.</p>"
}
```

If the URL is blank, the launcher returns `null` and the forum panel remains
empty. The endpoint should be public, fast, and served over HTTPS; no forum
backend or URL is assumed by this repository.

## Troubleshooting

- A blank panel with blank configuration is expected.
- A non-2xx response or malformed JSON is logged by the launcher and shown as
  an error state.
- Check the launcher log under `%APPDATA%\Esteria Launcher\logs` and verify
  the endpoint with `Invoke-WebRequest` before changing the client CDN.
