from __future__ import annotations

import random
import time
from typing import Dict, Optional

import requests


DEFAULT_HEADERS = {
	"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
	"accept-language": "zh-CN,zh;q=0.9,en;q=0.8,ru;q=0.7",
	"cache-control": "no-cache",
	"pragma": "no-cache",
	"upgrade-insecure-requests": "1",
	"user-agent": (
		"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
		"(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
	),
}


def fetch_page(url: str, timeout: int = 25, proxies: Optional[Dict[str, str]] = None) -> str:
	"""Fetch raw HTML from URL using requests with realistic headers.

	Args:
		url: Page URL
		timeout: Timeout in seconds
		proxies: Optional requests-style proxies dict

	Returns:
		HTML text
	"""
	session = requests.Session()
	session.headers.update(DEFAULT_HEADERS)
	resp = session.get(url, timeout=timeout, proxies=proxies, allow_redirects=True)
	resp.raise_for_status()
	# Small jitter to be polite
	time.sleep(random.uniform(0.2, 0.5))
	return resp.text

