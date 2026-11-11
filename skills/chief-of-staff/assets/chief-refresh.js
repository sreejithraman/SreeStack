(() => {
  const current = document.querySelector('meta[name="chief-version"]').content;
  const versionURL = new URL('./chief-version.json', location.href);
  let timer;
  let active;
  let resume = false;
  let replaced = false;

  async function check() {
    if (document.hidden || active || replaced) return;
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
      destination.searchParams.set('_chief_version', version);
      const page = await fetch(destination, options);
      if (!page.ok || page.headers.get('content-type')?.split(';')[0].trim() !== 'text/html') return;
      const text = await page.text();
      const html = new DOMParser().parseFromString(text, 'text/html');
      if (html.querySelector('meta[name="chief-version"]')?.content !== version) return;
      if (controller.signal.aborted || document.hidden) return;
      document.dispatchEvent(new Event('chief:replace'));
      document.open();
      document.write(text);
      document.close();
      replaced = true;
    } catch {
      // A failed check leaves the current page available; the next check can retry.
    } finally {
      clearTimeout(deadline);
      active = null;
      if (!document.hidden && !replaced) {
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
  if (document.readyState === 'loading') addEventListener('DOMContentLoaded', wake, {once: true});
  else wake();
})();
