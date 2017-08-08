USER_TYPES = (
    (1, 'Физическое лицо'),
    (2, 'Юридическое лицо'),
)
DOC_TYPES = (
    (1, 'СРТС'),
    (2, 'ПТС'),
)
TS_CATEGORIES = (
    (1, 'A'),
    (2, 'B'),
    (3, 'C'),
    (4, 'D'),
    (5, 'Прицеп'),
)

TS_SUBCATEGORIES = (
    (1, 'M1 (легковые до 8-ми пассажирских мест)'),
    (2, 'N1 (грузовые с максимальной массой не более 3,5 тонн)'),
)

TS_FUEL_TYPES = (
    (1, 'Бензин'),
    (2, 'Дизель'),
)

TS_BRAKE_TYPES = (
    (1, 'Гидравлическая'),
    (2, 'Пневматическая'),
    (3, 'Комбинированная'),
    (4, 'Механическая'),
)

TS_DUAL_FUEL = (
    (1, 'Пропан-бутан/бензин'),
    (2, 'Метан/бензин'),
)

MAX_TEST_VALUE = 67

SUCCESS_MESSAGE_CARD_SEND = 'Заявка успешно зарегистрирована.'
ERROR_MESSAGE_TASK_SEND = 'Ошибка при отправке: не доступно ЕАИСТО.'
ERROR_MESSAGE_TASK_SEND_NOT_FOUND_EXERT = 'Ошибка при отправке: нет доступных экспертов'
ERROR_MESSAGE_TASK_SEND_NOT_FOUND_STANTION = 'Ошибка при отправке: нет доступных станций'
SUCCESS_MESSAGE_CARD_CHANGE = 'Карта изменена'
SUCCESS_MESSAGE_CARD_DELETE = 'Карта удалена'
ERROR_MESSAGE_EAISTO_ERROR = 'Ошибка при регистрации в ЕАИСТО'
ERROR_MESSAGE_EAISTO_DELETE = 'Ошибка при удалении в ЕАИСТО'

EAISTO_API_ERROR_DUPLICATE = (
    'SQLSTATE[23000]: Integrity constraint violation: 1048 Column \'F_LICA\' cannot be null',
    'SQLSTATE[40001]: Serialization failure: 1213 Deadlock found when trying to get lock; try restarting transaction',
)
