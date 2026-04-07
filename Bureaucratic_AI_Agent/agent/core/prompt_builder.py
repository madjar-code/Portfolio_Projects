import json
from models import TaskMessage
from core.prompt_version_registry import PromptVersionRegistry, prompt_version_registry

_OUTPUT_SCHEMA = {
    "decision": "ACCEPT or REJECT",
    "validation_result": {
        "description": "object with validation checks and outcomes"
    },
    "extracted_data": {
        "description": "key fields extracted from the document"
    },
    "issues_found": [
        {"type": "string", "detail": "string", "severity": "critical|warning"}
    ],
    "recommendations": "string — human-readable summary of findings",
    "processing_time_seconds": "integer",
    "ai_model_used": "string — model identifier used",
}


class PromptBuilder:
    def __init__(self, registry: PromptVersionRegistry) -> None:
        self._registry = registry

    def build(
        self,
        task: TaskMessage,
        instructions: str,
        version: str,
    ) -> list[dict[str, str]]:
        """
        Returns messages[] ready for model.ainvoke():
        [{"role": "system", ...}, {"role": "user", ...}]
        """
        system_prompt = self._registry.load(version)
        user_message = self._build_user_message(task, instructions)
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

    def _build_user_message(self, task: TaskMessage, instructions: str) -> str:
        doc_block = self._format_document(task)
        return (
            f"## Procedure Instructions\n{instructions}\n\n"
            "---\n\n"
            "## Application Data\n\n"
            f"**Application ID:** {task.application_id}\n"
            f"**Procedure:** {task.procedure}\n\n"
            "### Form Data\n"
            f"```json\n{json.dumps(task.form_data, indent=2, ensure_ascii=False)}\n```\n\n"
            f"{doc_block}\n\n"
            "---\n\n"
            "## Required Output Schema\n\n"
            "Return a JSON object with exactly these fields:\n"
            f"```json\n{json.dumps(_OUTPUT_SCHEMA, indent=2)}\n```"
        )

    def _format_document(self, task: TaskMessage) -> str:
        if task.document is None:
            return "### Submitted Document\nNo document was provided with this application."
        doc = task.document
        size = f"{doc.file_size} bytes" if doc.file_size else "unknown"
        return (
            "### Submitted Document\n"
            f"- Filename: {doc.file_name}\n"
            f"- Format:   {doc.file_format}\n"
            f"- Size:     {size}\n"
            f"- URL:      {doc.file_url}\n\n"
            "Use tools to read the document content as needed."
        )

prompt_builder = PromptBuilder(registry=prompt_version_registry)
