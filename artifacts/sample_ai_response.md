以下が生成したMSTestコードです。

```csharp
using PurchaseLibrary;

namespace PurchaseLibrary.Tests;

[TestClass]
public class PurchaseServiceMatrixAiTests
{
    [DataTestMethod]
    [DataRow("TC001", "normal", "credit", "normal", "success")]
    [DataRow("TC002", "normal", "cash", "normal", "success")]
    [DataRow("TC003", "normal", "cash", "restricted", "forbidden")]
    [DataRow("TC004", "premium", "cash", "restricted", "failed")]
    [DataRow("TC005", "blacklisted", "credit", "normal", "blocked")]
    public void Evaluate_MatrixCases_FromAi(
        string id,
        string userType,
        string payment,
        string product,
        string expected)
    {
        var actual = PurchaseService.Evaluate(new PurchaseRequest(userType, payment, product));

        Assert.AreEqual(expected, actual, $"{id}: expected={expected}, actual={actual}");
    }
}
```
