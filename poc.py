import argparse
import json
import sys
import urllib.error
import urllib.request

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("base_url", help="DbGate base URL")
    parser.add_argument("--token", required=True, help="Bearer token for the authenticated test user")
    parser.add_argument("--sesid", help="Previously observed lab session ID instead of listening to /stream")
    parser.add_argument("--query", default="SELECT 1,2,3", help="SQL Query")
    parser.add_argument("--timeout", type=float, default=60, help="SSE observation timeout in seconds")
    parser.add_argument("--color", choices=("auto", "always", "never"), default="auto")
    args = parser.parse_args()

    color = args.color == "always" or (args.color == "auto" and sys.stdout.isatty())

    def tag(value: str, code: str) -> str:
        return f"\033[{code}m{value}\033[0m" if color else value

    base = args.base_url.rstrip("/")
    sesid = args.sesid

    if sesid:
        print(f"{tag('[*]', '32')} Using supplied sesid: {sesid}")
    else:
        url = f"{base}/stream"
        print(f"{tag('[?]', '36')} Requesting endpoint: {url}")

        try:
            with urllib.request.urlopen(url, timeout=args.timeout) as response:
                for line in response:
                    decoded = line.decode("utf-8", errors="replace").rstrip("\r\n")
                    if not decoded.startswith("data:"):
                        continue
                    print(f"{tag('[#]', '33')} EVENT {decoded}")
                    if "sesid" in decoded:
                        payload = decoded[5:].strip()
                        try:
                            sesid = json.loads(payload)["sesid"]
                            break
                        except (json.JSONDecodeError, KeyError):
                            continue
        except KeyboardInterrupt:
            print(f"\n{tag('[!]', '31')} Interrupted.", file=sys.stderr)
            return 130
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            print(f"{tag('[!]', '31')} Connection failed: {exc}", file=sys.stderr)
            return 2

    if sesid is not None:
        print(f"{tag('[*]', '32')} sesid: {sesid}")
        endpoint = f"{base}/sessions/execute-query"
        body = json.dumps({"sesid": sesid, "sql": args.query, "autoCommit": False}).encode("utf-8")
        request = urllib.request.Request(
            endpoint,
            data=body,
            headers={
                "Authorization": f"Bearer {args.token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        print(f"{tag('[?]', '36')} Submitting {endpoint}")
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                result = response.read().decode("utf-8", errors="replace")
                print(f"{tag('[+]', '32')} HTTP {response.status}: {result}")
                return 0 if response.status < 300 else 1
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            print(f"{tag('[!]', '31')} Query request failed: HTTP {exc.code}: {detail}", file=sys.stderr)
            return 1
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            print(f"{tag('[!]', '31')} Query request failed: {exc}", file=sys.stderr)
            return 1

    print(f"{tag('[!]', '31')} No event containing sesid was received.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
