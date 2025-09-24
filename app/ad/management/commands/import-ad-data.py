import os
import django
from django.db import transaction
from django.core.management.base import BaseCommand
from ad.models import *
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()


class Command(BaseCommand):
    help = "Imports data from ad/dataset"

    def add_arguments(self, parser):
        parser.add_argument(
            "--location",
            action="store_true",
            help="Import data for country, state, and city",
        )
        parser.add_argument(
            "--doctor",
            action="store_true",
            help="Import data for doctor",
        )

    def handle(self, *args, **kwargs):

        if kwargs["location"]:
            try:
                with open("ad/dataset/countries.json", "r") as file:
                    countries_data = json.load(file)

                    for country in countries_data:
                        Country.objects.create(
                            id=int(country["id"]),
                            name=country["country_name"],
                            abbr=country["country_abbr"],
                            slug=country["country_slug"],
                        )

                    self.stdout.write(
                        self.style.SUCCESS(f"Successfully created countries")
                    )

                with open("ad/dataset/states.json", "r") as file:
                    states_data = json.load(file)

                    states_to_create = [
                        State(
                            id=int(state["id"]),
                            country_id=int(state["country_id"]),
                            name=state["state_name"],
                            abbr=state["state_abbr"],
                            slug=state["state_slug"],
                        )
                        for state in states_data
                    ]
                    State.objects.bulk_create(states_to_create)

                    self.stdout.write(
                        self.style.SUCCESS(f"Successfully created states")
                    )

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error: {e}"))

            with open("ad/dataset/cities.json", "r") as file:
                cities_data = json.load(file)
                for city in cities_data:
                    try:
                        City.objects.create(
                            id=int(city["id"]),
                            state_id=int(city["state_id"]),
                            name=city["city_name"],
                            slug=city["city_slug"],
                            lat=city["city_lat"],
                            lng=city["city_lng"],
                        )
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"Error: {e} - {city['id']}")
                        )

                self.stdout.write(self.style.SUCCESS(f"Successfully created cities"))

        if kwargs["doctor"]:
            # Specialization.objects.bulk_create(
            #     [
            #         Specialization(
            #             id=1,
            #             title="Allergist",
            #             slug="allergist",
            #             description="An allergist-immunologist is trained in evaluation, "
            #             "physical and laboratory diagnosis, "
            #             "and management of disorders involving the immune system including asthma, "
            #             "anaphylaxis, rhinitis, eczema, and adverse reactions to drugs, foods, and insect stings.",
            #         ),
            #         Specialization(
            #             id=2,
            #             title="Advanced Heart Failure and Transplant Cardiologist",
            #             slug="advanced-heart-failure-and-transplant-cardiologist",
            #             description=None,
            #         ),
            #     ]
            # )

            with open("ad/dataset/doctors.json", "r") as file:
                doctors_data = json.load(file)
                for doctor in doctors_data:
                    try:
                        if doctor["category_slug"] == "allergist":
                            category_id = 1

                        if doctor["category_slug"] == "advanced-heart-failure-and-transplant-cardiologist":
                            category_id = 2

                        created_doctor = Doctor.objects.create(
                            id=int(doctor["id"]),
                            name=doctor["item_title"],
                            slug=doctor["item_slug"],
                            description=doctor["item_description"],
                            address=doctor["item_address"],
                            city_id=int(doctor["city_id"]),
                            state_id=int(doctor["state_id"]),
                            country_id=int(doctor["country_id"]),
                            postal_code=doctor["item_postal_code"],
                            website=doctor["item_website"],
                            phone=doctor["item_phone"],
                            lat=doctor["item_lat"],
                            lng=doctor["item_lng"],
                            timezone=doctor["item_hour_time_zone"],
                        )
                        created_doctor.specialization.add(category_id)

                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"Error: {e} - {doctor['id']}")
                        )

                self.stdout.write(self.style.SUCCESS(f"Successfully created doctors"))


if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    execute_from_command_line()
