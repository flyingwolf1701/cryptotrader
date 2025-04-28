📚 Architectum Models System (models_shape.json)
Overview
The models_shape.json file defines all structured models used by the REST APIs.
Each model represents a data contract used across the system: for API responses, internal business logic, and future client/server validation.

Models are grouped by module (matching your file structure):

order_models

user_models

market_models

wallet_models

staking_models

otc_models

base_models

Structure
json
Copy
Edit
{
  "models": {
    "module_name": {
      "ModelName": {
        "type": "object",
        "properties": {
          "fieldName": { "type": "primitiveType" }
        },
        "required": ["fieldName", ...],
        "callsOn": [],
        "calledBy": []
      }
    }
  }
}
Fields Explained

Field	Purpose
type	Always "object". Describes that this is a structured record with fields.
properties	Dictionary of fields and their types. Types are primitives (string, integer, number, boolean) or nested objects.
required	List of property names that must be present for a valid model.
callsOn	(Reserved) Future use. Lists other models this model calls internally (currently empty).
calledBy	Lists which API responses reference and use this model (populated automatically).
Important Design Principles
No duplication: Each model is declared exactly once.

Human-readable structure: Easy for developers to browse.

Machine-parseable: JSON format ready for validation, client codegen, and automated documentation.

Modular and future-proof: Models are grouped per original module (file).

Example
Suppose the API orderAPI.placeOrder responds with an OrderResult.
Then:

In models_shape.json:

json
Copy
Edit
{
  "models": {
    "order_models": {
      "OrderResult": {
        "type": "object",
        "properties": {
          "orderId": { "type": "integer" },
          "symbol": { "type": "string" }
        },
        "required": ["orderId", "symbol"],
        "callsOn": [],
        "calledBy": [
          "restAPI_shape.orderAPI.placeOrder.response"
        ]
      }
    }
  }
}
Rules for Models
✅ Every model is an object (no loose primitives).
✅ properties must list each field type explicitly.
✅ required array must be accurate and match system expectations.
✅ callsOn and calledBy must always exist, even if empty.

📌 Notes for Developers
When a REST API function returns a dataclass, its type points to the ModelName and reference points here.

When modifying or adding models, always update properties, required, and (eventually) callsOn relationships.

All primitive fields (string, number, etc.) are always lowercased type names.

New modules should be added by creating a new top-level key under "models" matching the module name.

📦 Future Enhancements
Automatic population of callsOn based on business rules between models.

Deep linking between models that internally reference other models.

Unified client building based on calledBy entries.

✨ Summary
models_shape.json serves as the blueprint for all structured data in Architectum —
driving validation, documentation, typing, and unified client mapping in a consistent, durable way.

Blueprints of living systems.
