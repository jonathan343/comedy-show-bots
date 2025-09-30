import json
import boto3
from typing import List, Dict, Any


class LLMExtractor:
    """Extracts structured comedy show data from HTML using AWS Bedrock."""

    def __init__(self, model_id: str = "global.anthropic.claude-sonnet-4-5-20250929-v1:0"):
        """
        Initialize the LLM extractor.

        Args:
            model_id: The Bedrock model ID to use for extraction
        """
        self.bedrock = boto3.client("bedrock-runtime")
        self.model_id = model_id

    def extract_shows(self, html: str, venue_name: str) -> List[Dict[str, Any]]:
        """
        Extract show information from HTML using LLM.

        Args:
            html: Cleaned HTML containing show information
            venue_name: Name of the venue for context

        Returns:
            List of show dictionaries with structure:
            [{
                "date": "YYYY-MM-DD",
                "time": "HH:MM AM/PM",
                "venue_location": "room/stage name if mentioned",
                "comedians": ["Name 1", "Name 2", ...],
                "show_url": "/path/to/show"
            }]
        """
        prompt = self._build_extraction_prompt(html, venue_name)

        try:
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps(
                    {
                        "anthropic_version": "bedrock-2023-05-31",
                        "max_tokens": 4096,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0,
                    }
                ),
            )

            response_body = json.loads(response["body"].read())
            content = response_body["content"][0]["text"]

            # Extract JSON from potential markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            shows_data = json.loads(content)

            # Handle both {shows: [...]} and [...] formats
            if isinstance(shows_data, dict) and "shows" in shows_data:
                return shows_data["shows"]
            return shows_data

        except Exception as e:
            print(f"Error extracting shows with LLM: {e}")
            return []

    def _build_extraction_prompt(self, html: str, venue_name: str) -> str:
        """Build the prompt for the LLM to extract show information."""
        return f"""Extract comedy show information from this {venue_name} HTML.

Return a JSON array with this exact structure:
[{{
  "date": "YYYY-MM-DD",
  "time": "HH:MM AM/PM",
  "venue_location": "specific room/stage if mentioned (e.g., 'Upstairs', 'Main room')",
  "comedians": ["Full Name 1", "Full Name 2", ...],
  "show_url": "/path/to/show/page"
}}]

Important rules:
1. Extract FULL comedian names (first and last names)
2. Parse dates and convert to YYYY-MM-DD format
3. Extract all individual comedian names - split on commas, "&", "and", etc.
4. If you see "& More!" or similar, OMIT it - only list named comedians
5. Include venue location if multiple rooms/stages are mentioned
6. Return ONLY valid JSON, no markdown or explanation

HTML:
{html}"""