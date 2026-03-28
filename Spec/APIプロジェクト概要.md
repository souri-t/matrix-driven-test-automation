# RamenTicketApi.csproj仕様

このドキュメントは、`src/RamenTicketApi/RamenTicketApi.csproj` の現在設定を基準に、
プロジェクト構成とアプリ機能仕様（TicketService）を定義します。

## 1. プロジェクトファイル仕様

### 1.1 基本情報

- 対象ファイル: `src/RamenTicketApi/RamenTicketApi.csproj`
- SDK: `Microsoft.NET.Sdk.Web`
- プロジェクト種別: ASP.NET Core Web API

### 1.2 ビルド設定

- TargetFramework: `net8.0`
- Nullable: `enable`
- ImplicitUsings: `enable`

### 1.3 パッケージ依存

- `Microsoft.AspNetCore.OpenApi` `8.0.7`
- `Swashbuckle.AspNetCore` `6.4.0`

### 1.4 ファイル運用方針

- `RamenTicketApi.csproj` は固定名の作業用JSON（例: `testcases/purchase_matrix.json`）を
	Content として参照しない。
- テストケース入力は、`testcases/testcase_*.json` の運用に統一する。

## 2. アプリ機能仕様（TicketService）

### 2.1 対象

- クラス名: `RamenTicketApi.Services.TicketService`
- 対象メソッド: `string? ResolveExpected(TicketRequest request)`
- 入力モデル: `RamenTicketApi.Models.TicketRequest`

### 2.2 目的

- スープ種別、麺の太さ、麺の量の組み合わせに応じて、対応する食券番号を返す。

### 2.3 入力仕様

`TicketRequest` は次の3項目を持つ。

- `Soup`（文字列）
- `NoodleThickness`（文字列）
- `NoodleAmount`（文字列）

想定される有効値:

- `Soup`: `塩`, `醤油`, `味噌`
- `NoodleThickness`: `細麺`, `太麺`
- `NoodleAmount`: `普通`, `大盛り`

### 2.4 出力仕様

- 戻り値型: `string?`
- 有効な組み合わせの場合: `食券1`〜`食券12` のいずれかを返す。
- 有効な組み合わせに一致しない場合: `null` を返す。

### 2.5 判定ルール

| Soup | NoodleThickness | NoodleAmount | 戻り値 |
| --- | --- | --- | --- |
| 塩 | 細麺 | 普通 | 食券1 |
| 塩 | 細麺 | 大盛り | 食券2 |
| 塩 | 太麺 | 普通 | 食券3 |
| 塩 | 太麺 | 大盛り | 食券4 |
| 醤油 | 細麺 | 普通 | 食券5 |
| 醤油 | 細麺 | 大盛り | 食券6 |
| 醤油 | 太麺 | 普通 | 食券7 |
| 醤油 | 太麺 | 大盛り | 食券8 |
| 味噌 | 細麺 | 普通 | 食券9 |
| 味噌 | 細麺 | 大盛り | 食券10 |
| 味噌 | 太麺 | 普通 | 食券11 |
| 味噌 | 太麺 | 大盛り | 食券12 |

### 2.6 実装上の注意

- 判定は完全一致（`==`）で行う。
- 大文字小文字・前後空白の正規化は行わない。
- `request` 自体が `null` の場合の防御は現在実装にない（呼び出し側で非nullを保証する前提）。

## 3. テスト観点

- 正常系: 上記12パターンがすべて期待どおりの食券番号を返すこと。
- 異常系: 想定外文字列、空文字、`null`相当値の入力で `null` を返すこと。
- 回帰: 条件式の順序変更やマッピング変更時に判定表との整合が崩れないこと。

