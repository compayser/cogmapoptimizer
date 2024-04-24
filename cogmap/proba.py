"""
Инструментарий для работы с вероятностной арифметикой
Probabilistic arithmetics routines
"""
import sys
import copy


class ProbVal:
    """
    Класс для работы с вероятностной арифметикой (описание вероятностной величины)
    """
    def __init__(self, val=0.0, prob=0.0):
        """
        Конструктор
        :param val: значение
        :param prob: вероятность
        """
        self.value = val
        self.prob = prob

    def __str__(self):
        """
        Строковое представление класса
        """
        str_ = f'{self.value}/{self.prob}\n'
        return str_


class ProbA:
    """
    Класс для работы с вероятностной арифметикой
    (описание дискретной вероятностной величины (ДСВ) и операций над ней)
    """
    def __init__(self):
        """
        Конструктор
        """
        self.vals = []  # Список значений/вероятностей
        self.COMPARE_RANGE = 0.5  # Пороговое значения для операций сравнения
        self.MAX_ELEMENTS = 10  # Максимальное число элементов для ДВС при умньшение размерности массива с описанием ДСВ
        self.BUILD_SCALAR = 'max'  # Режим получения скаляра из массива описания ДСВ (avg, max, min, max_avg, min_avg)

    def __str__(self):
        """
        Строковое представление класса
        """
        str_ = f''
        for i in range(len(self.vals)):
            str_ += f'v[{i}]={self.vals[i].value} p[{i}]={self.vals[i].prob}\n'
        return str_

    def append_value(self, value=0.0, prob=0.0):
        """
        Добавить вероятностное значение
        :param value: значение
        :param prob: вероятность
        """
        val = ProbVal(value, prob)
        self.vals.append(val)

    def check_probs(self):
        """
        Проверка значений вероятностей
        :return: ==0 - OK,
                  >0 - переполненый массив (сумма вероятностей > 1),
                  <0 - недозаполненый массив (сумма вероятностей < 1)
        """
        summ = 0
        for i in range(len(self.vals)):
            summ += self.vals[i].prob
        if 0.9999999999 < summ < 1.0000000001:
            return 0  # OK
        if summ <= 0.9999999999:
            return summ-1  # Недозаполненый массив значений
        return summ-1  # Переполненый массив значений

    def reduce(self, new_size=-1):
        """
        Умньшение размерности массива с описанием ДСВ
        """
        if new_size == -1:
            new_size = self.MAX_ELEMENTS
        if len(self.vals) > new_size:
            self.vals.sort(key=lambda x: x.value, reverse=False)
            new_size -= 1
            delta = int(len(self.vals) / new_size)
            rnd = ProbA()
            result = ProbA()
            index = 0
            processed_i = 0
            for i in range(len(self.vals)):
                rnd.append_value(self.vals[i].value, self.vals[i].prob)
                if index < delta-1:
                    index += 1
                else:
                    index = 0
                    sum_prob = 0
                    for j in range(len(rnd.vals)):
                        sum_prob += rnd.vals[j].prob
                    rnd_res_prob = 0
                    rnd_res_val = 0
                    for j in range(len(rnd.vals)):
                        if sum_prob != 0:
                            rnd_res_val += rnd.vals[j].value * (rnd.vals[j].prob / sum_prob)
                            rnd_res_prob += rnd.vals[j].prob
                    result.append_value(rnd_res_val, rnd_res_prob)
                    rnd = ProbA()
                    processed_i = i
            # Дообработать "хвост"
            if processed_i < len(self.vals):
                sum_prob = 0
                for j in range(processed_i+1, len(self.vals)):
                    sum_prob += self.vals[j].prob
                rnd_res_prob = 0
                rnd_res_val = 0
                for j in range(len(rnd.vals)):
                    if sum_prob != 0:
                        rnd_res_val += rnd.vals[j].value * (rnd.vals[j].prob / sum_prob)
                        rnd_res_prob += rnd.vals[j].prob
                if rnd_res_val != 0 and rnd_res_prob != 0:
                    result.append_value(rnd_res_val, rnd_res_prob)
            self.vals = result.vals
        return

    def __add__(self, rnd):
        """
        Сложение двух величин
        :param rnd: слагаемое в виде ДСВ
        """
        result = ProbA()
        if isinstance(rnd, int) or isinstance(rnd, float):
            val = rnd
            rnd = ProbA()
            rnd.append_value(val, 1.0)
        # Операция сложения
        for i in self.vals:
            for j in rnd.vals:
                new_val = i.value + j.value
                new_prob = i.prob * j.prob
                result.append_value(new_val, new_prob)
        result.reduce()
        # Редуцирование массива
        index = 0
        for i in range(len(result.vals)):
            for j in range(len(result.vals)):
                if i != j and \
                   result.vals[i].prob != -1 and \
                   result.vals[j].prob != -1 and \
                   result.vals[i].value == result.vals[j].value:
                    # Объединение значений
                    result.vals[i].prob += result.vals[j].prob
                    result.vals[j].prob = -1
                    index += 1
        # Удаление отброшенных элементов
        result.vals.sort(key=lambda x: (x.prob, x.value), reverse=False)
        for i in range(index):
            result.vals.pop(0)
        result.vals.sort(key=lambda x: x.value, reverse=False)
        # Результаты
        return result

    def __sub__(self, rnd):
        """
        Вычетание двух величин
        :param rnd: вычитаемое в виде ДСВ
        """
        result = ProbA()
        if isinstance(rnd, int) or isinstance(rnd, float):
            val = rnd
            rnd = ProbA()
            rnd.append_value(val, 1.0)
        # Операция вычетания
        for i in self.vals:
            for j in rnd.vals:
                new_val = i.value - j.value
                new_prob = i.prob * j.prob
                result.append_value(new_val, new_prob)
        result.reduce()
        # Редуцирование массива
        index = 0
        for i in range(len(result.vals)):
            for j in range(len(result.vals)):
                if i != j and \
                   result.vals[i].prob != -1 and \
                   result.vals[j].prob != -1 and \
                   result.vals[i].value == result.vals[j].value:
                    # Объединение значений
                    result.vals[i].prob += result.vals[j].prob
                    result.vals[j].prob = -1
                    index += 1
        # Удаление отброшенных элементов
        result.vals.sort(key=lambda x: (x.prob, x.value), reverse=False)
        for i in range(index):
            result.vals.pop(0)
        result.vals.sort(key=lambda x: x.value, reverse=False)
        # Результаты
        return result

    def __mul__(self, rnd):
        """
        Перемножение двух величин
        :param rnd: множитель в виде ДСВ
        """
        result = ProbA()
        if isinstance(rnd, int) or isinstance(rnd, float):
            val = rnd
            rnd = ProbA()
            rnd.append_value(val, 1.0)
        # Операция умножения
        for i in self.vals:
            for j in rnd.vals:
                new_val = i.value * j.value
                new_prob = i.prob * j.prob
                result.append_value(new_val, new_prob)
        result.reduce()
        # Редуцирование массива
        index = 0
        for i in range(len(result.vals)):
            for j in range(len(result.vals)):
                if i != j and \
                   result.vals[i].prob != -1 and \
                   result.vals[j].prob != -1 and \
                   result.vals[i].value == result.vals[j].value:
                    # Объединение значений
                    result.vals[i].prob += result.vals[j].prob
                    result.vals[j].prob = -1
                    index += 1
        # Удаление отброшенных элементов
        result.vals.sort(key=lambda x: (x.prob, x.value), reverse=False)
        for i in range(index):
            result.vals.pop(0)
        result.vals.sort(key=lambda x: x.value, reverse=False)
        # Результаты
        return result

    def __truediv__(self, rnd):
        """
        Деление двух величин
        :param rnd: делитель в виде ДСВ
        """
        result = ProbA()
        if isinstance(rnd, int) or isinstance(rnd, float):
            val = rnd
            rnd = ProbA()
            rnd.append_value(val, 1.0)
        # Операция деления
        for i in self.vals:
            for j in rnd.vals:
                new_val = i.value / j.value
                new_prob = i.prob * j.prob
                result.append_value(new_val, new_prob)
        result.reduce()
        # Редуцирование массива
        index = 0
        for i in range(len(result.vals)):
            for j in range(len(result.vals)):
                if i != j and \
                   result.vals[i].prob != -1 and \
                   result.vals[j].prob != -1 and \
                   result.vals[i].value == result.vals[j].value:
                    # Объединение значений
                    result.vals[i].prob += result.vals[j].prob
                    result.vals[j].prob = -1
                    index += 1
        # Удаление отброшенных элементов
        result.vals.sort(key=lambda x: (x.prob, x.value), reverse=False)
        for i in range(index):
            result.vals.pop(0)
        result.vals.sort(key=lambda x: x.value, reverse=False)
        # Результаты
        return result

    def __gt__(self, max_):
        """
        Сравнение RND-величины со скалярной величиной (больше, >)
        :param max_: операнд в виде ДСВ
        """
        res_prob = 0
        # Операция умножения
        for i in self.vals:
            if i.value > max_:
                res_prob += i.prob
        # Результат
        return True if res_prob > self.COMPARE_RANGE else False

    def __ge__(self, max_):
        """
        Сравнение RND-величины со скалярной величиной (больше или равно, >=)
        :param max_: операнд в виде ДСВ
        """
        res_prob = 0
        # Операция умножения
        for i in self.vals:
            if i.value >= max_:
                res_prob += i.prob
        # Результат
        return True if res_prob > self.COMPARE_RANGE else False

    def __lt__(self, min_):
        """
        Сравнение RND-величины со скалярной величиной (меньше, <)
        :param min_: операнд в виде ДСВ
        """
        res_prob = 0
        # Операция сравнения
        for i in self.vals:
            if i.value < min_:
                res_prob += i.prob
        # Результат
        return True if res_prob > self.COMPARE_RANGE else False

    def __le__(self, min_):
        """
        Сравнение RND-величины со скалярной величиной (меньше или равно, <=)
        :param min_: операнд в виде ДСВ
        """
        res_prob = 0
        # Операция сравнения
        for i in self.vals:
            if i.value <= min_:
                res_prob += i.prob
        # Результат
        return True if res_prob > self.COMPARE_RANGE else False

    def __ne__(self, val):
        """
        Операция неравенства с ДСВ (!=)
        :param val: операнд в виде ДСВ
        """
        if not isinstance(val, ProbA):
            # Сравнение с не ДСВ
            if not isinstance(val, float):
                return None
            else:
                return True if self.avg() != val else False
        else:
            # Сравнение с ДСВ
            if len(self.vals) != len(val.vals):
                return True
            # Результат
            for i in range(len(self.vals)):
                if self.vals[i].value != val.vals[i].value:
                    return True
            return False

    def abs(self):
        """
        Операция взятия по модулю
        """
        for i in self.vals:
            i.value = abs(i.value)

    def avg(self):
        """
        Средневзвешенное значение ДСВ
        """
        average = 0.0
        for i in range(len(self.vals)):
            average += self.vals[i].value * self.vals[i].prob
        return average

    # noinspection PyMethodMayBeStatic
    def max(self, rnd_arr):
        """
        Максимум значений ДСВ из массива ДСВ
        :param rnd_arr: массив ДСВ
        """
        maximum = ProbA()
        maximum.append_value(-sys.float_info.max, 1.0)
        for i in range(len(rnd_arr)):
            if rnd_arr[i] > maximum:
                maximum = rnd_arr[i]
        return maximum

    def max_prob(self):
        """
        Значение ДСВ с максимальной вероятностью
        """
        if len(self.vals) == 0:
            return None
        if len(self.vals) == 1:
            return self.vals[0].value
        maximum = 0.0
        idx = -1
        for i in range(len(self.vals)):
            if self.vals[i].prob > maximum:
                maximum = self.vals[i].prob
                idx = i
        return self.vals[idx].value

    def max2_prob(self):
        """
        Второе по вероятности значение ДСВ (max)
        """
        if len(self.vals) == 0:
            return None
        if len(self.vals) == 1:
            return self.vals[0].value
        maximum = 0.0
        idx = -1
        for i in range(len(self.vals)):
            if self.vals[i].prob > maximum:
                maximum = self.vals[i].prob
                idx = i
        tmp = copy.deepcopy(self)
        tmp.vals[idx].prob = -1.0
        maximum = 0.0
        for i in range(len(tmp.vals)):
            if tmp.vals[i].prob > maximum:
                maximum = tmp.vals[i].prob
                idx = i
        return tmp.vals[idx].value

    # noinspection PyMethodMayBeStatic
    def min(self, rnd_arr):
        """
        Минимум значений ДСВ из массива ДСВ
        :param rnd_arr: массив ДСВ
        """
        minimum = ProbA()
        minimum.append_value(sys.float_info.max, 1.0)
        for i in range(len(rnd_arr)):
            if rnd_arr[i] < minimum:
                minimum = rnd_arr[i]
        return minimum

    def min_prob(self):
        """
        Значение ДСВ с максимальной вероятностью
        """
        if len(self.vals) == 0:
            return None
        if len(self.vals) == 1:
            return self.vals[0].value
        minimum = 1.1
        idx = -1
        for i in range(len(self.vals)):
            if self.vals[i].prob < minimum:
                minimum = self.vals[i].prob
                idx = i
        return self.vals[idx].value

    def min2_prob(self):
        """
        Второе по вероятности значение ДСВ (max)
        """
        if len(self.vals) == 0:
            return None
        if len(self.vals) == 1:
            return self.vals[0].value
        minimum = 1.1
        idx = -1
        for i in range(len(self.vals)):
            if self.vals[i].prob < minimum:
                minimum = self.vals[i].prob
                idx = i
        tmp = copy.deepcopy(self)
        tmp.vals[idx].prob = 1.1
        minimum = 1.1
        for i in range(len(tmp.vals)):
            if tmp.vals[i].prob < minimum:
                minimum = tmp.vals[i].prob
                idx = i
        return tmp.vals[idx].value

    def build_scalar(self):
        """
        Получение скалярного числа из ДСВ разными методами
        """
        if self.BUILD_SCALAR == 'avg':  # Среднее взвешенное
            return self.avg()
        if self.BUILD_SCALAR == 'max':  # Максимально вероятное
            return self.max_prob()
        if self.BUILD_SCALAR == 'min':  # Минимально вероятное
            return self.min_prob()
        if self.BUILD_SCALAR == 'max_avg':  # Среднее по 2-м максимумам
            return (self.max_prob() + self.max2_prob()) / 2
        if self.BUILD_SCALAR == 'min_avg':  # Среднее по 2-м минимумам
            return (self.min_prob() + self.min2_prob()) / 2
        return None
