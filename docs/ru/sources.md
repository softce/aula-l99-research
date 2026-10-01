# Источники, благодарности и границы доказательств

[К оглавлению](../../README.ru.md)

Мы начали с уже существовавших исследований. Этот проект не присваивает себе открытие всех протоколов L99 и не содержит скопированного SDK производителя.

| Источник | Чем помог |
|---|---|
| [gavindi/Aula_L99_Linux](https://github.com/gavindi/Aula_L99_Linux), [инструменты](https://github.com/gavindi/Aula_L99_Linux/tree/main/tools) | Исследование HID/serial, записи обмена, часы/CPU/GPU/погода через HID клавиатуры; исходный ориентир по протоколам |
| [HuldaLloyd/lt7689](https://github.com/HuldaLloyd/lt7689/tree/a043cfb7214321cfb4165653fcb74822ec1754eb), [Basic_touch в bsp.c](https://github.com/HuldaLloyd/lt7689/blob/a043cfb7214321cfb4165653fcb74822ec1754eb/User/bsp.c#L12327) | Сопоставление структур UI, runtime и кодов touch; не доказательство того, что L99 имеет CPU LT7689 |
| [Salamor/aula-l99-open-widgets](https://github.com/Salamor/aula-l99-open-widgets), [обсуждение #2](https://github.com/Salamor/aula-l99-open-widgets/issues/2) | Независимое направление открытых виджетов и обсуждения экранного образа |
| [AULA: инструкция L99](https://aulastar.com/faq/818.html), [официальный reset-пакет](https://www.aulastar.com/uploads/soft/20240621/L99%20reset%20firmware%202026.5.25.zip) | Происхождение исследованных бинарных файлов; конкретные хеши в recovery.md |
| [LT168 datasheet V2.2](https://www.levetop.cn/uploadfiles/2025/%E8%A7%84%E6%A0%BC%E4%B9%A6/LT168_DS_V22_Eng_User-S.pdf) | Карта памяти семейства: стр. 64–65, 81–83; не board-specific карта L99 |
| [UI Editor-II V3.20](https://www.levetop.cn/uploadfiles/2025/%E5%BA%94%E7%94%A8%E6%89%8B%E5%86%8C/UI_Editor-II_CH_V3.2-250912.pdf) | Модель UI и направления аппаратного восстановления; boot-разделы 16.1.3.1–16.1.3.2 относятся к демонстрационным платам |
| [Фоторазборка L99, 大胖鸟, Weistang](https://www.weistang.com/thread-125204-1-1.html), [страница разборки](https://www.weistang.com/portal.php?mod=view&aid=25988&page=4&forcemobile=1) | Автор сообщает HFD168BDP, HFD80CP100, Goodix GT911; это другой экземпляр, не осмотр нашей платы |
| [fpb/ajazz-ak820-pro](https://github.com/fpb/ajazz-ak820-pro/tree/180d731357decae00c36bf8d94ad17bf6e43e392), [конфиг QMK](https://github.com/fpb/qmk_firmware/blob/cb2d34c07bd131d71fc5886bef1e4cea7f4d9ca9/keyboards/a_jazz/ak820pro/keyboard.json) | Родственная работа с HFD80CP100/SN32F299; matrix, firmware и recovery Ajazz нельзя переносить на L99 напрямую |
| [SonixFlasherC](https://github.com/SonixQMK/SonixFlasherC/blob/b41694cdff5b6d935b51067f24975aabeebe344c/sonixflasher.c) | Сопоставление арифметики checksum и SN32F290 update-протокола; не запускался для L99 |
| [mos9527/evbunpack](https://github.com/mos9527/evbunpack), [innoextract](https://github.com/dscharrer/innoextract) | Предварительный статический разбор контейнеров без исполнения updater |

## Как читать заявления в этой публикации

- **На устройстве:** пользователь наблюдал новый интерфейс, работу обычного ввода, управление HA и обновление значений. Это не полный readback flash и не тест каждой ревизии.
- **Статический разбор:** адреса/структуры получены из конкретного файла с указанным SHA256. Они не автоматически действуют для одноимённого файла другой версии.
- **Эмуляция:** выполнялись отдельные машинные функции и сравнивались буферы. Это не полный MCU с реальной периферией.
- **Гипотеза:** явно оставленные вопросы о маркировке, дополнительных проектах и аварийном recovery.

Многие ранние локальные заметки предшествовали последующим проверкам. Здесь отражена уточнённая картина: ресурсный образ найден у производителя, keyboard resource 4000 существенно важнее первоначально найденного HEX, а ограниченный рабочий UI не означает полностью открытую прошивку.

## Лицензия и персональные данные

Публикуются заново подготовленное описание и наши офлайн-инструменты. Общая лицензия GPL-2.0-only согласуется с открытым распространением исследовательского кода. Это не заявление о правах на firmware, SDK или графику AULA/Levetop. Такие файлы не включены; инструменты обрабатывают отдельно полученную пользователем копию.

В примерах только вымышленные entity_id и синтетические значения. Секреты, адреса домашней сети, конфигурации, абсолютные пользовательские пути, журнал переписки и USB/HA-захваты не публикуются. Рабочая папка не импортируется как история Git.

[English version](../sources.md)
