# Designing touch, sound, and motion

Turn the interaction's meaning into a sensation, then select the API that can
express it. The worked designs here are local proposals. Their numbers are
starting points for device comparison, not Apple presets or tested claims.

## Establish a consistent set of responses

| Meaning | First choice in SwiftUI | Design check |
| --- | --- | --- |
| A discrete value changed | `.selection` | Emit for a new step, not each drag sample. |
| Contact or snapping | `.impact` | Match weight and flexibility to the apparent contact. |
| A task succeeded | `.success` | The result must be true when feedback occurs. |
| A decision needs care | `.warning` | Pair with the warning becoming relevant; silence while it simply remains visible. |
| An action failed | `.error` | Show the reason and a way to recover. A drag reaching its limit is not automatically an error. |

Use weight to compare light and heavy impacts, and flexibility to compare soft
and rigid character. These are different choices; rigid is not merely stronger
than heavy. First compare system responses in the actual interaction. Reserve
custom patterns for an expressive need you can name.

Balance feedback across a whole flow. Repeated adjustment steps should not
compete with its final result. A pattern that seems subtle in isolation may
become tiring after twenty uses. Silence between meaningful events helps users
distinguish those events.

## Shape a custom sensation

Draw or describe a timeline before building the pattern. Mark each visual
landmark and the event that supports it. Use only as many haptic events as the
interaction needs.

| Choice | What it controls | Experiment |
| --- | --- | --- |
| Transient | A brief pulse | Start with one pulse at contact. Add another only for a separate accent. |
| Continuous | A sensation with duration | Use when the user should feel a process develop or continue. |
| Intensity | Strength | Compare low and moderate values at the same timing. |
| Sharpness | Soft versus crisp character | Hold intensity steady while comparing character. |
| Envelope | How strength rises and falls | Compare an abrupt beginning with a gradual rise. |
| Spacing | Whether pulses form a rhythm or distinct events | Try the sequence during fast repeated use. |

Core Haptics event intensity and sharpness range from 0 to 1. They are not
physical units, and equal values need not feel equal on different hardware.
Sharpness does not select a precise vibration frequency. Use parameter curves
to shape a continuous event instead of leaving every sustained effect flat.

Patterns can become unclear when dense or repeated. For rapid input, reduce the
number of accents or tie them to meaningful milestones. A continuous texture
may suit ongoing movement; a constant vibration during an uncertain network
wait rarely tells the user anything useful.

## Compose a shared timeline

Identify contact, peak change, and settling in the visual sequence. Align touch
and any sound to these landmarks. The start or completion of an animation API
call may not correspond to the moment the user perceives contact.

Match character as well as timing. A sharp contact can pair with a short sound
with a clear attack. A smooth expansion can pair with a rising haptic envelope
and a sound that grows with it. Let the event's significance or force guide
strength; sound volume alone should not decide haptic intensity.

Sound and touch can have different shapes while sharing accents. Do not assume
the haptic should copy the audio waveform. Judge each output alone, then the
whole interaction. When sound is optional, the visual and tactile result must
still make sense with sound off.

## Worked designs

### Save: communicate a real outcome

The event is a successful save, not the tap that requested it. Use `.success`
when the operation confirms the result, alongside the saved state. Use `.error`
with a recoverable failure. The spinner needs no repeated pulse.

Represent each completion as a new event so two successful saves both produce
feedback. Decide whether a result still belongs to the active UI if the user
leaves while saving. Test fast and slow saves, consecutive saves, and cancellation.
If feedback feels disconnected, fix the state transition before its strength.
The [SwiftUI example](swiftui-feedback.md) consumes these outcome events.

### Snap: make a useful alignment detectable

A crop handle enters alignment and the guide appears. Start with a light impact
or compare a rigid impact if the contact should feel firm. Use `.selection` for
a control with several equal steps. Sound may add little to an editing tool.

Emit on entry into alignment. Require movement beyond a slightly wider release
boundary before the snap can occur again; this prevents tiny movements near the
edge from causing repeated feedback. Test approach, reversal, and rapid dragging.
Use SwiftUI first. If distinct direct events need tighter control than view
updates provide, use the UIKit path described in the implementation reference.

### Reveal: let the user feel a transformation

Suppose an object expands for 240 ms and settles for 80 ms. Compare a single
system impact at the settling point with this custom candidate:

| Time | Visual | Touch | Optional sound |
| --- | --- | --- | --- |
| 0–240 ms | Expansion | Continuous event at sharpness 0.25, intensity rising from 0.10 to 0.45 | Soft rise reaching its accent with the visual peak |
| 240–320 ms | Settling | Intensity falls to zero | Short decay |

Keep the custom version if feeling the growth adds value. If the finish lacks
clarity, compare a small transient at the peak, checking that it adds meaning
rather than excess force. The [custom playback reference](core-haptics.md)
implements the continuous candidate. Match a reduced-motion version to its
actual visual change instead of retaining this duration by habit.

### Texture: make movement perceptible

For a surface with widely spaced marks, emit transients as the object crosses
them. Derive crossings from distance, so speed changes cadence and a stationary
object produces none. For dense texture, compare a continuous effect whose
strength follows movement through smooth, bounded updates.

Tie any sound to the same movement state. Stop when contact or movement ends,
on cancellation, and when the app becomes inactive. Test slow movement, fast
movement, and reversal. If it becomes tiring, lower density or intensity before
adding complexity.

## Sources

- [Apple's design and iteration example](https://developer.apple.com/videos/play/wwdc2021/10278/)
- [Apple's sound and touch discussion](https://developer.apple.com/videos/play/wwdc2019/223/)
- [Sharpness](https://developer.apple.com/documentation/corehaptics/chhapticevent/parameterid/hapticsharpness)
- [Parameter curves](https://developer.apple.com/documentation/corehaptics/chhapticparametercurve)
