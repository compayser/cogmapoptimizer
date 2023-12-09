# Инструментарий для работы с вероятностной арифметикой
# Probabilistic arithmetics routines
import sys
import copy
import proba

# ----------------------------------------------------------------------------------
# Класс для работы с вероятностной арифметикой
class ProbVal:
    # Конструктор
    def __init__(self, val=0.0, prob=0.0):
        self.value = val  # Значение
        self.prob = prob  # Вероятность

    # Строковое представление
    def __str__(self):
        str = f'{self.value}/{self.prob}\n'
        return str
# ----------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------
# Класс для работы с ДСВ и вероятностной арифметикой
class ProbA:

    # Конструктор
    def __init__(self):
        self.vals = []
        self.COMPARE_RANGE = 0.5
        self.MAX_ELEMENTS = 10
        self.BUILD_SCALAR = 'max'  # Options: avg, max, min, max_avg, min_avg

    # Строковое представление
    def __str__(self):
        str = f''
        for i in range(len(self.vals)):
            str += f'v[{i}]={self.vals[i].value} p[{i}]={self.vals[i].prob}\n'
        i = 0
        return str

    # Добавить вероятностное значение
    def append_value(self, value=0.0, prob=0.0):
        val = ProbVal(value, prob)
        self.vals.append(val)

    # Проверка значений вероятностей
    def check_probs(self):
        summ = 0
        for i in range(len(self.vals)):
            summ += self.vals[i].prob
        # OK
        if summ > 0.9999999999 and summ < 1.0000000001:
            return 0
        # Недозаполненый массив значений
        if summ <= 0.9999999999:
            return summ-1
        # Переполненый массив значений
        return summ-1

    # Умньшение размерности массива с описанием ДСВ
    def reduce(self, newSize = -1):
        if newSize == -1:
            newSize = self.MAX_ELEMENTS
        if len(self.vals) > newSize:
            self.vals.sort(key=lambda x: x.value, reverse=False)
            newSize -= 1
            delta = int(len(self.vals) / newSize)
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
                rnd = ProbA()

            self.vals = result.vals
        return

    # Сложение двух величин
    def __add__(self, rnd):
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
                if i != j and result.vals[i].prob != -1 and result.vals[j].prob != -1 and result.vals[i].value == result.vals[j].value:
                    # Объединение значений
                    result.vals[i].prob += result.vals[j].prob
                    result.vals[j].prob  = -1
                    index += 1
        # Удаление отброшенных элементов
        result.vals.sort(key=lambda x: (x.prob, x.value), reverse=False)
        for i in range(index):
            result.vals.pop(0)
        result.vals.sort(key=lambda x: x.value, reverse=False)
        # Результаты
        return result


    # Вычетание двух величин
    def __sub__(self, rnd):
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
                if i != j and result.vals[i].prob != -1 and result.vals[j].prob != -1 and result.vals[i].value == result.vals[j].value:
                    # Объединение значений
                    result.vals[i].prob += result.vals[j].prob
                    result.vals[j].prob  = -1
                    index += 1
        # Удаление отброшенных элементов
        result.vals.sort(key=lambda x: (x.prob, x.value), reverse=False)
        for i in range(index):
            result.vals.pop(0)
        result.vals.sort(key=lambda x: x.value, reverse=False)
        # Результаты
        return result


    # Перемножение двух величин
    def __mul__(self, rnd):
        result = ProbA()
        if isinstance(rnd, int) or isinstance(rnd, float):
            val = rnd
            rnd = ProbA()
            rnd.append_value(val, 1.0)
        # Операция умножения
        for i in self.vals:
            for j in rnd.vals:
                new_val  = i.value * j.value
                new_prob = i.prob * j.prob
                result.append_value(new_val, new_prob)
        result.reduce()
        # Редуцирование массива
        index = 0
        for i in range(len(result.vals)):
            for j in range(len(result.vals)):
                if i != j and result.vals[i].prob != -1 and result.vals[j].prob != -1 and result.vals[i].value == result.vals[j].value:
                    # Объединение значений
                    result.vals[i].prob += result.vals[j].prob
                    result.vals[j].prob  = -1
                    index += 1
        # Удаление отброшенных элементов
        result.vals.sort(key=lambda x: (x.prob, x.value), reverse=False)
        for i in range(index):
            result.vals.pop(0)
        result.vals.sort(key=lambda x: x.value, reverse=False)
        # Результаты
        return result


    # Деление двух величин
    def __truediv__(self, rnd):
        result = ProbA()
        if isinstance(rnd, int) or isinstance(rnd, float):
            val = rnd
            rnd = ProbA()
            rnd.append_value(val, 1.0)
        # Операция деления
        for i in self.vals:
            for j in rnd.vals:
                new_val  = i.value / j.value
                new_prob = i.prob * j.prob
                result.append_value(new_val, new_prob)
        result.reduce()
        # Редуцирование массива
        index = 0
        for i in range(len(result.vals)):
            for j in range(len(result.vals)):
                if i != j and result.vals[i].prob != -1 and result.vals[j].prob != -1 and result.vals[i].value == result.vals[j].value:
                    # Объединение значений
                    result.vals[i].prob += result.vals[j].prob
                    result.vals[j].prob  = -1
                    index += 1
        # Удаление отброшенных элементов
        result.vals.sort(key=lambda x: (x.prob, x.value), reverse=False)
        for i in range(index):
            result.vals.pop(0)
        result.vals.sort(key=lambda x: x.value, reverse=False)
        # Результаты
        return result


    # Сравнение RND-величины со скалярной величиной (больше, >)
    def __gt__(self, max):
        res_prob = 0
        # Операция умножения
        for i in self.vals:
            if i.value > max:
                res_prob += i.prob
        # Результат
        return True if res_prob > self.COMPARE_RANGE else False


    # Сравнение RND-величины со скалярной величиной (больше или равно, >=)
    def __ge__(self, max):
        res_prob = 0
        # Операция умножения
        for i in self.vals:
            if i.value >= max:
                res_prob += i.prob
        # Результат
        return True if res_prob > self.COMPARE_RANGE else False


    # Сравнение RND-величины со скалярной величиной (меньше, <)
    def __lt__(self, min):
        res_prob = 0
        # Операция сравнения
        for i in self.vals:
            if i.value < min:
                res_prob += i.prob
        # Результат
        return True if res_prob > self.COMPARE_RANGE else False


    # Сравнение RND-величины со скалярной величиной (меньше или равно, <=)
    def __le__(self, min):
        res_prob = 0
        # Операция сравнения
        for i in self.vals:
            if i.value <= min:
                res_prob += i.prob
        # Результат
        return True if res_prob > self.COMPARE_RANGE else False

    # Операция неравенства с ДСВ (!=)
    def __ne__(self, val):
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


    # Модуль RND-величины
    def abs(self):
        # Операция взятия по модулю
        for i in self.vals:
            i.value = abs(i.value)


    # Средневзвешенное значение ДСВ
    def avg(self):
        average = 0.0
        for i in range(len(self.vals)):
            average += self.vals[i].value * self.vals[i].prob
        return average


    # Максимум значений ДСВ из массива ДСВ
    def max(self, rnd_arr):
        maximum = proba.ProbA()
        maximum.append_value(-sys.float_info.max, 1.0)
        for i in range(len(rnd_arr)):
            if rnd_arr[i] > maximum:
                maximum = rnd_arr[i]
        return maximum


    # Значение ДСВ с максимальной вероятностью
    def max_prob(self):
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


    # Второе по вероятности значение ДСВ (max)
    def max2_prob(self):
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


    # Минимум значений ДСВ из массива ДСВ
    def min(self, rnd_arr):
        minimum = proba.ProbA()
        minimum.append_value(sys.float_info.max, 1.0)
        for i in range(len(rnd_arr)):
            if rnd_arr[i] < minimum:
                minimum = rnd_arr[i]
        return minimum


    # Значение ДСВ с максимальной вероятностью
    def min_prob(self):
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


    # Второе по вероятности значение ДСВ (max)
    def min2_prob(self):
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

    # Получение обычного числа из ДСВ разными методами
    def build_scalar(self):
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

# ----------------------------------------------------------------------------------