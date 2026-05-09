# Good and Bad Tests

## Good Tests

**Integration-style**: Test through real interfaces, not mocks of internal parts.

```csharp
// GOOD: Tests observable behavior
public class CheckoutTests
{
    [Fact]
    public async Task UserCanCheckoutWithValidCart()
    {
        var cart = new Cart();
        cart.Add(product);
        var result = await _checkoutService.CheckoutAsync(cart, paymentMethod);
        Assert.Equal("confirmed", result.Status);
    }
}
```

Characteristics:

- Tests behavior users/callers care about
- Uses public API only
- Survives internal refactors
- Describes WHAT, not HOW
- One logical assertion per test

## Bad Tests

**Implementation-detail tests**: Coupled to internal structure.

```csharp
// BAD: Tests implementation details
public class CheckoutTests
{
    [Fact]
    public async Task Checkout_CallsPaymentServiceProcess()
    {
        var mockPayment = new Mock<IPaymentService>();
        var sut = new CheckoutService(mockPayment.Object);
        await sut.CheckoutAsync(cart, payment);
        mockPayment.Verify(p => p.ProcessAsync(cart.Total), Times.Once);
    }
}
```

Red flags:

- Mocking internal collaborators
- Testing private methods
- Asserting on call counts/order
- Test breaks when refactoring without behavior change
- Test name describes HOW not WHAT
- Verifying through external means instead of interface

```csharp
// BAD: Bypasses interface to verify
[Fact]
public async Task CreateUser_SavesRowToDatabase()
{
    await _userService.CreateUserAsync(new CreateUserRequest { Name = "Alice" });
    var row = await _dbContext.Users.FirstOrDefaultAsync(u => u.Name == "Alice");
    Assert.NotNull(row);
}

// GOOD: Verifies through interface
[Fact]
public async Task CreateUser_MakesUserRetrievable()
{
    var user = await _userService.CreateUserAsync(new CreateUserRequest { Name = "Alice" });
    var retrieved = await _userService.GetUserAsync(user.Id);
    Assert.Equal("Alice", retrieved.Name);
}
```
