import os
import re
from google.cloud import translate_v2 as translate
from typing import Optional
from openai import OpenAI

# Ensure GOOGLE_APPLICATION_CREDENTIALS environment variable is set
# to the path of your service account key file.

class TranslationService:
    def __init__(self):
        self.google_client = None
        self.openai_client = None

        # Try to initialize Google Translate client
        if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            try:
                self.google_client = translate.Client()
                print("TranslationService initialized with Google Cloud Translate.")
            except Exception as e:
                print(f"Failed to initialize Google Translate: {e}")

        # Try to initialize OpenAI client as fallback
        if os.getenv("OPENAI_API_KEY"):
            try:
                self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                print("OpenAI client available as translation fallback.")
            except Exception as e:
                print(f"Failed to initialize OpenAI client: {e}")

        if not self.google_client and not self.openai_client:
            print("TranslationService initialized in mock mode (no credentials available).")

    def _extract_code_blocks(self, text: str) -> list[tuple[str, str]]:
        """Extract code blocks from markdown text."""
        pattern = r'(```[\w]*\n.*?\n```)'
        code_blocks = re.findall(pattern, text, re.DOTALL)
        return [(f"__CODE_BLOCK_{i}__", block) for i, block in enumerate(code_blocks)]

    def _remove_code_blocks(self, text: str, code_blocks: list[tuple[str, str]]) -> str:
        """Replace code blocks with placeholders."""
        result = text
        for placeholder, block in code_blocks:
            result = result.replace(block, placeholder)
        return result

    def _restore_code_blocks(self, text: str, code_blocks: list[tuple[str, str]]) -> str:
        """Restore code blocks from placeholders."""
        result = text
        for placeholder, block in code_blocks:
            result = result.replace(placeholder, block)
        return result

    async def translate_text(self, text: str, target_language: str = "ur") -> Optional[str]:
        """
        Translates text to the target language.
        Tries Google Translate first, falls back to OpenAI, then mock.
        """
        if not text:
            return None

        # Extract code blocks to preserve them
        code_blocks = self._extract_code_blocks(text)
        text_without_code = self._remove_code_blocks(text, code_blocks)

        try:
            # Try Google Translate first
            if self.google_client:
                result = self.google_client.translate(
                    text_without_code,
                    target_language=target_language,
                    source_language='en'
                )
                translated_text = result['translatedText']
                # Restore code blocks
                translated_text = self._restore_code_blocks(translated_text, code_blocks)
                return translated_text

            # Fall back to OpenAI
            elif self.openai_client:
                language_names = {
                    'ur': 'Urdu',
                    'ar': 'Arabic',
                    'hi': 'Hindi',
                    'es': 'Spanish',
                    'fr': 'French'
                }
                target_lang_name = language_names.get(target_language, target_language)

                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": f"You are a professional translator. Translate the following English text to {target_lang_name}. Preserve markdown formatting. Only return the translated text, no explanations."
                        },
                        {
                            "role": "user",
                            "content": text_without_code
                        }
                    ],
                    temperature=0.3
                )
                translated_text = response.choices[0].message.content
                # Restore code blocks
                translated_text = self._restore_code_blocks(translated_text, code_blocks)
                return translated_text

            # Mock response if no clients available
            else:
                print("No translation service available. Returning mock translation.")
                return f"[MOCK TRANSLATION] {text[:100]}... (to {target_language})"

        except Exception as e:
            print(f"Error during translation: {e}")
            return None

# Singleton instance of the service
translation_service = TranslationService()
