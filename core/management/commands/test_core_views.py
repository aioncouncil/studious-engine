from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Test importing views from the core.views module only'

    def handle(self, *args, **options):
        try:
            from core.views import GameDashboardView, PlayerProfileView, MapView, update_player_location
            self.stdout.write(self.style.SUCCESS('Successfully imported all core views:'))
            self.stdout.write(f'- GameDashboardView: {GameDashboardView}')
            self.stdout.write(f'- PlayerProfileView: {PlayerProfileView}')
            self.stdout.write(f'- MapView: {MapView}')
            self.stdout.write(f'- update_player_location: {update_player_location}')
        except ImportError as e:
            self.stdout.write(self.style.ERROR(f'Error importing core views: {e}')) 