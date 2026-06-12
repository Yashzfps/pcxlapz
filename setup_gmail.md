# Gmail Setup for Rias

1. Open [Google Cloud Console](https://console.cloud.google.com/) and create a project.
2. Enable the **Gmail API** for that project.
3. Configure OAuth consent screen (External is fine for personal use).
4. Create OAuth credentials of type **Desktop app**.
5. Download the JSON file and place it at:
   - `/home/runner/work/pcxlapz/pcxlapz/Yashzfps/pcxlapz/credentials.json`
6. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
7. Run the assistant:
   ```bash
   python main.py
   ```
8. Send email with:
   ```text
   send email to recipient@example.com | Subject | Message
   ```
9. On first send, a browser opens for OAuth login and `token.json` is generated automatically.

Never commit `credentials.json` or `token.json`.
