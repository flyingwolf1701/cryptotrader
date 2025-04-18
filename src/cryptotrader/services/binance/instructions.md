Binance WebSocket API Implementation Instructions
Purpose
These instructions guide the implementation of Binance WebSocket API components based on official Binance documentation. They ensure consistency across implementations and maintain the established project architecture.

Process Overview
When implementing a new WebSocket API component:

Documentation Review: Parse the provided Binance documentation
Structure Analysis: Review the wsDesignDoc.md and wsStructureDoc.yaml files
Plan Creation: Develop an implementation plan including:
YAML updates
Design document updates
Stream file implementation
Diagnostic script creation
Model additions/modifications (if needed)
Plan Approval: Present the implementation plan for review and approval before proceeding
Code Implementation: Produce the required files following the established patterns only after plan approval
Required Inputs
Provide the following to start the implementation process:

Binance Documentation: The official Binance documentation section relevant to the feature being implemented
Current Design Document: The current wsDesignDoc.md file
Current Structure Document: The current wsStructureDoc.yaml file
Implementation Target: Specify which stream component is being implemented (e.g., market_stream, user_stream, order_stream)
Expected Outputs
The implementation should produce:

Updated YAML: Modified wsStructureDoc.yaml with accurate endpoint details, methods, and models
Updated Design Doc: Modified wsDesignDoc.md with implementation guidance and patterns
Stream Implementation: New [feature]_stream.py file following the project's architecture
Diagnostic Script: New [feature]_stream_diagnostic.py file for testing the implementation
Model Additions: Any required model classes for the feature (if needed)
Implementation Guidelines
1. YAML Updates
Add only factual information directly from the Binance documentation
Document all endpoints with their exact paths and parameters
Define all required data models with their properties
Specify the security type required for each endpoint
Include dependency relationships between components
2. Design Document Updates
Add feature-specific implementation guidance
Include any special considerations for the feature
Document authentication requirements
Explain stream subscription patterns
Provide error handling recommendations
3. Stream File Implementation
Follow the factory pattern established in base_operations.py
Use async/await for all network operations
Include comprehensive error handling
Provide detailed docstrings for all methods
Follow the naming convention with "_stream.py" suffix
4. Diagnostic Script Creation
Follow the pattern in binance_websocket_diagnostic.py
Test the actual live implementation against the Binance API (not unit tests)
Verify real-world functionality with the actual Binance WebSocket endpoints
Use colorama for clear, color-coded output
Implement proper connection management and error handling
Include interactive testing of live data streams
Provide summary reporting of test results
5. Model Additions
Create strongly-typed data classes for requests and responses
Include factory methods for parsing JSON responses
Maintain consistency with existing models in base_models.py
Document all models with clear docstrings
File Naming Conventions
Feature implementation files: [feature]_stream.py (e.g., market_stream.py)
Diagnostic scripts: [feature]_stream_diagnostic.py (e.g., market_stream_diagnostic.py)
Model files (if needed): [feature]_models.py (e.g., market_models.py)
Example Instruction
"Please review the provided Binance WebSocket Market Stream documentation, along with the current wsDesignDoc.md and wsStructureDoc.yaml files. Create an implementation plan for the market_stream.py component, including necessary YAML and design document updates, the stream file implementation, a diagnostic script that tests against the live Binance API, and any required model additions. Follow the established patterns in base_operations.py and binance_websocket_diagnostic.py. Present this plan for approval before proceeding with any code implementation."

General Instructions:
Please review the provided Binance WebSocket Market Stream documentation, along with the current wsDesignDoc.md and wsStructureDoc.yaml files. Create an implementation plan this component, including necessary YAML and design document updates, the stream file implementation, a diagnostic script that tests against the live Binance API, and any required model additions. Follow the established patterns in base_operations.py and binance_websocket_diagnostic.py. Present this plan for approval before proceeding with any code implementation.