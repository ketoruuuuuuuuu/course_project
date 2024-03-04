## Cian long-term rent analisis
Анализ спроса и предложения на рынке долгосрочной аренды квартир в СПБ

### Парсер
Основан на базе библиотеки *cianparser* с модикацией исходного кода, чтобы находились объявления в Лен. области.
Дополнительно собирает фотографии, дату поста, дату в которую последний раз видел объявление и удобства(кондиционер,холодильник и т.д.)

### Данные
Все собранные на данный момент данные хранятся в папке [data](/data/)

### Анализ
В папке [analisis](/analisis/) можно найти предварительный анализ и решение проблем с пропущенными переменными

### Модели
Находятся в папке [models](/models/).
Пока используются только обычная множественная регрессия и GWR

### TODO
- Собрать больше данных
- Сделать все числовые переменные без среднего для интерпритируемости коэфов
- Сделать нормальный анализ уже после чистки всего
- Чистить балконы
- Сделать модель со светкаи для картинок с объявлений
- Проанализировать коэфы в GWR
