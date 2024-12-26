# Локальный запуск

```bash
docker-compose up
```

# Тестирование
## TODO-сервис
1. Зайти на localhost:8082/docs
2. Воспользоваться POST /items для создания задачи
3. Воспользоваться GET /items для получения списка задач
4. Перезапустить контейнеры
```bash
docker-compose down
docker-compose up
```
5. Проверить, что данные остались через GET /items 

## Shoerten-сервис
1. Зайти на localhost:8081/docs
2. Воспользоваться POST /shorten для создания короткой ссылки
3. Воспользоваться GET /{short_id} для редиректа
4. Воспользоваться GET /stats/{short_id} для просмотра данных о ссылке
5. Перезапустить контейнеры
```bash
docker-compose down
docker-compose up
```
6. Проверить, что данные остались через GET /stats/{short_id}