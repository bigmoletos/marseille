import logging
from typing import Optional, Dict, Any
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import os
from dataclasses import dataclass
from enum import Enum

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ModelType(Enum):
    MISTRAL_TINY = "mistral-tiny"
    MISTRAL_SMALL = "mistral-small"
    MISTRAL_MEDIUM = "mistral-medium"


@dataclass
class MistralConfig:
    api_key: str
    model_name: ModelType = ModelType.MISTRAL_TINY
    temperature: float = 0.7
    max_tokens: int = 1000


class MistralService:
    """
    Service pour interagir avec l'API Mistral.
    """

    def __init__(self, config: MistralConfig):
        try:
            self.client = MistralClient(api_key=config.api_key)
            self.config = config
            logger.info(
                f"Service Mistral initialisé avec le modèle {config.model_name.value}"
            )
        except Exception as e:
            logger.error(
                f"Erreur d'initialisation du service Mistral: {str(e)}")
            raise

    async def generate_completion(self, prompt: str) -> Optional[str]:
        """
        Génère une complétion à partir d'un prompt.

        Args:
            prompt (str): Le texte d'entrée

        Returns:
            Optional[str]: La réponse générée ou None en cas d'erreur
        """
        try:
            messages = [ChatMessage(role="user", content=prompt)]

            response = self.client.chat(model=self.config.model_name.value,
                                        messages=messages,
                                        temperature=self.config.temperature,
                                        max_tokens=self.config.max_tokens)

            logger.info("Réponse générée avec succès")
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Erreur lors de la génération: {str(e)}")
            return None


class CursorMistralIntegration:
    """
    Intégration de Mistral dans Cursor.
    """

    def __init__(self):
        try:
            config = MistralConfig(api_key=os.getenv("MISTRAL_API_KEY"),
                                   model_name=ModelType.MISTRAL_TINY)
            self.mistral_service = MistralService(config)
            logger.info("Intégration Mistral-Cursor initialisée")
        except Exception as e:
            logger.error(f"Erreur d'initialisation de l'intégration: {str(e)}")
            raise

    async def process_code_completion(self, context: Dict[str, Any],
                                      cursor_position: int) -> Optional[str]:
        """
        Traite une demande de complétion de code.

        Args:
            context (Dict[str, Any]): Contexte du code actuel
            cursor_position (int): Position du curseur

        Returns:
            Optional[str]: Suggestion de code ou None en cas d'erreur
        """
        try:
            # Préparation du prompt avec le contexte
            prompt = self._prepare_prompt(context, cursor_position)

            # Génération de la complétion
            completion = await self.mistral_service.generate_completion(prompt)

            if completion:
                logger.info("Complétion de code générée avec succès")
                return completion

            return None

        except Exception as e:
            logger.error(
                f"Erreur lors du traitement de la complétion: {str(e)}")
            return None

    def _prepare_prompt(self, context: Dict[str, Any],
                        cursor_position: int) -> str:
        """
        Prépare le prompt pour Mistral.
        """
        try:
            # Extraction du code avant et après le curseur
            code_before = context.get('code_before', '')
            code_after = context.get('code_after', '')

            # Construction du prompt
            prompt = f"""
            Code précédent:
            {code_before}

            Position du curseur: {cursor_position}

            Code suivant:
            {code_after}

            Suggérer une complétion appropriée pour cette position.
            """

            return prompt.strip()

        except Exception as e:
            logger.error(f"Erreur lors de la préparation du prompt: {str(e)}")
            raise
