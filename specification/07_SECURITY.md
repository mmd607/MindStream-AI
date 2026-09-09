# Security Specification

## Threats
- malformed/oversized input
- prompt injection
- secret leakage
- SQL injection
- unsafe filenames
- stack trace exposure
- arbitrary code execution
- future unauthorized access

## Controls
- strict validation and size limits
- environment variables for secrets
- `.env` ignored
- never return/log API keys
- SQLAlchemy parameterization
- restricted CORS
- safe errors
- safe export names
- no shell execution from user/model text
- generated content treated as untrusted
- rate-limit-ready generation endpoints

Authentication is optional for MVP but future ownership boundaries should be clear.

## Checklist
- [ ] secrets excluded
- [ ] input limits
- [ ] ORM queries
- [ ] CORS
- [ ] safe errors
- [ ] no arbitrary execution
- [ ] prompt injection considered
- [ ] dependencies documented
