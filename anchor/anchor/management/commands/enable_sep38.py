from django.core.management.base import BaseCommand
from polaris.models import Asset

class Command(BaseCommand):
    help = 'Enables SEP-38 protocol for specific assets'

    def handle(self, *args, **options):
        # Fetching assets by their respective codes
        afro = Asset.objects.filter(code="AFRO").first()
        cnb = Asset.objects.filter(code="CNB").first()
        life = Asset.objects.filter(code="LIFE").first()

        # Enabling SEP-38 protocol for the specified assets if they exist
        if afro:
            afro.sep38_enabled = True
            afro.save()
            self.stdout.write(self.style.SUCCESS('Successfully enabled SEP-38 for AFRO'))

        if cnb:
            cnb.sep38_enabled = True
            cnb.save()
            self.stdout.write(self.style.SUCCESS('Successfully enabled SEP-38 for CNB'))

        if life:
            life.sep38_enabled = True
            life.save()
            self.stdout.write(self.style.SUCCESS('Successfully enabled SEP-38 for LIFE'))


