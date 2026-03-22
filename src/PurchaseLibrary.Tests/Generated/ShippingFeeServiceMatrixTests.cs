using System.Globalization;
using PurchaseLibrary;

namespace PurchaseLibrary.Tests.Generated;

[TestClass]
public class ShippingFeeServiceMatrixTests
{
    [DataTestMethod]
    [DataRow("SF001", "unsupported", "regular", "-1", false, "unavailable")]
    [DataRow("SF002", "local", "regular", "-1", true, "invalid")]
    [DataRow("SF003", "local", "platinum", "5000", false, "free")]
    [DataRow("SF004", "local", "platinum", "5000", true, "standard")]
    [DataRow("SF005", "remote", "platinum", "5000", false, "free")]
    [DataRow("SF006", "remote", "regular", "7000", false, "medium")]
    [DataRow("SF007", "remote", "regular", "7000", true, "high")]
    [DataRow("SF008", "local", "regular", "10000", false, "free")]
    [DataRow("SF009", "local", "regular", "10000", true, "medium")]
    [DataRow("SF010", "local", "regular", "3000", false, "low")]
    [DataRow("SF011", "local", "regular", "3000", true, "medium")]
    [DataRow("SF012", "local", "regular", "0", false, "standard")]
    [DataRow("SF013", "local", "regular", "0", true, "high")]
    public void Evaluate_MatrixCases(
        string id,
        string destinationRegion,
        string memberTier,
        string orderAmount,
        bool isFragile,
        string expected)
    {
        var service = new ShippingFeeService();

        var request = new ShippingFeeRequest(
            destinationRegion,
            memberTier,
            decimal.Parse(orderAmount, CultureInfo.InvariantCulture),
            isFragile);

        var actual = service.Evaluate(request);

        Assert.AreEqual(expected, actual, $"{id}: expected={expected}, actual={actual}");
    }
}