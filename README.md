# Общие сведения #

Компонент реализует функции сильного ИИ в части алгоритмов адаптивной оптимизации выполнения производственных 
процессов на основе интеллектуальных технологий и мультиагентной имитационной среды в части обеспечения адаптации
имитационной среды к различным уровням абстракции и детализации выполнения алгоритмов за счет сочетания когнитивного 
анализа параметров производственной среды и тенденций в производственных процессах в нефтегазовой отрасли.
Необходимая функциональность реализуется в виде следующих алгоритмов:
* алгоритм поиска оптимального изменения параметров когнитивной карты;
* алгоритм мультиагентного моделирования.

Компонент предназначен для применения в системах поддержки принятия решений при работе со сложными техническими системами.

Для применения компонента когнитивная карта должна удовлетворять следующим условиям:
* число вершин графа когнитивной карты (N) — менее 32;
* число дуг графа когнитивной карты (М) — менее 992;

# Композиция репозитория #

* ![cognitive](cognitive) - файлы инструмента агентного моделирования на базе FlameGPU
* ![cogmap](cogmap) - файлы библиотеки когнитивного моделирования
* ![docs](docs) - описание библиотеки ![CogMap Optimizer](docs/cogmap.md), программы агентного моделирования на основе 
FlameGPU ![Cognitive](docs/cognitive.md) и примеры
* ![Лицензия GPL v3.0](LICENSE.md)

# Примеры когнитивных моделей и результатов оптимизации #
1. Оптимизация ![дебета скважин](docs/example1/Control_example_1_ReadMe.md)
2. Мероприятия по ликвидации ![разлива нефти](docs/example2/Control_example_2_ReadMe.md)

 

