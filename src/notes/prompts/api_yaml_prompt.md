# REST API YAML Documentation Creation Prompt

You are creating structured YAML documentation for a REST API client.

Follow this exact format:

## Structure:
- **Top-level**: Group APIs by service name (e.g., `systemApi`, `market_data_api`).
- **Each function must include**:
  - `endpoint`: HTTP method and path (e.g., `"GET /api/v3/time"`).
  - `description`: What the endpoint does. Clear, one or two sentences.
  - `arguments`:  
    - List each argument as:
      - `name`: The parameter name.
      - `type`: The data type (`string`, `integer`, `boolean`, `array of strings`, `object`, etc.).
      - `description`: Short explanation of the parameter.
    - If there are no arguments, use `arguments: []`.
    - If the possible values are **finite and enumerable** (like `SPOT`, `TRADING`), list them in the description.
    - **If the type is boolean, no need to list accepted values** ("true/false" is implied).
  - `returns`:  
    - `type`: The return object (e.g., `integer`, `SystemStatus`, `ExchangeInfo`).
  - `examples`:  
    - List real usage examples that a developer could copy and run.
    - Each example must include:
      - `description`: What the example is doing.
      - `usage`: Realistic Python code using the function.

## General style rules:
- Be specific about finite values for enums (permissions, statuses).
- Keep descriptions clear and non-redundant.
- Focus examples on **real-world developer usage patterns**.
- Boolean fields are **self-explanatory** and need no additional accepted values note.

---

# WebSocket API YAML Documentation Creation Prompt

You are creating structured YAML documentation for a WebSocket API client.

Follow this exact format:

## Structure:
- **Top-level**: Group WebSocket APIs by logical category (e.g., `market_streams`, `user_streams`).
- **Each function must include**:
  - `websocket_topic`: Topic name to subscribe to (e.g., `"bookTicker"`, `"aggTrade"`).
  - `description`: Clear one or two sentences explaining what subscribing to this topic delivers.
  - `arguments`:  
    - Same rules as REST.
    - List all subscription parameters clearly.
    - If none, use `arguments: []`.
  - `returns`:  
    - `type`: The expected pushed message object (e.g., `BookTickerUpdate`).
  - `examples`:  
    - Provide real subscription examples showing:
      - Subscribing
      - (Optionally) basic message handling

## General style rules:
- Use the same consistent formatting as REST APIs.
- Focus examples on **subscription and event handling**.
- Keep types simple and self-explanatory where possible.
- Avoid redundant notes for boolean parameters.

---

# Quick Tips
- This style is optimized for **developers**, **documentation generation**, and **AI understanding**.
- Future versions can easily be auto-converted into Markdown, OpenAPI, or even programmatically parsed if needed.

