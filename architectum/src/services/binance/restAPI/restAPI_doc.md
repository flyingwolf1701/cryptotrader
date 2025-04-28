📚 Architectum REST API Shape System (restAPI_shape.json)
Overview
The restAPI_shape.json defines the full structured behavior of the REST API endpoints.
Each API module and function includes:

Its request shape

Its response shape

Future wiring (callsOn, calledBy)

This ensures all APIs are consistently documented, machine-validated, and ready for automated client generation.

Structure
json
Copy
Edit
{
  "restAPI_spec": {
    "moduleAPI": {
      "functionName": {
        "request": { ... },
        "response": { ... },
        "callsOn": [],
        "calledBy": []
      }
    }
  }
}
Fields Explained

Field	Purpose
request	Defines the input data structure expected by the function.
response	Defines the output data structure returned by the function.
type (inside request/response)	Either a primitive (string, integer, etc.), "object", "array", or the name of a Dataclass model.
properties (inside request/response)	Only exists if type is "object".
reference (inside response)	JSON path to the corresponding model in models_shape.json.
callsOn[]	Future list of API specs that this function internally calls.
calledBy[]	Future list of API specs that call this function.
Important Design Principles
No duplication: Request and response shapes are clean and minimal.

Self-contained documentation: Everything needed is inside each function block.

Separation of concerns: Models live in models_shape.json, APIs reference them.

Machine-parseable: Strict structure for easy tooling.

Example
json
Copy
Edit
{
  "restAPI_spec": {
    "orderAPI": {
      "placeOrder": {
        "request": {
          "type": "object",
          "properties": {
            "symbol": { "type": "string" },
            "side": { "type": "string" },
            "type": { "type": "string" },
            "quantity": { "type": "number" },
            "price": { "type": "number" },
            "timeInForce": { "type": "string" }
          },
          "required": ["symbol", "side", "type"]
        },
        "response": {
          "type": "OrderResult",
          "reference": "models_shape.order_models.OrderResult"
        },
        "callsOn": [],
        "calledBy": []
      }
    }
  }
}
✅ Requests inline primitive properties if needed.
✅ Responses point cleanly to a model definition.

Rules for APIs
✅ Always use camelCase function names.
✅ Group APIs under correct module keys (e.g., orderAPI, walletAPI, marketAPI).
✅ Requests can be:

Object (with properties)

Null (no input required)

✅ Responses are either:

Primitive/simple

Or a model type with a reference field.

✅ callsOn and calledBy arrays must always exist, even if empty.

⚙️ Base Operations Layer
All REST API functions are built on top of a powerful internal module: base_operations.py.

Key Responsibilities:
Secure authentication and request signing using HMAC-SHA256.

Rate limit tracking to prevent API bans.

Automatic retry and exponential backoff when encountering temporary failures (HTTP 429/418).

Transparent error handling and response validation.

Separation of concerns: Application logic never touches raw HTTP.

How it Works:
When an API call is made (e.g., placeOrder or getServerTime):

base_operations.py automatically prepares the request.

Signs it if authentication is needed.

Sends the request and handles retries if necessary.

Tracks rate limits locally.

Returns the parsed response cleanly to the API function.

Why It Matters:
Stability: Automatic recovery from temporary failures.

Security: Signed requests for protected endpoints.

Maintainability: Clear separation between transport and business logic.

Performance: Local rate limit tracking reduces server load and keeps requests efficient.

📚 In Summary
base_operations.py is the engine that powers the Architectum REST API layer —
ensuring your systems remain fast, safe, and reliable, without extra complexity leaking into the business code.

📌 Notes for Developers
Requests are manually defined unless they map to a dataclass in the future.

Responses must be typed, referencing the proper model whenever applicable.

New API functions should follow this exact pattern for consistency.

📦 Future Enhancements
Auto-population of callsOn during full internal service mapping.

Full backward/forward validation between request and response shapes.

Code generation (TypeScript, Python) directly from this schema.