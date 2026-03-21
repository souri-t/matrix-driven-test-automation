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
