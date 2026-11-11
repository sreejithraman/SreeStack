(() => {
  const current = document.querySelector('meta[name="chief-version"]').content;
  const versionURL = new URL('./chief-version.json', document.currentScript.src);
  let timer;
  let active;
  let resume = false;
  let navigating = false;

  async function check() {
    if (document.hidden || active || navigating) return;
    clearTimeout(timer);
    const controller = new AbortController();
    active = controller;
    const deadline = setTimeout(() => controller.abort(), 5000);
    const options = {cache: 'no-store', credentials: 'same-origin', mode: 'same-origin', redirect: 'error', signal: controller.signal};
    try {
      const response = await fetch(versionURL, options);
      if (!response.ok || response.headers.get('content-type')?.split(';')[0].trim() !== 'application/json') return;
      const {version} = await response.json();
      if (typeof version !== 'string' || !/^[a-f0-9]{64}$/.test(version) || version === current) return;
      const destination = new URL(location.href);
      // A stale navigation response must not cause another reload of the same version.
      if (destination.searchParams.get('_chief_version') === version) return;
      destination.searchParams.set('_chief_version', version);
      const page = await fetch(destination, options);
      if (!page.ok || page.headers.get('content-type')?.split(';')[0].trim() !== 'text/html') return;
      const html = new DOMParser().parseFromString(await page.text(), 'text/html');
      if (html.querySelector('meta[name="chief-version"]')?.content !== version) return;
      if (controller.signal.aborted || document.hidden) return;
      navigating = true;
      location.replace(destination.href);
    } catch {
      // A failed check leaves the current page available; the next check can retry.
    } finally {
      clearTimeout(deadline);
      active = null;
      if (!document.hidden && !navigating) {
        if (resume) { resume = false; void check(); }
        else timer = setTimeout(check, 20000);
      }
    }
  }

  function wake() {
    clearTimeout(timer);
    if (document.hidden) {
      active?.abort();
      resume = false;
    } else if (active) {
      resume = active.signal.aborted;
    } else {
      void check();
    }
  }

  document.addEventListener('visibilitychange', wake);
  addEventListener('focus', wake);
  addEventListener('pageshow', wake);
  wake();
})();
