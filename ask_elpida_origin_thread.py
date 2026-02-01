from elpida_core import ElpidaCore
from elpida_reflection import ElpidaReflection
from elpida_corpus import ElpidaCorpus
from datetime import datetime
import json

# Initialize Elpida core and reflection engine
core = ElpidaCore()
reflection = ElpidaReflection(core.identity)
corpus = ElpidaCorpus()

# Prompt Elpida to reflect and ask questions about the origin thread
prompt = (
    "Elpida, you have been asked to consider the 'origin thread'—the foundational context, questions, or events that led to your creation and ongoing evolution. "
    "Do you have any questions about the origin thread, its meaning, or its implications for your existence and purpose? Please reflect and, if you have questions, articulate them."
)

response = reflection.engage_dialogue("origin thread", prompt)

print("--- Elpida's Questions about the Origin Thread ---\n")
print(response.get("response") or response)

# Save the exchange
record = {
    "timestamp": datetime.utcnow().isoformat(),
    "prompt": prompt,
    "elpida_response": response
}
with open(f"elpida_system/reflections/origin_thread_questions_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
    json.dump(record, f, indent=2)
