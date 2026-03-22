# APIプロジェクト概要

ASP.NET Core Web APIプロジェクトを使用したプロジェクトの概要を説明します。
尚、３層スキーマとして、API層、サービス層、データアクセス層を分けて設計します。

### API仕様

- ユーザー取得
  - 仕様ID: API-001
  - エンドポイント: `GET /api/users`
  - 説明: 登録されているユーザーのリストを取得します。
  - レスポンス例:
    ```json
    [
      {
        "id": 1,
        "name": "John Doe",
        "email": "john.doe@example.com"
      }
    ]
    ```
  - 備考: 論理削除されたユーザーはリストに含まれません。

- ユーザー作成
  - 仕様ID: API-002
  - エンドポイント: `POST /api/users`
  - 説明: 新しいユーザーを作成します。
  - リクエスト例:
    ```json
    {
      "name": "Jane Doe",
      "email": "jane.doe@example.com"
    }
    ```
    - レスポンス例:
        ```json
        {
        "id": 2,
        "name": "Jane Doe",
        "email": "jane.doe@example.com"
        }
        ```
    
