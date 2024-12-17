[![SAI](./docs/media/SAI_badge_flat.svg)](https://sai.itmo.ru/)
[![ITMO](./docs/media/ITMO_badge_flat_rus.svg)](https://en.itmo.ru/en/)

[![license](https://img.shields.io/github/license/compayser/cogmapoptimizer)](https://github.com/compayser/cogmapoptimizer/blob/main/LICENSE.md)
[![Eng](https://img.shields.io/badge/lang-en-red.svg)](/README_en.md)

# Общие сведения #

Экспериментальный образец программной библиотеки алгоритмов сильного ИИ, включающей в себя неклассические методы оптимизации для решения задач в условиях неопределенности и неполноты данных, предназначен для адаптивной оптимизации выполнения производственных процессов на основе интеллектуальных технологий и мультиагентной имитационной среды в части обеспечения адаптации имитационной среды к различным уровням абстракции и детализации выполнения алгоритмов за счет сочетания когнитивного анализа параметров производственной среды и тенденций в производственных процессах.
Необходимая функциональность реализуется в виде следующих алгоритмов:
* алгоритм поиска оптимального изменения параметров когнитивной карты;
* алгоритм мультиагентного моделирования.

Компонент предназначен для применения в системах поддержки принятия решений при работе со сложными техническими системами.

Для применения компонента когнитивная карта должна удовлетворять следующим условиям:
* число вершин графа когнитивной карты (N) — не более 32;
* число дуг графа когнитивной карты (М) — не более 992.

# Сведения о репозитории#

## Композиция репозитория ##

* [cogmap](cogmap) - файлы библиотеки когнитивного моделирования
* [cognitive](cognitive) - файлы инструмента агентного моделирования на базе FlameGPU
* [deploy](deploy) - файлы инструмента параллельной обработки когнитивных карт
* [ai-interpreter](ai-interpreter) - файлы инструмента подготовки конкретизирующих ИИ-запросов для когнитивных карт
* [graph-drawer](graph-drawer) - файлы инструмента визуализации вероятностных когнитивных карт
* [docs](docs/README.md) - описание библиотеки
* [examples](examples/README.md) - примеры когнитивных моделей и результатов оптимизации
* [Лицензия GPL v3.0](LICENSE.md)

## Встроенные тесты ##
По причине отсутствия доступа к инструментам и конвейера CI/CD (непрерывная интеграция / непрерывное развертывание) и их настройкам на стороне GitLab ИТМО (ошибка "you don't have any active runners", ссылка на настройки CI/CD, которая ведет на страницу 404 и проч.), модульное тестирование проводилось в GitHub проекта (https://github.com/compayser/cogmapoptimizer/).

Для этого были созданы раздельные файлы требований:
- requirements.txt - для развертывания,
- requirements_test.txt - для тестирования.

Различия заключаются в отсутствии в файле requirements_test.txt зависимости «wxPython==4.2.2». Во-первых, GitHub не в состоянии установить все ПО, нужное для сборки данной библиотеки (файлы библиотек из состава Visual C++ Redistributable, нужные для работы с графикой). Во-вторых, wxPython не  требуется непосредственно для процесса модульного тестирования классов библиотеки когнитивного моделирования и оптимизации, являющихся целью тестирования.

# Поддержка #
Исследование проводится при поддержке [Исследовательского центра сильного искусственного интеллекта в промышленности](https://sai.itmo.ru/) [Университета ИТМО](https://itmo.ru) в рамках мероприятия программы центра: Техническое проектирование и разработка экспериментального образца программной библиотеки алгоритмов сильного ИИ, включающей в себя неклассические методы оптимизации для решения задач в условиях неопределенности и неполноты данных.
