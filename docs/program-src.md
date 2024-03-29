# ТЕКСТ ПРОГРАММЫ

# ОБЩИЕ СВЕДЕНИЯ

Текст программы размещен в репозитории [https://gitlab.actcognitive.org/itmo-sai-code/cogmapoptimizer](https://gitlab.actcognitive.org/itmo-sai-code/cogmapoptimizer).

В директории `cogmap` собраны файлы модуля когнитивного моделирования. Перечень основных файлов (исходный код, файлы данных, файлы конфигурации и т. п.) представлен в табл. 1.

В директории cognitive собраны файлы исходного кода модуля агентного моделирования. Перечень основных файлов (исходный код, файлы данных, файлы конфигурации и т. п.) представлен в табл. 2.

Т а б л и ц а  1 - Перечень основных файлов модуля когнитивного моделирования.                   
  
|   Название файла    |  Тип файла   |                   Назначение                   |
| ------------------- | ------------ | ---------------------------------------------- |
| cogmap.py           | Исходный код | Класс когнитивной карты и сопутствующие классы |
| impact_generator.py | Исходный код | Генератор воздействий для когнитивной карты    |
| main.py             | Исходный код | Файл примера приложения                        |
| optimizer.py        | Исходный код | Класс оптимизатора когнитивной карты           |
| report.py           | Исходный код | Класс генератора отчета                        |
| proba.py            | Исходный код | Класс для работы с вероятностной арифметикой   |
| test_cogmap.py      | Исходный код | Модульный тест для cogmap.py                   |
| model.h5            | Файл модели  | Файл модели нейронной сети для ImpactGenerator |

Т а б л и ц а  2 - Перечень основных файлов модуля агентного моделирования.                   

|              Название файла              |       Тип файла       |                                           Назначение                                           |
| ---------------------------------------- | --------------------- | ---------------------------------------------------------------------------------------------- |
| cognitive.cpp                            | Исходный код          | Запуск программы, анализ входных аргументов                                                    |
| minunit.h                                | Исходный код          | Функции тестирования                                                                           |
| model.cpp                                | Исходный код          | Функции генерации проекта для FLAME GPU, начальной итерации, анализа результатов моделирования |
| model.h                                  | Исходный код          | Прототипы функций и типы данных, используемые в программе                                      |
| nxjson.cpp                               | Исходный код          | Библиотека работы с JSON                                                                       |
| nxjson.h                                 | Исходный код          | Заголовочный файл библиотеки работы с JSON                                                     |
| unit-test.cmj                            | Конфигурационный файл | Файл с входными данными, используемый при тестировании                                         |
| unit-test-group.cmj_xyz                  | Конфигурационный файл | Файл с входными данными, используемый при тестировании                                         |
| prj_templates/run.sh                     | Шаблон для генерации  | Шаблон генерации проекта для FLAME GPU                                                         |
| prj_templates/make.sh                    | Шаблон для генерации  | Шаблон генерации проекта для FLAME GPU                                                         |
| prj_templates/Makefile                   | Шаблон для генерации  | Шаблон генерации проекта для FLAME GPU                                                         |
| prj_templates/src/model/function.c       | Шаблон для генерации  | Шаблон генерации исходного кода модели для FLAME GPU                                           |
| prj_templates/src/model/XMLModelFile.xml | Шаблон для генерации  | Шаблон генерации исходного кода модели для FLAME GPU                                           |
| config.txt                               | Конфигурационный файл | Конфигурационный файл с параметрами генерации                                                  |
| impulse-lag.txt                          | Конфигурационный файл | Конфигурационный файл для режима модели с задержками                                           |
| group.cmj_xyz                            | Конфигурационный файл | Конфигурационный файл отслеживаемых вершин                                                     |

