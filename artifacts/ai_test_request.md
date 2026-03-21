# Task
Generate MSTest code for PurchaseService from the matrix.

## Output format
- Output ONLY one C# code block.
- Target file: src/PurchaseLibrary.Tests/Generated/PurchaseServiceMatrixAiTests.cs

## Constraints
- Namespace: PurchaseLibrary.Tests
- Use [TestClass] and [DataTestMethod]
- Use [DataRow] for each matrix row
- Method name: Evaluate_MatrixCases_FromAi
- Call: PurchaseService.Evaluate(new PurchaseRequest(userType, payment, product))
- Assert: Assert.AreEqual(expected, actual, $"{id}: expected={expected}, actual={actual}")

## Matrix JSON
```json
[
  {
    "id": "TC001",
    "user_type": "normal",
    "payment": "credit",
    "product": "normal",
    "expected": "success"
  },
  {
    "id": "TC002",
    "user_type": "normal",
    "payment": "cash",
    "product": "normal",
    "expected": "success"
  },
  {
    "id": "TC003",
    "user_type": "normal",
    "payment": "cash",
    "product": "restricted",
    "expected": "forbidden"
  },
  {
    "id": "TC004",
    "user_type": "premium",
    "payment": "cash",
    "product": "restricted",
    "expected": "failed"
  },
  {
    "id": "TC005",
    "user_type": "blacklisted",
    "payment": "credit",
    "product": "normal",
    "expected": "blocked"
  }
]
```

## Source Code
```csharp
namespace PurchaseLibrary;

public sealed record PurchaseRequest(string UserType, string Payment, string Product);

public static class PurchaseService
{
    public static string Evaluate(PurchaseRequest request)
    {
        if (request.UserType == "blacklisted")
        {
            return "blocked";
        }

        if (request.Product == "restricted" && request.UserType != "premium")
        {
            return "forbidden";
        }

        if (request.Payment == "credit")
        {
            return "success";
        }

        if (request.Payment == "cash" && request.Product == "normal")
        {
            return "success";
        }

        return "failed";
    }
}

```
