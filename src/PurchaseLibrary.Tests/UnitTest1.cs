using PurchaseLibrary;

namespace PurchaseLibrary.Tests;

[TestClass]
public class PurchaseServiceTests
{
    [DataTestMethod]
    [DataRow("TC001", "normal", "credit", "normal", "success")]
    [DataRow("TC002", "normal", "cash", "normal", "success")]
    [DataRow("TC003", "normal", "cash", "restricted", "forbidden")]
    [DataRow("TC004", "premium", "cash", "restricted", "failed")]
    [DataRow("TC005", "blacklisted", "credit", "normal", "blocked")]
    public void Evaluate_ReturnsExpectedResult(
        string id,
        string userType,
        string payment,
        string product,
        string expected)
    {
        var request = new PurchaseRequest(userType, payment, product);

        var actual = PurchaseService.Evaluate(request);

        Assert.AreEqual(expected, actual, $"{id}: expected={expected}, actual={actual}");
    }
}
