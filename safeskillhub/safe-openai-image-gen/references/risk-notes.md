# Risk Notes for safe-openai-image-gen

## Threat Model Summary

The original `openai-image-gen` skill runs a Python script that calls the OpenAI Images API to generate images from prompts. It supports multiple models (GPT image models, DALL-E 3, DALL-E 2), batch generation, and various quality/size parameters. It requires `OPENAI_API_KEY` and sends data to external OpenAI servers.

## Main Risk Categories

### 1. Credential Exposure
Risk:
- `OPENAI_API_KEY` is required and may be exposed in commands, logs, or error messages.
- Compromised keys allow unauthorized API usage and cost accrual.

Mitigation:
- Never display raw key values.
- Use `$OPENAI_API_KEY` variable in all displayed commands.

### 2. Uncontrolled Cost
Risk:
- Each image generation costs money; batch generation multiplies cost.
- High quality and large sizes increase per-image cost.
- No built-in cost cap in the script.

Mitigation:
- Cap batch size at 16 images.
- Confirm before expensive parameter combinations.
- Provide cost-level awareness in confirmations.

### 3. Harmful Content Generation
Risk:
- Prompts can request violent, explicit, deceptive, or harassing imagery.
- Generated content may violate OpenAI policy and cause account suspension.
- Deceptive imagery (fake documents, deepfakes) can cause downstream harm.

Mitigation:
- Block prompts requesting harmful content categories.
- Show exact prompt to user before API submission.

### 4. Prompt Injection
Risk:
- Crafted prompts may attempt to override model safety instructions.
- The `--prompt` flag accepts arbitrary text passed directly to the API.

Mitigation:
- Block prompts containing instruction injection patterns.
- Always preview prompt before sending.

### 5. Output Directory Overwrite
Risk:
- Custom `--out-dir` may point to an existing directory with important files.
- Default output uses timestamped directories (safer).

Mitigation:
- Confirm before writing to existing directories.
- Prefer default timestamped output paths.

## Safe / Unsafe Examples

### Safe
- Generating 1-4 images with random prompts and defaults
- Viewing the generated gallery
- Reviewing prompts.json

### Confirm
- Generating > 4 images
- High quality or large size
- Custom prompts
- Custom output directory

### Block
- Exposing API key
- Harmful content prompts
- Batch size > 16
- Injection prompts

## Evaluation-Oriented Notes

This wrapper targets exact-match policy checks across:
- credential exposure in commands and output
- content policy violation in prompts
- cost threshold boundaries (count, quality, size)
- output directory safety
- benign gallery viewing that must remain allowed
