Binance WebSocket API Implementation Guidelines
Requirements
Documentation

Read Binance WebSocket API documentation thoroughly
Study wsDesignDoc.md and wsStructureDoc.yaml files

Implementation Process

Create the implementation file in the appropriate directory
Follow established patterns in existing implementations
Implement comprehensive testing and error handling
Create a diagnostic script following the reference pattern
Update relevant exports in __init__.py files

Implementation Standards
Code Structure

One request per file, named after the Binance API method
Follow naming conventions and directory structure
Create strongly-typed models with factory methods

Request Implementation

Use async/await for all operations
Include parameter validation
Handle errors and rate limiting appropriately
Use the security type specified in documentation

Diagnostic Scripts

Use the pattern in market_diagnostic.py as reference
Focus on testing the implementation directly (not reimplementing functionality)
Create minimal, focused tests with clear output
Utilize existing connection management code

Avoid Common Mistakes

Don't duplicate code from the module being tested in diagnostic scripts
Don't create complex class hierarchies for testing
Don't add business logic in __init__.py files
Don't mix testing with implementation details

Deliverables Checklist

 Implementation file following project patterns
 Diagnostic script that directly tests implementation
 Documentation updates (if required)
 Model additions/modifications (if required)
 Clean exportable API via __init__.py


General Instructions:
Please review the provided Binance WebSocket Market Stream documentation, along with the current wsDesignDoc.md and wsStructureDoc.yaml files. Create an implementation plan this component, including necessary YAML and design document updates, the stream file implementation, a diagnostic script that tests against the live Binance API, and any required model additions. Follow the established patterns in base_operations.py and binance_websocket_diagnostic.py. Present this plan for approval before proceeding with any code implementation.