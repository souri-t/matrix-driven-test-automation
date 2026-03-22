# ShippingFeeService 仕様

対象: [src/PurchaseLibrary/ShippingFeeService.cs](../src/PurchaseLibrary/ShippingFeeService.cs)

## 概要
`ShippingFeeService.Evaluate(ShippingFeeRequest request)` は、配送条件に応じて送料区分を文字列で返します。

返却される送料区分:
- `unavailable`
- `invalid`
- `free`
- `low`
- `medium`
- `standard`
- `high`

## 入力
`ShippingFeeRequest` の項目:
- `DestinationRegion` (string)
- `MemberTier` (string)
- `OrderAmount` (decimal)
- `IsFragile` (bool)

## 判定ルール（上から順に評価、最初に一致した条件を採用）

1. `DestinationRegion == "unsupported"` の場合、`unavailable` を返す。
2. `OrderAmount < 0` の場合、`invalid` を返す。
3. `MemberTier == "platinum"` かつ `OrderAmount >= 5000` の場合:
   - `IsFragile == true` なら `standard`
   - `IsFragile == false` なら `free`
4. `DestinationRegion == "remote"` の場合:
   - `IsFragile == true` なら `high`
   - `IsFragile == false` なら `medium`
5. `OrderAmount >= 10000` の場合:
   - `IsFragile == true` なら `medium`
   - `IsFragile == false` なら `free`
6. `OrderAmount >= 3000` の場合:
   - `IsFragile == true` なら `medium`
   - `IsFragile == false` なら `low`
7. 上記すべてに該当しない場合:
   - `IsFragile == true` なら `high`
   - `IsFragile == false` なら `standard`

## 優先順位に関する注意
- `DestinationRegion == "unsupported"` は最優先です。
  - たとえ `OrderAmount < 0` でも `unavailable` が返ります。
- `platinum` 特典判定は `remote` 判定より先に評価されます。
  - `DestinationRegion == "remote"` かつ `MemberTier == "platinum"` かつ `OrderAmount >= 5000` の場合、`remote` ルールではなく `platinum` ルールが適用されます。

## 境界値
- `OrderAmount < 0`: `invalid`
- `OrderAmount == 0`: 通常の金額帯判定（最終 `standard` / `high` 側）
- `OrderAmount == 3000`: `>= 3000` ルール対象
- `OrderAmount == 5000`: `platinum` かつ会員条件一致時に特典対象
- `OrderAmount == 10000`: `>= 10000` ルール対象（ただし、より上位ルールがあればそちらを優先）
