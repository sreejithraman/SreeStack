# Good and Bad Tests

## Good Tests

**Integration-style**: Test through real interfaces, not mocks of internal parts.

```typescript
// GOOD: Tests observable behavior
test("user can checkout with valid cart", async () => {
  const cart = createCart();
  cart.add(product);
  const result = await checkout(cart, paymentMethod);
  expect(result.status).toBe("confirmed");
});
```

Characteristics:

- Tests behavior users/callers care about
- Uses public API only
- Survives internal refactors
- Describes WHAT, not HOW
- One logical assertion per test

## Event sequences

For lifecycle rules, choose sequences from the product contract using
[Model the Domain](../engineering-principles/references/model-the-domain.md#stateful-behavior).
Check repeated input and recovery, plus cancellation and late completion when
supported. Build each scenario in its own red → green cycle; a longer sequence
can be one scenario when the order is the behavior under test.

This Vitest example assumes a submission's public API exposes `submit`, `retry`,
`waitForStatus`, and `getResult`. `save` is the external persistence boundary;
`deferred` is a test helper whose promise the test can resolve or reject.
Use the project's actual public seam and helpers.

```typescript
test("repeated submit saves once, then a failed save can be retried", async () => {
  const draft = { title: "Draft" };
  const firstAttempt = deferred<{ id: string }>();
  const save = vi.fn()
    .mockReturnValueOnce(firstAttempt.promise)
    .mockResolvedValueOnce({ id: "saved-1" });
  const submission = createSubmission({ save });

  submission.submit(draft);
  submission.submit(draft);
  expect(save.mock.calls).toEqual([[{ title: "Draft" }]]);

  firstAttempt.reject(new Error("Offline"));
  await submission.waitForStatus("failure");
  submission.retry();
  await submission.waitForStatus("success");

  expect(submission.getResult()).toEqual({ id: "saved-1" });
  expect(save.mock.calls).toEqual([
    [{ title: "Draft" }],
    [{ title: "Draft" }],
  ]);
});
```

The assertions check outgoing payloads at the external boundary and the public
result. They detect duplicate writes and a missing or broken retry. Choose
expected behavior independently of the implementation's transition table.
Add real UI acceptance coverage when the feature has UI entry points.

## Bad Tests

**Implementation-detail tests**: Coupled to internal structure.

```typescript
// BAD: Tests implementation details
test("checkout calls paymentService.process", async () => {
  const mockPayment = jest.mock(paymentService);
  await checkout(cart, payment);
  expect(mockPayment.process).toHaveBeenCalledWith(cart.total);
});
```

Red flags:

- Mocking internal collaborators
- Testing private methods
- Asserting on internal call counts/order instead of public results or external effects
- Test breaks when refactoring without behavior change
- Test name describes HOW not WHAT
- Verifying through external means instead of interface

```typescript
// BAD: Bypasses interface to verify
test("createUser saves to database", async () => {
  await createUser({ name: "Alice" });
  const row = await db.query("SELECT * FROM users WHERE name = ?", ["Alice"]);
  expect(row).toBeDefined();
});

// GOOD: Verifies through interface
test("createUser makes user retrievable", async () => {
  const user = await createUser({ name: "Alice" });
  const retrieved = await getUser(user.id);
  expect(retrieved.name).toBe("Alice");
});
```

**Tautological tests**: Expected value restates the implementation, so the test passes by construction.

```typescript
// BAD: Expected value is recomputed the way the code computes it
test("calculateTotal sums line items", () => {
  const items = [{ price: 10 }, { price: 5 }];
  const expected = items.reduce((sum, i) => sum + i.price, 0);
  expect(calculateTotal(items)).toBe(expected);
});

// GOOD: Expected value is an independent, known literal
test("calculateTotal sums line items", () => {
  expect(calculateTotal([{ price: 10 }, { price: 5 }])).toBe(15);
});
```
