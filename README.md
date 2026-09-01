# ゲーム業界ニュース Discord自動配信

パソコンを起動していなくても、GitHub Actionsが1日4回(JST 8:00 / 12:00 / 18:00 / 21:00)自動でゲーム業界のニュースを収集し、Discordチャンネルに配信します。

- 国内メディア: 4Gamer, AUTOMATON, Game*Spark, INSIDE
- 海外メディア(自動翻訳): IGN, GameSpot, PC Gamer, Eurogamer, Polygon
- セキュリティ/データ流出系: Google Newsのキーワード検索(情報漏えい・不正アクセス・data breach 等)

要約は120文字程度に短くまとめ、海外記事は無料の翻訳API([MyMemory](https://mymemory.translated.net/))で日本語化します。無料APIのため、機械翻訳特有の多少の不自然さや、まれに翻訳できず原文のまま届くことがあります。

## セットアップ手順

### 1. Discord Webhook URLを発行する

1. Discordでニュースを流したいチャンネルの「チャンネルの編集」→「連携サービス」→「ウェブフック」を開く
2. 「新しいウェブフック」を作成し、名前を設定
3. 「ウェブフックURLをコピー」でURLを控える(他人に共有しないこと)

### 2. GitHubリポジトリを作成してpushする

このフォルダ(`discord-game-news`)をGitHubリポジトリとして作成し、pushしてください。

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<あなたのユーザー名>/<リポジトリ名>.git
git push -u origin main
```

### 3. Webhook URLをSecretsに登録する

1. GitHubのリポジトリページで `Settings` → `Secrets and variables` → `Actions` を開く
2. `New repository secret` をクリック
3. Name: `DISCORD_WEBHOOK_URL`、Secret: 手順1で控えたURLを入力して保存

### 4. Actionsを有効化して動作確認する

1. リポジトリの `Actions` タブを開き、ワークフローを有効化する
2. `Game News to Discord` ワークフローを選択し、`Run workflow` で手動実行してテストする
3. Discordチャンネルにニュースが届けば成功

以降は `cron` の設定に従い、1日4回自動的にニュースが配信されます。

## カスタマイズ

- **配信頻度・時刻を変える**: [.github/workflows/news.yml](.github/workflows/news.yml) の `cron` を編集(UTC基準。JSTはUTC+9)
- **ニュースソースを追加/削除する**: [scripts/sources.py](scripts/sources.py) の `FEEDS` リストを編集(RSSのURLと `category`(`japan`/`overseas`/`security`)、`lang`(`ja`/`en`)を指定)
- **1回あたりの最大配信件数・要約の長さを変える**: [scripts/main.py](scripts/main.py) の `MAX_ARTICLES_PER_RUN` / `SUMMARY_MAX_LEN`

## ローカルでの動作確認

```bash
pip install -r requirements.txt
cd scripts
python main.py --dry-run   # Discordには送信せず、収集・翻訳・要約の結果をコンソールに表示
```

実際にDiscordへ送信して確認する場合は、環境変数 `DISCORD_WEBHOOK_URL` を設定してから `--dry-run` なしで実行してください。

```bash
# PowerShellの例
$env:DISCORD_WEBHOOK_URL = "取得したWebhook URL"
python main.py
```

## 仕組み

- 送信済み記事のURLは [data/sent_articles.json](data/sent_articles.json) に記録し、重複配信を防ぎます(30日以上前の記録は自動削除)
- Discord Webhook URLはコードに直接書かず、GitHub Secretsからのみ読み込みます
- 1つのニュースソースの取得に失敗しても、他のソースの処理は継続します
