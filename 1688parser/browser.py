from __future__ import annotations

from typing import Optional


def render_page(url: str, timeout: int = 25, proxy: Optional[str] = None) -> str:
	"""Render page with Playwright (Chromium) and return HTML.

	Requires optional dependency: playwright

	Args:
		url: Target URL
		timeout: Timeout in seconds
		proxy: Optional proxy string

	Returns:
		Final page content (HTML)
	"""
	try:
		from playwright.sync_api import Playwright, sync_playwright
	except Exception as e:  # noqa: BLE001
		raise RuntimeError("Playwright is not installed. Install with: pip install .[browser]") from e

	def _run(play: Playwright) -> str:
		browser = play.chromium.launch(
			headless=True,
			proxy={"server": proxy} if proxy else None,
		)
		context = browser.new_context(
			user_agent=(
				"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
				"(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
			),
			locale="zh-CN",
		)
		page = context.new_page()
		page.set_default_timeout(timeout * 1000)
		page.goto(url, wait_until="networkidle")
		content = page.content()
		context.close()
		browser.close()
		return content

	with sync_playwright() as p:
		return _run(p)

