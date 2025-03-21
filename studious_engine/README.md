# studious-engine

Gamified Civilization & Manufacturing Engine for Creating & Running Physical Post-Scarcity Societies

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

License: MIT

## App Configuration Notes

The apps in this project follow these conventions:

1. App names in `INSTALLED_APPS` should match the import path used in the code
2. For example, the core app is configured with `name = "core"` in CoreConfig and referenced as `"core.apps.CoreConfig"` in INSTALLED_APPS
3. When models reference models from other apps, they should use the same app name (e.g., `from core.models import ...`)

If you encounter import errors:
- Check that the app configuration in `apps.py` matches how it's referenced in `settings.py`
- Make sure imports use consistent paths throughout the codebase
- Run `python manage.py collectstatic` after adding new static files

## Profile System

EudaimoniaGo uses a dual profile system:

1. **Game Profile** (`/profile/` or `core:player_profile`):
   - Game-specific player information 
   - Shows player rank, experience points, powers, and accomplishments
   - Tracks game progress, unlocked abilities, and achievements
   - Access via the "My Profile" link in the game navigation dropdown or directly at `/profile/`

2. **User Account Profile** (`/users/<username>/` or `users:detail`):
   - Django user account management 
   - Personal information, email preferences, and account settings
   - Password changes and account security options
   - Access via the "Account Settings" link in the game navigation dropdown or directly at `/users/<username>/`

This separation keeps game-specific data isolated from account management, providing a cleaner architecture and better user experience.

## Template System

EudaimoniaGo provides different templates for different interface needs:

1. **Base Template** (`base.html`):
   - Standard web application layout with navigation bar
   - Used for account management, admin pages, and information pages
   - Traditional web navigation with header, content area, and footer
   - Good for pages that require standard website UI/UX

2. **Game Base Template** (`game_base.html`):
   - Enhanced web interface specifically for game content
   - Includes game-specific navigation and styles
   - Still has a traditional navigation bar with dropdowns
   - Suitable for game content that benefits from web navigation

3. **App-style Template** (`game_app_base.html`):
   - Mobile app-like interface inspired by Pokémon Go
   - No standard navigation bar - uses bottom tab navigation instead
   - Top status bar showing player info and resources
   - Full-screen immersive experience for game content
   - Best for map, dashboard, and core gameplay features

To provide a Pokémon Go-like experience, use the `game_app_base.html` template for game pages and customize as needed. The template choice depends on the specific content and user interaction needs.

## Settings

Moved to [settings](https://cookiecutter-django.readthedocs.io/en/latest/1-getting-started/settings.html).

## Basic Commands

### Setting Up Your Users

- To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

- To create a **superuser account**, use this command:

      $ python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

### Type checks

Running type checks with mypy:

    $ mypy studious_engine

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

#### Running tests with pytest

    $ pytest

### Live reloading and Sass CSS compilation

Moved to [Live reloading and SASS compilation](https://cookiecutter-django.readthedocs.io/en/latest/2-local-development/developing-locally.html#using-webpack-or-gulp).

### Email Server

In development, it is often nice to be able to see emails that are being sent from your application. If you choose to use [Mailpit](https://github.com/axllent/mailpit) when generating the project a local SMTP server with a web interface will be available.

1.  [Download the latest Mailpit release](https://github.com/axllent/mailpit/releases) for your OS.

2.  Copy the binary file to the project root.

3.  Make it executable:

        $ chmod +x mailpit

4.  Spin up another terminal window and start it there:

        ./mailpit

5.  Check out <http://127.0.0.1:8025/> to see how it goes.

Now you have your own mail server running locally, ready to receive whatever you send it.

## Deployment

The following details how to deploy this application.
