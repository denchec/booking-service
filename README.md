Запуск проекта:
1) git clone https://github.com/denchec/booking-service.git
2) docker compose up -d --build
3) docker compose exec web python manage.py createsuperuser
(создаем суперпользователя для входа в админку)
4) Зайти в админку:
5) Создать клинику во вкладке "Clinics"
6) Создать задачу "consultations.tasks.check_consultations" во вкладке "Periodic tasks"
   (Задача проводит опирации с автоматической заменой статуса или удалением консультации)

Готово, можно проверять работу сайта:
http://127.0.0.1:8000/login
