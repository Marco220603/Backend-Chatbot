from django.core.management.base import BaseCommand
from api.models import FeedbackGPT
from pathlib import Path

class Command(BaseCommand):
    help = 'Exporta feedback aprobado a un archivo NLU para Rasa'

    def handle(self, *args, **kwargs):
        export_path = Path('data/generated_nlu.yml')
        export_path.parent.mkdir(parents=True, exist_ok=True)

        approved_feedbacks = FeedbackGPT.objects.filter(status='approved')

        if not approved_feedbacks.exists():
            self.stdout.write(self.style.WARNING("No hay feedbacks aprobados para exportar."))
            return

        intent_examples = [f"- {feedback.user_message.strip()}" for feedback in approved_feedbacks]

        with open(export_path, 'w', encoding='utf-8') as file:
            file.write("version: \"3.1\"\n\n")
            file.write("- intent: auto_generated_intent\n")
            file.write("  examples: |\n")
            for example in intent_examples:
                file.write(f"    {example}\n")

        self.stdout.write(self.style.SUCCESS(f'Se exportaron {len(intent_examples)} ejemplos a {export_path}'))
