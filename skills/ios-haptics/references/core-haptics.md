# Custom playback

Use Core Haptics to implement an authored tactile timeline: a custom rhythm,
shaped continuous effect, live texture, or coordinated audio and touch. Keep the
pattern definition separate from the owner that manages playback.

## Translate the design into events

An engine creates players; a player runs a pattern of timed events and optional
parameter curves. Use Swift for generated patterns and AHAP for assets that
benefit from separate authoring. Either form needs the same hardware and lifecycle
handling.

This implements the continuous reveal from [the design reference](design.md).
Its values are candidates for device tuning.

```swift
import CoreHaptics

func makeRevealPattern() throws -> CHHapticPattern {
    let event = CHHapticEvent(
        eventType: .hapticContinuous,
        parameters: [
            .init(parameterID: .hapticIntensity, value: 1),
            .init(parameterID: .hapticSharpness, value: 0.25)
        ],
        relativeTime: 0,
        duration: 0.32
    )
    let envelope = CHHapticParameterCurve(
        parameterID: .hapticIntensityControl,
        controlPoints: [
            .init(relativeTime: 0, value: 0.10),
            .init(relativeTime: 0.24, value: 0.45),
            .init(relativeTime: 0.32, value: 0)
        ],
        relativeTime: 0
    )
    return try CHHapticPattern(events: [event], parameterCurves: [envelope])
}
```

The intensity curve multiplies the event's base intensity. With a base of 0.5,
a control value of 0.45 yields 0.225. Curves interpolate linearly and apply across
the pattern; adding a transient requires checking the curve's effect on it too.

For live interaction, derive bounded dynamic parameters from the current input
and smooth noisy measurements. Standard players support `sendParameters` and
`scheduleParameterCurve`. Use `CHHapticAdvancedPatternPlayer` when looping,
pause/resume, or seeking is needed. Retain players that need later control and
give every sustained effect an explicit stop condition.

## Own the engine in the feature

Check `CHHapticEngine.capabilitiesForHardware().supportsHaptics` before creating
an engine. The iOS 26 deployment target does not replace that check. If unsupported,
continue the interaction without tactile output.

Keep engine, players, and registered resource IDs with a stable feature owner,
not in a SwiftUI view body. Reuse the app's existing owner where suitable. Install
`stoppedHandler` and `resetHandler` before starting the engine. Move callbacks
onto the actor or serial queue that owns mutable playback state; avoid strong
capture cycles. Match the project's Swift concurrency settings rather than
assuming framework callbacks run on the main actor.

| Event | Required owner behavior |
| --- | --- |
| Valid playback request | Check preference and current intent, start the engine as needed, then start a valid player. |
| Interaction ends or cancels | Stop its player and cancel pending starts. Clear any intent to continue. |
| App becomes inactive | Stop sustained interaction feedback; retain only the resources appropriate to the feature's lifecycle. |
| External engine stop | Record the reason and stopped state. Wait for conditions and current input that justify another start. |
| Engine reset | Discard players and resource IDs, restart when appropriate, register custom audio again, and recreate players. |
| Creation, loading, or playback error | Keep diagnostic details and let the user action continue without haptics. Retry on a relevant state change or later valid request. |

Do not replay old events after an interruption or repeatedly restart while the
app is inactive. Restarting alone does not restore resources after reset. Prepare
reusable assets ahead of time-sensitive input and let idle engines stop.

## Author AHAP assets

AHAP stores pattern events and timing in a bundled file. This single transient
is a candidate accent for comparison with the continuous reveal:

```json
{
  "Version": 1.0,
  "Pattern": [
    {
      "Event": {
        "EventType": "HapticTransient",
        "Time": 0.0,
        "EventParameters": [
          { "ParameterID": "HapticIntensity", "ParameterValue": 0.45 },
          { "ParameterID": "HapticSharpness", "ParameterValue": 0.25 }
        ]
      }
    }
  ]
}
```

Resolve the bundled URL, load it with `CHHapticPattern(contentsOf:)`, create a
player through the engine, and start after engine startup succeeds. Check target
membership and report load errors. JSON syntax validation does not prove Core
Haptics can load or play an asset.

For authored sound, add an `AudioCustom` event with its `Time`, an
`EventWaveformPath` for the real bundled audio file, and audio parameters. Verify
paths, supported formats, and current resource limits. Keep haptic-only operation
usable when sound is absent; do not ship a reference to a nonexistent waveform.

## Coordinate output

Put tightly coupled sound and touch in one pattern so they share its timeline.
Align accents to the visual landmarks from the design. Prepare assets before
playback and coordinate the visual sequence with the pattern. Starting calls
together is not proof that their outputs reach the user together.

If separate audio playback is required, use each API's documented timebase.
`AVAudioPlayer.play(atTime:)` uses the audio device timeline from
`deviceCurrentTime`; a Core Haptics player uses its engine timeline.
`CACurrentMediaTime()` is not interchangeable with either. An immediate haptic
and future audio start do not synchronize them.

Preserve the app's audio-session policy. Test actual audio routes, route changes,
and interruptions when timing matters. Pair these checks with physical device
tuning; neither successful loading nor a simulator run establishes tactile feel.

## Sources

- [Engine setup and recovery](https://developer.apple.com/documentation/corehaptics/preparing-your-app-to-play-haptics)
- [Pattern player APIs](https://developer.apple.com/documentation/corehaptics/chhapticpatternplayer)
- [Parameter curves](https://developer.apple.com/documentation/corehaptics/chhapticparametercurve)
- [AHAP format](https://developer.apple.com/documentation/corehaptics/representing-haptic-patterns-in-ahap-files)
- [Audio scheduling](https://developer.apple.com/documentation/avfaudio/avaudioplayer/play(attime:))
