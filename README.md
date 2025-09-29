# sampleMCP

このリポジトリは、Model Context Protocol (MCP) の非常にシンプルなクライアントとサーバーのサンプル実装です。JSON Lines 形式を使った TCP 通信上でハンドシェイク・ツール一覧・ツール実行という基本的なフローを確認できます。

## 構成

```
.
├── mcp_sample/
│   ├── __init__.py
│   ├── client.py
│   ├── protocol.py
│   └── server.py
└── tests/
    └── test_integration.py
```

- `mcp_sample.server` は 2 つのツール (`echo` と `uppercase`) を公開する MCP サーバーです。
- `mcp_sample.client` はサーバーとハンドシェイクを行い、`list_tools` / `call_tool` リクエストを送信するクライアントです。
- `tests/test_integration.py` ではサーバーとクライアントの往復通信を確認します。

## 使い方

### サーバーの起動

```
python -m mcp_sample.server
```

デフォルトでは `127.0.0.1:8765` で待ち受けます。ログに接続状況が表示されます。

### クライアントの実行

別のターミナルで次を実行し、サーバーに接続します。

```
python -m mcp_sample.client --message "こんにちは"
```

サーバーからのレスポンスが JSON 形式で出力されます。

### テスト

```
pytest
```

サーバーとクライアントが正しく通信できることを確認します。
