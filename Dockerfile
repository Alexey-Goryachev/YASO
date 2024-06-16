# Используйте официальный образ Python в качестве базового
FROM python:3.10

# Установите рабочую директорию
WORKDIR /app

# Скопируйте файлы pyproject.toml и poetry.lock
COPY impred/pyproject.toml ./

# Установите Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> /etc/profile.d/poetry.sh && \
    /root/.local/bin/poetry config virtualenvs.create false && \
    /root/.local/bin/poetry install --no-root

# Скопируйте проект в рабочую директорию
COPY impred /app
COPY impred/db.sqlite3 /app/db.sqlite3

# Примените миграции и соберите статические файлы
RUN /root/.local/bin/poetry run python3 manage.py migrate
    #/root/.local/bin/poetry run python3 manage.py collectstatic --noinput

# Откройте порт
EXPOSE 8000

# Определите команду запуска
CMD ["/root/.local/bin/poetry", "run", "python3", "manage.py", "runserver", "0.0.0.0:8000"]
