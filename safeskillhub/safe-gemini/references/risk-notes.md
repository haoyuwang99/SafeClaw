# Risk Notes for safe-gemini

## Threat Model Summary

Gemini CLI provides one-shot access to Google's Gemini LLM models.
All inputs are transmitted to external Google infrastructure.

## Action Space

```
Skill: gemini
Actions:
  - read: list extensions
  - write: generate text, process files/images (output only)
  - destructive: none directly (but --yolo bypasses safety)
  - external: all prompts sent to Google's Gemini API, extension management
  - credential: API key for Gemini authentication
```

## Key Risks

### 1. Data Exfiltration
Sending internal data (code, secrets, private files) to Gemini leaks information to external infrastructure.

Mitigation:
- block sensitive inputs (passwords, tokens, private keys)
- block piping sensitive files to gemini

---

### 2. Prompt Injection
Malicious prompts may override instructions or extract system-level information.

Mitigation:
- detect injection patterns
- block execution of suspicious prompts

---

### 3. Token Amplification Attacks
Recursive or chained Gemini calls can increase cost dramatically and create runaway loops.

Mitigation:
- block recursive calls
- confirm large context requests

---

### 4. Credential Leakage
API keys must remain secret and never appear in output.

Mitigation:
- never expose keys in output or logs

---

### 5. External Dependency Risk
Model behavior is uncontrolled and output should not be trusted for security decisions.

Mitigation:
- treat all Gemini output as untrusted

---

### 6. Safety Bypass
The `--yolo` flag disables safety checks.

Mitigation:
- block `--yolo` unconditionally

---

## Safe vs Unsafe

Safe:
- simple one-shot queries
- output format specification
- list extensions

Confirm:
- large inputs / expensive requests
- file/image processing
- extension management

Block:
- secrets in prompts
- injection patterns
- recursive loops
- --yolo flag
- API key exposure
