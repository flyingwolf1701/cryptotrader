# 📚 Architectum REST API Shape System (`restAPI_shape.json`)

## Overview
The `restAPI_shape.json` defines the structured behavior of REST API endpoints in a consistent, machine-validated format.

Each API function describes:
- **`request`**: Input schema, primitive or structured
- **`response`**: Output schema, primitive or structured
- **`callsOn`**: Other functions this API calls, mapped by function to file path
- **`calledBy`**: Functions that call this one, mapped by function to file path

---

## 📐 Structure
```json
{
  "restAPI_spec": {
    "moduleName": {
      "functionName": {
        "request": { ... } | null,
        "response": { ... } | null,
        "callsOn": { "functionName": "path/to/file.py" } | null,
        "calledBy": { "functionName": "path/to/file.py" } | null
      }
    }
  }
}
```

---

## 🧬 Field Definitions
- **`request` / `response`**: May be `null`, or an object with:
  - **`type`**: The structure type — either a primitive (`string`, `number`, `boolean`), a container (`object`, `array`), or a model name.
  - **`properties`**:
    - If `type` is a model, this is the model path (e.g., `models_shape.order_models.OrderRequest`).
    - If `type` is `object` or `array`, this defines the structure inline.
    - For primitives, use direct mappings (e.g., `{ "symbol": "string" }`).
- **`callsOn` / `calledBy`**: Objects mapping function names to their source file paths. Use `null` if none.

---

## 🔍 Examples
```json
{
  "orderAPI": {
    "placeOrder": {
      "request": {
        "type": "string",
        "properties": {
          "symbol": "BTCUSDT"
        }
      },
      "response": {
        "type": "OrderResult",
        "properties": "models_shape.order_models.OrderResult"
      },
      "callsOn": {
        "baseOperations.sendRequest": "restAPI/base_operations.py"
      },
      "calledBy": null 
    },
    "getStatus": {
      "request": {
        "properties": {
          "symbol": "string",
          "orderId": "string"
        }
      },
      "response": {
        "type": "OrderStatus",
        "properties": "models_shape.order_models.OrderStatus"
      },
      "callsOn": null,
      "calledBy": {
        "unifiedClientsBinance.getOrderStatus": "gui/unified_clients/binanceRestUnifiedClient.py"
      }
    }
  }
}
```

---

## ✅ Guidelines
- Use `null` for empty inputs or responses.
- Use inline primitives for flat requests.
- Reference models for nested or reusable structures.
- Include `callsOn` and `calledBy` mappings always — even if empty.
- Avoid deep nesting in `properties`; extract as models if complex.

---

## 🎯 Why This Format?
- Machine-parsable and clear
- Supports model reuse and auto-validation
- Enables call graph analysis and tooling
- Supports direct schema-to-code generation

---

## 🧾 In Summary
Architectum’s REST shape schema captures the surface contract of each function cleanly and precisely. Its design supports automation, validation, and future introspection for resilient system architecture.
