import os
from random import choice

import django
from django.core.exceptions import MultipleObjectsReturned

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

from datacenter.models import (
    Schoolkid,
    Lesson,
    Commendation,
    Chastisement,
    Mark,
)

schoolkid_search_string: str = "Фролов Иван"


def fix_marks(
    schoolkid_search_string: str = "Фролов Иван",
    positive_marks: list = [4, 5],
    negative_marks: list = [1, 2, 3],
):
    marks = Schoolkid.objects.get(
        full_name__icontains=schoolkid_search_string
    ).marks.filter(points__in=negative_marks)
    for mark in marks:
        mark.points = choice(positive_marks)

    Mark.objects.bulk_update(marks, fields=["points"])


def remove_chastisements(schoolkid_search_string="Фролов Иван"):
    chastisements = Schoolkid.objects.get(
        full_name__icontains=schoolkid_search_string
    ).chastisements
    print(f"Текущие замечания (кол-во:{chastisements.count()}):")
    chastisement: Chastisement
    for chastisement in chastisements.iterator():
        print(chastisement.text)
    Schoolkid.objects.filter(
        full_name__icontains=schoolkid_search_string
    ).first().chastisements.all().delete()
    print("Замечания удалены.")


def create_commendation(
    schoolkid_search_string="Фролов Иван", subject_search_string="Математика"
):
    schoolkid = Schoolkid.objects.get(
        full_name__icontains=schoolkid_search_string
    )

    latest_lesson: Lesson = Lesson.objects.filter(
        year_of_study=schoolkid.year_of_study,
        group_letter=schoolkid.group_letter,
        subject__title__icontains=subject_search_string,
    ).latest("date")

    Commendation.objects.create(
        text=choice(Commendation.objects.values_list("text", flat=True)),
        created=latest_lesson.date,
        schoolkid=schoolkid,
        subject=latest_lesson.subject,
        teacher=latest_lesson.teacher,
    )


if __name__ == "__main__":
    try:
        fix_marks(schoolkid_search_string="f")
        remove_chastisements(schoolkid_search_string=schoolkid_search_string)
        create_commendation(schoolkid_search_string=schoolkid_search_string)
    except MultipleObjectsReturned:
        print(
            "По этим указанным параметрам нейдено несколько учеников. Exiting..."
        )
