# sampleMCP

Model Context Protocol (MCP) の最小構成を確認できるサンプル実装です。TCP 上で JSON Lines フォーマットをやり取りし、ハンドシェイクからツール呼び出しまでの一連の流れを追跡できます。

## 目次
- [特徴](#特徴)
- [前提条件](#前提条件)
- [セットアップ/インストール手順](#セットアップインストール手順)
- [アーキテクチャ概要](#アーキテクチャ概要)
- [サンプル入出力](#サンプル入出力)
- [ツールの挙動](#ツールの挙動)
- [サーバーとクライアントの実行](#サーバーとクライアントの実行)
- [開発者向けワークフロー](#開発者向けワークフロー)
- [拡張のヒントとロードマップ](#拡張のヒントとロードマップ)

## 特徴
- ✅ JSON Lines を用いたシンプルな MCP 通信のサンプル。
- ✅ ハンドシェイク、ツール一覧取得、ツール呼び出しの典型的なフローを網羅。
- ✅ `echo` / `uppercase` という 2 種類のツールを通じてパラメータの受け渡しを確認。
- ✅ 自動テストによるクライアント・サーバー間の往復通信検証を提供。

## 前提条件
| 項目 | 内容 |
| --- | --- |
| 推奨 Python | 3.11 以上 |
| 必須ツール | `python`, `pip`, （任意で `make` や `pipx` など） |
| 動作確認済み OS | macOS, Linux（WSL を含む） |

主要な依存パッケージは以下のとおりです。

- 実行時: 標準ライブラリのみ
- 開発時: [`pytest`](https://docs.pytest.org/), [`ruff`](https://docs.astral.sh/ruff/)（任意の静的解析）

## セットアップ/インストール手順
1. 仮想環境を作成して有効化します。
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows の場合は .venv\Scripts\activate
   ```
2. 依存関係をインストールします。
   ```bash
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```
3. 依存ライブラリを更新した場合は、次のいずれかの方法で `requirements.txt` を再生成してください。
   - シンプルに固定したい場合:
     ```bash
     pip freeze --exclude-editable > requirements.txt
     ```
   - `pip-tools` を使う場合（任意）:
     ```bash
     python -m pip install pip-tools
     pip-compile requirements.in --output-file requirements.txt
     ```
   ※ このリポジトリでは開発用依存 (`pytest`, `ruff`) のみを固定しています。実行コードは標準ライブラリで動作します。

## アーキテクチャ概要
```
.
├── mcp_sample/
│   ├── client.py    # クライアント実装。サーバーに接続してツールを順に呼び出す
│   ├── protocol.py  # JSON Lines のエンコード/デコードとハンドシェイクユーティリティ
│   └── server.py    # 非同期サーバーとツールレジストリの定義
└── tests/
    └── test_integration.py  # クライアントとサーバーの往復通信テスト
```

- `protocol.py` がメッセージの共通処理を担い、`client.py` と `server.py` は同一プロトコルを共有します。
- `ToolRegistry` によりツールを簡単に差し替えられる構造になっており、拡張が容易です。

## サンプル入出力
実際の通信は JSON Lines（1 行 1 メッセージ）で行われます。以下は代表的なやり取りです。

### 1. ハンドシェイク
```jsonc
// クライアント -> サーバー
{"type": "handshake", "role": "client", "version": 1}
// サーバー -> クライアント
{"type": "handshake", "role": "server", "version": 1}
```

### 2. ツール一覧の取得
```jsonc
// クライアント -> サーバー
{"type": "request", "id": 1, "method": "list_tools"}
// サーバー -> クライアント
{
  "type": "response",
  "id": 1,
  "result": {
    "tools": [
      {"name": "echo", "description": "Echo the provided message back to the caller."},
      {"name": "uppercase", "description": "Convert the provided message to uppercase."}
    ]
  }
}
```

### 3. ツール呼び出し
```jsonc
// echo ツール
{"type": "request", "id": 2, "method": "call_tool", "params": {"name": "echo", "arguments": {"message": "Hello"}}}
{"type": "response", "id": 2, "result": {"output": "Hello"}}

// uppercase ツール
{"type": "request", "id": 3, "method": "call_tool", "params": {"name": "uppercase", "arguments": {"message": "Hello"}}}
{"type": "response", "id": 3, "result": {"output": "HELLO"}}
```

## ツールの挙動
| ツール名 | 入力例 | 出力例 | 用途 |
| --- | --- | --- | --- |
| `echo` | `{ "message": "sample" }` | `{ "output": "sample" }` | 原文そのままを返し、接続確認や単純な往復テストに利用できます。 |
| `uppercase` | `{ "message": "sample" }` | `{ "output": "SAMPLE" }` | 文字列処理の例として大文字変換を実行します。 |

## サーバーとクライアントの実行
### サーバーの起動
```bash
python -m mcp_sample.server
```
デフォルトでは `127.0.0.1:8765` で待ち受けます。

### クライアントの実行
別ターミナルで以下を実行します。
```bash
python -m mcp_sample.client --message "こんにちは"
```
サーバーからのレスポンスが JSON 形式で標準出力に表示されます。

## 開発者向けワークフロー
### テスト
```bash
pytest
```
`tests/test_integration.py` がクライアントとサーバーの往復通信を検証します。

### Lint / フォーマット
```bash
ruff check .
```
Ruff を利用してコードスタイルと潜在的なバグを検出できます。（必要に応じて `ruff format` の利用も検討してください。）

### 型チェック（任意）
標準ライブラリのみで構成されているため、`pyright` や `mypy` を導入するとより安全です。

## 拡張のヒントとロードマップ
- `ToolRegistry` に新しい関数を登録することで、追加ツールを簡単に提供できます。
- プロトコル層を `protocol.py` に切り出しているため、バージョン管理や認証ロジックの挿入が容易です。
- クライアントはリクエスト順序を固定していますが、キューや再試行ロジックを追加することで堅牢性を高められます。

今後のロードマップ（例）:
- 認証付きハンドシェイクや暗号化通信のサポート
- ロギングの構造化（JSON 形式など）
- CLI オプションの拡充（複数ツールの同時呼び出し、レスポンス保存など）
- コンテナイメージの提供や CI での自動テスト実行

---
ご意見・フィードバックは issue でお知らせください。
