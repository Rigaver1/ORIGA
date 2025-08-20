import argparse
import json
import sys
from typing import Iterable, List, Optional

from .models import Product
from .http_client import fetch_page
from .parser import parse_product


def _iter_input_urls(urls: List[str], from_file: Optional[str]) -> Iterable[str]:
	seen = set()
	for url in urls:
		url = url.strip()
		if not url:
			continue
		if url in seen:
			continue
		seen.add(url)
		yield url
	if from_file:
		with open(from_file, "r", encoding="utf-8") as fh:
			for line in fh:
				u = line.strip()
				if not u or u.startswith("#"):
					continue
				if u in seen:
					continue
				seen.add(u)
				yield u


def _dump(obj) -> str:
	if isinstance(obj, Product):
		return json.dumps(obj.model_dump(mode="json"), ensure_ascii=False)
	return json.dumps(obj, ensure_ascii=False)


def build_arg_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(
		prog="aliyun1688parser",
		description="Parse 1688 product pages and print JSON with cargo-relevant fields",
	)
	parser.add_argument("urls", nargs="*", help="1688 product URLs")
	parser.add_argument("--from-file", dest="from_file", help="Path to file with URLs (one per line)")
	parser.add_argument("--browser", action="store_true", help="Use Playwright when static parse is weak or blocked")
	parser.add_argument("--timeout", type=int, default=25, help="Request/page timeout in seconds")
	parser.add_argument("--proxy", type=str, default=None, help="HTTP(S) proxy, e.g., http://user:pass@host:port")
	parser.add_argument("--out", type=str, default=None, help="Output file path (defaults to stdout)")
	parser.add_argument("--ndjson", action="store_true", help="Emit NDJSON (one JSON per line) instead of array")
	parser.add_argument("--verbose", action="store_true", help="Verbose logging to stderr")
	return parser


def main(argv: Optional[List[str]] = None) -> int:
	args = build_arg_parser().parse_args(argv)

	urls = list(_iter_input_urls(args.urls, args.from_file))
	if not urls:
		print("No URLs provided", file=sys.stderr)
		return 2

	def verbose(msg: str) -> None:
		if args.verbose:
			print(msg, file=sys.stderr)

	results: List[Product] = []

	proxies = None
	if args.proxy:
		proxies = {"http": args.proxy, "https": args.proxy}

	for url in urls:
		try:
			verbose(f"Fetching (static): {url}")
			html = fetch_page(url=url, timeout=args.timeout, proxies=proxies)
			product = parse_product(html=html, url=url, timeout=args.timeout, proxies=proxies)
			weak = not (product.title and (product.price_tiers or product.sku_list or product.min_order))
			if args.browser and weak:
				try:
					verbose(f"Static parse weak, trying browser: {url}")
					from .browser import render_page
					html2 = render_page(url=url, timeout=args.timeout, proxy=args.proxy)
					product = parse_product(html=html2, url=url, timeout=args.timeout, proxies=proxies)
				except Exception as be:  # noqa: BLE001
					verbose(f"Browser render failed: {be}")
			results.append(product)
		except Exception as e:  # noqa: BLE001
			verbose(f"Failed to parse {url}: {e}")
			results.append(Product(url=url, extra={"error": str(e)}))

	# Emit output
	if args.ndjson:
		lines = [
			_dump(r)
			for r in results
		]
		data = "\n".join(lines) + "\n"
	else:
		data = json.dumps([r.model_dump(mode="json") for r in results], ensure_ascii=False)

	if args.out:
		with open(args.out, "w", encoding="utf-8") as fh:
			fh.write(data)
	else:
		print(data)

	return 0


if __name__ == "__main__":
	sys.exit(main())

