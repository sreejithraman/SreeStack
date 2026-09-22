# Remote Images

Model loading, failure, and the rendered image as distinct states. Preserve the
product's existing image pipeline when it supplies transforms, authentication,
prefetching, decoded-image caching, or observability that `AsyncImage` does not.

## Use OS 27 caching correctly

On OS 27, existing `AsyncImage(url:)` calls cache downloaded data according to
the transport protocol and server cache headers. This is runtime behavior and
does not require a source change. It does not promise a cache of decoded SwiftUI
`Image` values or permission to ignore HTTP freshness.

When the deployment target supports OS 27 APIs:

- use `AsyncImage(request:)` to choose a `URLRequest` cache policy or other
  request properties for one image;
- use `.asyncImageURLSession(_:)` on an ancestor to provide the session used by
  descendant `AsyncImage` download tasks; and
- configure that session's `URLCache` when the feature needs explicit memory or
  disk capacity.

The request initializers and session modifier are available on iOS, macOS,
watchOS, tvOS, and visionOS 27. The no-closure initializer takes a nonoptional
request; the placeholder and phase variants accept an optional request. See
Apple's [`AsyncImage`](https://developer.apple.com/documentation/swiftui/asyncimage)
and [`asyncImageURLSession`](https://developer.apple.com/documentation/swiftui/view/asyncimageurlsession%28_%3A%29)
documentation.

Test a cold load, a protocol-valid cached load, an expired response, failure,
cancellation during reuse or scrolling, and the product's offline behavior.
