"""
Replicate Vision — generates visual representations of Live Audit synthesis.

Takes the synthesis output, fault lines, and domain tensions from a
Divergence Engine run and produces an abstract visual via Replicate Flux.
"""

import os
import time
import replicate


def _build_prompt(synthesis: str, fault_lines: list, consensus: list, problem: str) -> str:
    """Convert governance synthesis into a Flux image prompt."""
    # Extract key tensions
    tension_phrases = []
    for fl in fault_lines[:3]:
        topic = fl.get("topic", "")
        sides = fl.get("sides", [])
        if len(sides) >= 2:
            tension_phrases.append(
                f"{sides[0].get('stance', '')[:40]} versus {sides[1].get('stance', '')[:40]}"
            )
        elif topic:
            tension_phrases.append(topic)

    consensus_count = len(consensus)
    fault_count = len(fault_lines)

    # Build an abstract art prompt — NOT literal, but metaphorical
    tension_fragment = "; ".join(tension_phrases[:3]) if tension_phrases else "hidden tensions beneath calm surface"

    prompt = (
        f"Abstract expressionist digital painting. "
        f"A luminous philosophical landscape representing a complex decision: "
        f"'{problem[:80]}'. "
        f"{fault_count} visible fault lines crack through the composition — "
        f"representing: {tension_fragment}. "
        f"{consensus_count} golden threads of consensus weave through the fractures, "
        f"holding the structure together. "
        f"Color palette: deep indigo, electric violet, amber gold, midnight blue. "
        f"Style: ethereal, layered, architectural yet organic. "
        f"No text, no words, no letters. Cinematic lighting, 8k detail."
    )
    return prompt


def generate_vision(result: dict, problem: str) -> dict:
    """
    Generate a visual representation of a Live Audit result.

    Args:
        result: Full DivergenceEngine.analyze() output
        problem: The original problem statement

    Returns:
        {"image_url": str, "prompt": str, "latency_s": float}
        or {"error": str} on failure
    """
    token = os.getenv("REPLICATE_API_TOKEN", "").strip()
    if not token:
        return {"error": "REPLICATE_API_TOKEN not set"}
    os.environ["REPLICATE_API_TOKEN"] = token  # write back stripped value

    synthesis = result.get("synthesis", {})
    divergence = result.get("divergence", {})
    fault_lines = divergence.get("fault_lines", [])
    consensus = divergence.get("consensus", [])
    synthesis_text = synthesis.get("output", "")

    prompt = _build_prompt(synthesis_text, fault_lines, consensus, problem)

    t0 = time.time()
    try:
        output = replicate.run(
            "black-forest-labs/flux-schnell",
            input={
                "prompt": prompt,
                "num_outputs": 1,
                "aspect_ratio": "16:9",
                "output_format": "webp",
                "output_quality": 90,
            },
        )
        # Flux returns a list of FileOutput objects
        image_url = None
        if output:
            first = output[0] if isinstance(output, list) else output
            image_url = str(first)

        latency = round(time.time() - t0, 1)

        if not image_url:
            return {"error": "No image returned from Replicate"}

        return {
            "image_url": image_url,
            "prompt": prompt,
            "latency_s": latency,
        }

    except Exception as exc:
        return {"error": f"Replicate call failed: {exc}"}
