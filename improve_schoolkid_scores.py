import os
from random import choice

import fire
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

from datacenter.models import (
    Schoolkid,
    Lesson,
    Commendation,
    Chastisement,
    Mark,
)


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
    print(f"Кол-во текущих замечаний: {schoolkid.chastisements.count()}.")
    schoolkid.chastisements.all().delete()
    print("Все замечания удалены.")


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
    print(f'Добавлена похвала от имени {latest_lesson.teacher}.')


def main(
    fio: str = "Фролов Иван",
    subj: str = "Математика",
):
    """

    Args:
        fio: Маска поиска ученика по ФИО
        subj: Маска поиска предмета, куда будет добавлена похвала
    """
    try:
        schoolkid = Schoolkid.objects.get(
            full_name__icontains=fio
        )
    except Schoolkid.MultipleObjectsReturned:
        print(f"По указанным параметрам ({fio}) найдено несколько учеников. Exiting...")
        exit()
    except Schoolkid.DoesNotExist:
        print(f"По указанным параметрам ({fio}) учеников не найдено. Exiting...")
        exit()

    fix_marks(schoolkid)
    remove_chastisements(schoolkid)

    try:
        create_commendation(
            schoolkid, subject_search_string=subj
        )
    except Lesson.DoesNotExist:
        print(
            f'Не могу найти такой предмет "{subj}". Exiting...'
        )


if __name__ == "__main__":
    fire.Fire(main)
