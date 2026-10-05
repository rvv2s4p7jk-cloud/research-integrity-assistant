# Review methodology

Local source comparison uses normalized eight-word shingles. Matched paper token indices are combined in a set before computing percentage, preventing duplicate-source inflation. Quotation and reference masks preserve character offsets. Windows crossing masked quoted text are rejected.

Writing flags are not evidence of AI use. Research alignment is assessed only by the optional LLM using user-supplied context; without it, no alignment evaluation is claimed. Citation flags are pattern-based reminders, not verified reference checks.

No representative academic quality benchmark is yet available. Unit tests validate mechanics, not precision or recall of integrity judgments. Next evaluation steps: independently annotated passages, legitimate quotation and technical-language examples, extraction-quality cases, reference verification against authoritative metadata, and blinded review of model suggestions. Never tune and report quality on the same benchmark without disclosure.

The LLM prompt treats documents as untrusted data. Output validation rejects wrong categories and missing exact quotation evidence. Prompt injection and unsupported reasoning remain possible; human review is required.
