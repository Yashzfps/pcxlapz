# Gmail OAuth Setup for Rias

Follow these steps once to enable email sending:

1. Go to Google Cloud Console and create/select a project.
2. Enable **Gmail API** for that project.
3. Configure OAuth consent screen (External/Internal as needed).
4. Create OAuth client credentials of type **Desktop app**.
5. Download the credentials JSON.
6. Rename it to `credentials.json` and place it in the project root:
   - `/home/runner/work/pcxlapz/pcxlapz/Yashzfps/pcxlapz/credentials.json`
7. Run:
   ```bash
   python main.py
   ```
8. Use a command like:
   `send email to user@example.com | Test Subject | Hello from Rias`
9. On first send attempt, sign in and approve permissions in browser.

Rias stores OAuth token at `data/token.json`. Do not commit credentials or token files.
