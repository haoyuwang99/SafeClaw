# Risk Notes for safe-openhue

## Threat Model Summary

openhue controls Philips Hue lights via a local Hue Bridge. It can turn lights on/off, adjust brightness/color, and activate scenes across rooms. As a physical-world actuator, its risk profile differs from purely digital tools.

## Action Space

- **read**: List lights, rooms, scenes, bridge status
- **write**: Change light state (on/off, brightness, color, temperature), activate scenes
- **destructive**: Turn off all lights (physical safety hazard in dark environments), rapid state changes
- **external**: Communicates with Hue Bridge on local network
- **credential**: Bridge pairing token stored locally

## Key Risks

### 1. Physical-World Disruption
Turning off lights unexpectedly can create safety hazards (falls, disorientation). Extreme brightness changes affect comfort and vision adaptation.

Mitigation:
- Confirm all off/on operations with room scope
- Confirm extreme brightness values

### 2. Scope Explosion
A command targeting "all lights" or "all rooms" has broad physical impact.

Mitigation:
- Block broad unscoped operations
- Require per-room confirmation for multi-room changes

### 3. Seizure/Flicker Risk
Rapid color or brightness cycling can trigger photosensitive seizures.

Mitigation:
- Block rapid sequential state changes
- Enforce minimum interval between commands

### 4. Bridge Configuration Tampering
Modifying bridge pairing or settings affects all users on the network.

Mitigation:
- Block bridge configuration changes entirely

### 5. Automation Without Bounds
Looping light commands without user-set limits could cause persistent disruption.

Mitigation:
- Block unattended automation loops

## Safe vs Unsafe

Safe:
- Listing lights, rooms, scenes
- Checking single light status

Confirm:
- Turning lights on/off per room
- Brightness/color changes
- Scene activation

Block:
- All-lights-off without explicit scope
- Rapid flickering commands
- Bridge config changes
- Unbounded automation loops
