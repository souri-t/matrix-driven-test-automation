namespace PurchaseLibrary;

public sealed class ShippingFeeService
{
    public string Evaluate(ShippingFeeRequest request)
    {
        ArgumentNullException.ThrowIfNull(request);

        if (request.DestinationRegion == "unsupported")
        {
            return "unavailable";
        }

        if (request.OrderAmount < 0)
        {
            return "invalid";
        }

        if (request.MemberTier == "platinum" && request.OrderAmount >= 5000)
        {
            return request.IsFragile ? "standard" : "free";
        }

        if (request.DestinationRegion == "remote")
        {
            return request.IsFragile ? "high" : "medium";
        }

        if (request.OrderAmount >= 10000)
        {
            return request.IsFragile ? "medium" : "free";
        }

        if (request.OrderAmount >= 3000)
        {
            return request.IsFragile ? "medium" : "low";
        }

        return request.IsFragile ? "high" : "standard";
    }
}

public sealed record ShippingFeeRequest(
    string DestinationRegion,
    string MemberTier,
    decimal OrderAmount,
    bool IsFragile);