- [ ] set up a webhook receiver:
  - use Flask to listen for GitHub webhook events on `/gh-webhook`
  - check for any file changes under `/servermap/` in `added`, `modified`, or `removed`

- [ ] on webhook ping (if `/servermap` changed):
  - notify console (or log) that config has changed
  - queue an internal sync or send a message (no auto-apply yet)

- [ ] host webhook server alongside Discord.py bot:
  - run both Flask and Discord bot in the same Python process using threading
  - expose webhook server with ngrok or public HTTPS endpoint for GitHub

- [ ] document how to add the webhook to the GitHub repo
