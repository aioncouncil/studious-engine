from django.core.management.base import BaseCommand

# [REF:00a1b2c3-d4e5-f6a7-b8c9-d0e1f2a3b4c5:CORE_USER_SYSTEM]
# [CLAUDE:OPTIMIZATION_LAYER:START]
# This file is part of the core_user_system component
# See .claude/README.md for more information
# [CLAUDE:OPTIMIZATION_LAYER:END]

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