import os
from random import choice

import django
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

from datacenter.models import (
    Schoolkid,
    Lesson,
    Commendation,
    Chastisement,
    Mark,
)

schoolkid_search_string: str = "Фролов Ива"


def fix_marks(
    schoolkid: Schoolkid,
    positive_marks: list = [4, 5],
    negative_marks: list = [1, 2, 3],
):
    marks = schoolkid.marks.filter(points__in=negative_marks)
    for mark in marks:
        mark.points = choice(positive_marks)

    Mark.objects.bulk_update(marks, fields=["points"])


def remove_chastisements(schoolkid: Schoolkid):
    print(f"Текущие замечания (кол-во:{schoolkid.chastisements.count()}):")
    chastisement: Chastisement
    for chastisement in schoolkid.chastisements.iterator():
        print(chastisement.text)
    Schoolkid.objects.filter(
        full_name__icontains=schoolkid_search_string
    ).first().chastisements.all().delete()
    print("Замечания удалены.")


def create_commendation(schoolkid: Schoolkid, subject_search_string: str):

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
        schoolkid = Schoolkid.objects.get(
            full_name__icontains=schoolkid_search_string
        )
    except Schoolkid.MultipleObjectsReturned:
        print(
            "По этим указанным параметрам нейдено несколько учеников. Exiting..."
        )
        exit()
    except Schoolkid.DoesNotExist:
        print("По этим указанным параметрам учеников не найдено. Exiting...")
        exit()

    fix_marks(schoolkid)
    remove_chastisements(schoolkid)
    subject_search_string="Мате"

    try:
        create_commendation(schoolkid, subject_search_string=subject_search_string)
    except Lesson.DoesNotExist:
        print(f'Не могу найти такой предмет "{subject_search_string}". Exiting...')