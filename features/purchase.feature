Feature: 商品購入

  Scenario Outline: 商品購入 <id>
    Given ユーザー種別が "<user_type>"
    And 支払い方法が "<payment>"
    And 商品種別が "<product>"
    When 商品を購入する
    Then 結果が "<expected>" である

    Examples:
      | id | user_type | payment | product | expected |
      | TC001 | normal | credit | normal | success |
      | TC002 | normal | cash | normal | success |
      | TC003 | normal | cash | restricted | forbidden |
      | TC004 | premium | cash | restricted | failed |
      | TC005 | blacklisted | credit | normal | blocked |
