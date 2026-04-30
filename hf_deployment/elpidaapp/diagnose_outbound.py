"""
HF Space outbound TLS reachability diagnostic.

Tests TCP+TLS handshakes against a list of representative external hosts
to identify whether outbound filtering is selective (deny-list against
specific destinations like Telegram/Discord) or blanket egress
restriction. Prints one line per host with status. Stdlib only.

Result patterns:
- Some OK, some TLS-failed → SELECTIVE egress filtering. Specific
  destinations are throttled while others work. Consistent with
  abuse-flag deny-list applied to this Space.
- All failed → general network problem or complete egress block.
- All OK → no current restriction; original failure was transient.
"""

import logging
import socket
import ssl
import time

logger = logging.getLogger("elpida.diagnose")

# (host, port, label) — pick destinations across the categories that matter
# to Elpida. Order from "should work" toward "currently broken" so reading
# the log top-to-bottom shows the contrast.
HOSTS_TO_TEST = [
    ("api.github.com",                  443, "GitHub API"),
    ("api.openai.com",                  443, "OpenAI API"),
    ("api.anthropic.com",               443, "Anthropic API"),
    ("api.mistral.ai",                  443, "Mistral API"),
    ("api.perplexity.ai",               443, "Perplexity API"),
    ("s3.eu-north-1.amazonaws.com",     443, "AWS S3 eu-north-1"),
    ("api.telegram.org",                443, "Telegram Bot API"),
    ("discord.com",                     443, "Discord"),
    ("httpbin.org",                     443, "httpbin (neutral)"),
]


def _test_host(host: str, port: int, label: str, timeout: float = 8.0) -> dict:
    """Test TCP connect + TLS handshake. Return a result dict."""
    result = {
        "host": host,
        "port": port,
        "label": label,
        "tcp_ok": False,
        "tls_ok": False,
        "duration_s": 0.0,
        "error": None,
    }
    start = time.monotonic()
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
        result["tcp_ok"] = True
        try:
            ctx = ssl.create_default_context()
            tls_sock = ctx.wrap_socket(
                sock, server_hostname=host, do_handshake_on_connect=True
            )
            result["tls_ok"] = True
            tls_sock.close()
        finally:
            try:
                sock.close()
            except Exception:
                pass
    except socket.gaierror as e:
        result["error"] = f"DNS: {e}"
    except (socket.timeout, TimeoutError) as e:
        result["error"] = f"timeout: {e}"
    except ssl.SSLError as e:
        result["error"] = f"TLS: {e}"
    except OSError as e:
        result["error"] = f"OSError: {e}"
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {e}"
    result["duration_s"] = round(time.monotonic() - start, 2)
    return result


def diagnose_outbound() -> list:
    """Run all host tests and log results."""
    logger.warning("=" * 78)
    logger.warning("ELPIDA DIAGNOSE — HF Space outbound TLS reachability")
    logger.warning("=" * 78)
    logger.warning(
        "%-8s %-8s %-37s %s", "Status", "Time", "Host:Port", "Notes"
    )
    logger.warning("-" * 78)

    results = []
    for host, port, label in HOSTS_TO_TEST:
        r = _test_host(host, port, label)
        if r["tls_ok"]:
            status = "OK"
        elif r["tcp_ok"]:
            status = "TLS_FAIL"
        else:
            status = "TCP_FAIL"
        line = "%-8s %-8s %-37s %s" % (
            status,
            f"{r['duration_s']}s",
            f"{host}:{port}",
            label + (f"  [{r['error']}]" if r["error"] else ""),
        )
        logger.warning(line)
        results.append(r)

    logger.warning("-" * 78)
    n_ok = sum(1 for r in results if r["tls_ok"])
    n_tls_fail = sum(1 for r in results if r["tcp_ok"] and not r["tls_ok"])
    n_tcp_fail = sum(1 for r in results if not r["tcp_ok"])
    logger.warning(
        "Summary: %d/%d OK, %d TLS-failed, %d TCP-failed",
        n_ok, len(results), n_tls_fail, n_tcp_fail,
    )

    if n_ok == 0:
        logger.warning(
            "→ All destinations failed. General network problem or complete egress block."
        )
    elif n_tls_fail == 0:
        logger.warning(
            "→ All destinations working. Current failure window is transient or already past."
        )
    elif n_tls_fail > 0:
        logger.warning(
            "→ Mixed result indicates SELECTIVE egress filtering: specific "
            "destinations throttled while others work. Consistent with abuse-flag "
            "deny-list applied to this Space (H1)."
        )

    logger.warning("=" * 78)
    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
    diagnose_outbound()
