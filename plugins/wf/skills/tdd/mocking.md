# When to Mock

Mock at **system boundaries** only:

- External APIs (payment, email, etc.)
- Databases (sometimes - prefer test DB)
- Time/randomness
- File system (sometimes)

Don't mock:

- Your own classes/modules
- Internal collaborators
- Anything you control

## Designing for Mockability

At system boundaries, design interfaces that are easy to mock:

**1. Use dependency injection**

Pass external dependencies in rather than creating them internally:

```csharp
// Easy to mock — dependency injected via constructor
public class PaymentService
{
    private readonly IPaymentClient _client;

    public PaymentService(IPaymentClient client) => _client = client;

    public Task<Result> ProcessPaymentAsync(Order order) =>
        _client.ChargeAsync(order.Total);
}

// Hard to mock — creates its own dependency
public class PaymentService
{
    public Task<Result> ProcessPaymentAsync(Order order)
    {
        var client = new StripeClient(Environment.GetEnvironmentVariable("STRIPE_KEY"));
        return client.ChargeAsync(order.Total);
    }
}
```

**2. Prefer SDK-style interfaces over generic fetchers**

Create specific methods for each external operation instead of one generic method with conditional logic:

```csharp
// GOOD: Each method is independently mockable
public interface IOrderApi
{
    Task<User> GetUserAsync(int id);
    Task<IReadOnlyList<Order>> GetOrdersAsync(int userId);
    Task<Order> CreateOrderAsync(CreateOrderRequest request);
}

// BAD: Mocking requires conditional logic inside the mock
public interface IOrderApi
{
    Task<string> FetchAsync(string endpoint, HttpMethod method, object? body = null);
}
```

The SDK approach means:
- Each mock returns one specific shape
- No conditional logic in test setup
- Easier to see which endpoints a test exercises
- Type safety per endpoint

## Mocking with Moq in xUnit

**Basic setup**

```csharp
public class PaymentServiceTests
{
    private readonly Mock<IPaymentClient> _clientMock = new();
    private readonly PaymentService _sut;

    public PaymentServiceTests()
    {
        _sut = new PaymentService(_clientMock.Object);
    }

    [Fact]
    public async Task ProcessPayment_ChargesCorrectAmount()
    {
        var order = new Order { Total = 99.99m };
        _clientMock
            .Setup(c => c.ChargeAsync(order.Total))
            .ReturnsAsync(Result.Success());

        var result = await _sut.ProcessPaymentAsync(order);

        Assert.True(result.IsSuccess);
        _clientMock.Verify(c => c.ChargeAsync(order.Total), Times.Once);
    }
}
```

**Returning different values per call**

```csharp
_clientMock
    .SetupSequence(c => c.ChargeAsync(It.IsAny<decimal>()))
    .ReturnsAsync(Result.Success())
    .ReturnsAsync(Result.Failure("Declined"));
```

**Simulating exceptions**

```csharp
_clientMock
    .Setup(c => c.ChargeAsync(It.IsAny<decimal>()))
    .ThrowsAsync(new HttpRequestException("Gateway timeout"));
```

**Capturing arguments**

```csharp
CreateOrderRequest? captured = null;
_apiMock
    .Setup(a => a.CreateOrderAsync(It.IsAny<CreateOrderRequest>()))
    .Callback<CreateOrderRequest>(r => captured = r)
    .ReturnsAsync(new Order());

await _sut.PlaceOrderAsync(cart);

Assert.Equal(cart.Items.Count, captured!.LineItems.Count);
```

**Strict vs loose mocks**

```csharp
// Loose (default) — unexpected calls return defaults, no error
var loose = new Mock<IPaymentClient>();

// Strict — unexpected calls throw; useful for verifying no extra calls
var strict = new Mock<IPaymentClient>(MockBehavior.Strict);
```

Prefer **loose mocks** in most tests; use strict only when you need to assert no unintended interactions occur.
