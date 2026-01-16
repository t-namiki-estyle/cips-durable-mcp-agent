<div id="top"></div>

# Durable Mcp Agent

<div align="left">

![Python Version][python-badge]

</div>

[python-badge]: https://img.shields.io/badge/python-3.11-blue

伊藤忠チームでAzure Durable FunctionsとMCPを用いてAgentを動作させるためのリポジトリです。
エージェント側の動作ロジックと各案件で使用するエージェントの設定が、すべてここに集約されています。

## 目次

1. [エージェントのアーキテクチャ概要](#エージェントのアーキテクチャ概要)
2. [開発環境構築](#開発環境構築)
3. [エージェント一覧](#エージェント一覧)

## エージェントのアーキテクチャ概要

![システムアーキテクチャ図](.github/assets/伊藤忠生成AIプロジェクト_システムアーキ.jpg)

## 開発環境構築

### `azurite`のインストール

[ローカルでの Azure Storage の開発に Azurite エミュレーターを使用する](https://learn.microsoft.com/ja-jp/azure/storage/common/storage-use-azurite?tabs=npm%2Cblob-storage)を参照してインストールしてください。

### Python 3.11の用意

Python 3.11が使用できるか確認してください。

```zsh
python -V
```

### ローカル実行用の仮想環境の構築

```zsh
python3.11 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

開発やローカルデバッグに関しては、[CONTRIBUTING.md](.github/CONTRIBUTING.md)を参照してください。

## エージェント一覧

<!-- 以下はサンプルです。
### エージェントの名前

ここにエージェントの概要とその案件を記載します。個別案件で使用するわけではない場合は、汎用エージェントとしてください。

#### 設定ファイル: `{name}_config.py`

#### モード: {mode}名を記載

#### 履歴

- 20XX-XX-XX: 作成
- 20XX-XX-XX: エージェント本体のプロンプトを変更

---
-->

### ReAct Agent

シンプルなReAct推論を実行するエージェントです

#### 設定ファイル: `default_config.py`

#### モード: `default`

#### 履歴

- 2025-05-02: 作成

---

### Deep Research Agent

Deep Research機能の汎用エージェントです。

#### 設定ファイル: `research_config.py`

#### モード: `research`

#### 履歴

- 2025-05-15 作成

---

### Sales Enquiry Agent

営業問い合わせ支援用のDBを検索するエージェントです。

#### 設定ファイル: `panel_sales_enquiry_config.py`

#### モード: `panel_sales_enquiry`

#### 履歴

- 2025-06-04 作成

---

### Audit Precheck Agent

監査予備調査機能用のDB検索並びにWeb検索を行うエージェントです。

#### 設定ファイル: `audit_precheck_config.py`

#### モード: `audit_precheck`

#### 履歴

- 2025-06-06 作成

---

### IRL Agent

IRL（伊藤忠リーテイルリンク株式会社）様特化エージェントです。Gemini検索と取引実績情報をもとにメーカーリストを回答します。

#### 設定ファイル: `irl_config.py`

#### モード: `irl`

#### 履歴

- 2025-06-09 作成

---

### Plastic Agent

プラスチックの原料のTDSと生産メーカーのキャパシティのデータを検索して回答するエージェントです。

#### 設定ファイル: `plastic_config.py`

#### モード: `plastic`

#### 履歴

- 2025-06-20 作成

---

### Tariff Agent

関税情報取得エージェントです。Gemini検索でHSコードを特定し、TradeCompassAPIを使用して関税情報を取得します。

#### 設定ファイル: `tariff_config.py`

#### モード: `tariff`

#### 履歴

- 2025-06-24 作成

---

### Plastic IRL Integrated Agent

以下の２つのエージェント機能を統合したエージェントです。
1. プラスチックエージェント
  プラスチックの原料のTDSと生産メーカーのキャパシティのデータを検索して回答します。
2. IRL（伊藤忠リーテイルリンク株式会社）様特化エージェント
  Gemini検索と取引実績情報をもとにメーカーリストを回答します。

#### 設定ファイル: `plastic_agent_config.py`

#### モード: `plastic_agent`

#### 履歴

- 2025-08-14 作成

---

### Company Information Investment Agent

ユーザーの入力から調査対象企業を1社に特定し、詳細調査エージェント（Company Research Investment Agent）に引き継ぐエージェントです。企業名が曖昧な場合は具体的な企業名を求め、企業検索で候補を特定し、法人番号と企業情報の確認を行います。

#### 設定ファイル: `company_info_config.py`

#### モード: `company_info`

#### 履歴

- 2025-09-02: 作成
- 2025-10-14: 更新

---

### Company Research Investment Agent

企業の投資調査を担当するエキスパートエージェントです。Company Information Investment Agentから引き継いだ企業情報をもとに、企業の投資価値を総合的に調査・分析し、意思決定に必要な情報をExcel形式でレポートとして提供します。


#### 設定ファイル: `company_research_config.py`

#### モード: `company_research`

#### 履歴

- 2025-10-14: 作成

<p align="right"><a href="#top">このページのトップへ</a></p>