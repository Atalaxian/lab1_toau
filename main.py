import pickle
import sys
from os import listdir, system
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QPainter, QPdfWriter, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QListWidgetItem, \
    QTableWidgetItem, QCheckBox, QHBoxLayout
from main_window_v2 import Ui_MainWindow
from save_load import Ui_Form
from error_window import Ui_widget
from pulp import LpVariable, LpProblem, lpSum, LpMinimize
import datetime


def str_variables(number):
    for x in range(number):
        yield 'x' + str(x + 1)


class SaveLoad(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setWindowTitle('Загрузка и сохранение')


class ErrorWindow(QWidget, Ui_widget):
    def __init__(self, log):
        super().__init__()
        self.setupUi(self)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.error_label.setText(log)
        self.setWindowIcon(QIcon('error_icon.jpg'))


class MainWindow(QMainWindow, Ui_MainWindow):
    error_window = None
    number_production = 1
    number_raw_material = 1
    number_equipment = 1
    number_worker = 1
    number_assort_group = 1
    integer_data = True
    end_value = []
    result_funk = None
    start_stocks = None
    start_minimize_price = None
    start_minimize_cost = None
    start_limits_raw_materials = None
    start_equipment = None
    start_time_fond = None
    start_worker = None
    start_price_hour = None
    start_time_fond_worker = None
    start_groups = None
    start_min_number = None
    start_max_number = None
    fond_pay = None
    file_work_ui = None
    load_check = False
    float_values = False

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('Задача объёмного планирования')
        self.back.clicked.connect(self.go_back)
        self.save_result.clicked.connect(self.save_result_in_file)
        self.save_raw_data.triggered.connect(self.save)
        self.load_raw_data.triggered.connect(self.load)
        self.spinBox_1.valueChanged.connect(self.first_change)
        self.spinBox_2.valueChanged.connect(self.second_change)
        self.spinBox_3.valueChanged.connect(self.third_changed)
        self.spinBox_4.valueChanged.connect(self.fourth_changed)
        self.spinBox_5.valueChanged.connect(self.fifth_changed)
        self.solution.clicked.connect(self.calculate)
        self.check_float.stateChanged.connect(self.funk_check_float)
        self.set_layout()

    @QtCore.pyqtSlot()
    def go_back(self):
        self.stackedWidget.setCurrentIndex(0)

    @QtCore.pyqtSlot(int)
    def funk_check_float(self, state):
        if state == 2:
            self.float_values = True
        else:
            self.float_values = False

    @QtCore.pyqtSlot(int)
    def first_change(self, value_box: int) -> None:
        self.load_check = False
        self.number_production = value_box
        self.minimize.setColumnCount(value_box)
        for x in range(value_box):
            elem = QTableWidgetItem(str(x + 1))
            elem.setTextAlignment(QtCore.Qt.AlignCenter)
            self.minimize.setItem(0, x, elem)
        self.raw_material.setColumnCount(value_box + 1)
        self.equipment_price.setColumnCount(value_box + 1)
        self.worker_price.setColumnCount(value_box + 2)
        for y in range(self.raw_material.columnCount() - 1):
            self.raw_material.setHorizontalHeaderItem(y, QTableWidgetItem(str(y + 1)))
            self.equipment_price.setHorizontalHeaderItem(y, QTableWidgetItem(str(y + 1)))
            self.worker_price.setHorizontalHeaderItem(y, QTableWidgetItem(str(y + 1)))
        self.raw_material.setHorizontalHeaderItem(self.raw_material.columnCount() - 1, QTableWidgetItem('Запасы сырья'))
        self.equipment_price.setHorizontalHeaderItem(self.equipment_price.columnCount() - 1, QTableWidgetItem('Фонд'))
        self.worker_price.setHorizontalHeaderItem(self.worker_price.columnCount() - 1, QTableWidgetItem('Фонд времени'))
        self.worker_price.setHorizontalHeaderItem(self.worker_price.columnCount() - 2,
                                                  QTableWidgetItem('Цена одного часа'))
        self.assort_group.setColumnCount(value_box)
        for x in range(self.number_assort_group):
            for y in range(value_box):
                check = QCheckBox()
                cell_widget = QWidget()
                lay_out = QHBoxLayout(cell_widget)
                lay_out.addWidget(check)
                lay_out.setAlignment(QtCore.Qt.AlignCenter)
                lay_out.setContentsMargins(0, 0, 0, 0)
                cell_widget.setLayout(lay_out)
                self.assort_group.setCellWidget(x, y, cell_widget)
        self.set_layout()

    @QtCore.pyqtSlot(int)
    def second_change(self, value_box: int) -> None:
        self.load_check = False
        self.number_raw_material = value_box
        self.raw_material.setRowCount(value_box)
        for x in range(value_box):
            item_widget = QTableWidgetItem('Сырьё №' + str(x + 1))
            self.raw_material.setVerticalHeaderItem(x, item_widget)
        self.set_layout()

    @QtCore.pyqtSlot(int)
    def third_changed(self, value_box: int) -> None:
        self.load_check = False
        self.number_equipment = value_box
        self.equipment_price.setRowCount(value_box)
        for x in range(value_box):
            item_widget = QTableWidgetItem('Оборуд. №' + str(x + 1))
            self.equipment_price.setVerticalHeaderItem(x, item_widget)
        self.set_layout()

    @QtCore.pyqtSlot(int)
    def fourth_changed(self, value_box: int) -> None:
        self.load_check = False
        self.number_worker = value_box
        self.worker_price.setRowCount(value_box)
        for x in range(value_box):
            item_widget = QTableWidgetItem('Спец. №' + str(x + 1))
            self.worker_price.setVerticalHeaderItem(x, item_widget)
        self.set_layout()

    @QtCore.pyqtSlot(int)
    def fifth_changed(self, value_box: int) -> None:
        self.load_check = False
        self.number_assort_group = value_box
        self.assort_group.setRowCount(value_box)
        self.limits_assort_group.setRowCount(value_box)
        for x in range(value_box):
            item_widget = QTableWidgetItem('Группа. №' + str(x + 1))
            item_2 = item_widget.clone()
            self.assort_group.setVerticalHeaderItem(x, item_widget)
            self.limits_assort_group.setVerticalHeaderItem(x, item_2)
            for y in range(self.number_production):
                check = QCheckBox()
                cell_widget = QWidget()
                lay_out = QHBoxLayout(cell_widget)
                lay_out.addWidget(check)
                lay_out.setAlignment(QtCore.Qt.AlignCenter)
                lay_out.setContentsMargins(0, 0, 0, 0)
                cell_widget.setLayout(lay_out)
                self.assort_group.setCellWidget(x, y, cell_widget)
        self.set_layout()

    def load_data_from_ui(self):
        if self.float_values:
            funk = float
        else:
            funk = int
        self.start_minimize_price = [funk(self.minimize.item(1, x).text()) for x in range(self.number_production)]
        self.start_minimize_cost = [funk(self.minimize.item(2, x).text()) for x in range(self.number_production)]
        self.start_limits_raw_materials = [[funk(self.raw_material.item(x, y).text())
                                            for y in range(self.number_production)]
                                           for x in range(self.number_raw_material)]
        self.start_stocks = [funk(self.raw_material.item(x, self.number_production).text())
                             for x in range(self.number_raw_material)]
        self.start_equipment = [[funk(self.equipment_price.item(x, y).text()) for y in range(self.number_production)]
                                for x in range(self.number_equipment)]
        self.start_time_fond = [funk(self.equipment_price.item(x, self.number_production).text())
                                for x in range(self.number_equipment)]
        self.start_worker = [[funk(self.worker_price.item(x, y).text()) for y in range(self.number_production)]
                             for x in range(self.number_worker)]
        self.start_price_hour = [funk(self.worker_price.item(x, self.number_production).text())
                                 for x in range(self.number_worker)]
        self.start_time_fond_worker = [funk(self.worker_price.item(x, self.number_production + 1).text())
                                       for x in range(self.number_worker)]
        widgets = self.assort_group.findChildren(QCheckBox)
        groups = [[widgets[y + self.number_production * x].isChecked() for y in range(self.number_production)]
                  for x in range(self.number_assort_group)]
        self.start_groups = [[y + 1 for y in range(self.number_production) if groups[x][y] is True]
                             for x in range(self.number_assort_group)]
        self.start_min_number = [funk(self.limits_assort_group.item(x, 0).text())
                                 for x in range(self.number_assort_group)]
        self.start_max_number = [funk(self.limits_assort_group.item(x, 1).text())
                                 for x in range(self.number_assort_group)]
        self.fond_pay = funk(self.fond.text())

    @QtCore.pyqtSlot()
    def calculate(self):
        if not self.load_check:
            try:
                self.load_data_from_ui()
            except AttributeError:
                self.error_window = ErrorWindow('Ошибка! Введены не все значений.')
                self.error_window.show()
                return
            except ValueError:
                self.error_window = ErrorWindow('Ошибка! Введённые значения не могут быть преобразованы в числа.')
                self.error_window.show()
                return
        else:
            self.load_check = False
        names = str_variables(self.number_production + 1)
        variables = [LpVariable(x, lowBound=0, cat='Continuous') for x in names]
        problem = LpProblem('0', LpMinimize)
        problem += lpSum([self.start_minimize_cost[x] * variables[x] for x in range(self.number_production)])
        for x in range(self.number_raw_material):
            problem += lpSum([self.start_limits_raw_materials[x][y] * variables[y]
                              for y in range(self.number_production)]) <= self.start_stocks[x] * variables[
                           self.number_production]
        for x in range(self.number_equipment):
            problem += lpSum([self.start_equipment[x][y] * variables[y]
                              for y in range(self.number_production)]) <= self.start_time_fond[x] * variables[
                           self.number_production]
        for x in range(self.number_worker):
            problem += lpSum([self.start_worker[x][y] * variables[y]
                              for y in range(self.number_production)]) <= self.start_time_fond_worker[x] * variables[
                           self.number_production]
        values = []
        for y in range(self.number_production):
            values.append(sum([self.start_worker[x][y] * self.start_price_hour[x] for x in range(self.number_worker)]))
        problem += lpSum([values[y] * variables[y]
                          for y in range(self.number_production)]) <= self.fond_pay * variables[self.number_production]
        for x in range(self.number_assort_group):
            problem += lpSum([variables[value - 1]] for count, value in enumerate(self.start_groups[x])) \
                       <= self.start_max_number[x] * variables[self.number_production]
            problem += lpSum([variables[value - 1]] for count, value in enumerate(self.start_groups[x])) >= \
                       self.start_min_number[x] * variables[self.number_production]
        problem += lpSum([self.start_minimize_price[x] * variables[x] for x in range(self.number_production)]) == 1

        problem.solve()
        if problem.status != 1:
            self.error_window = ErrorWindow('Ошибка! Система уравнений не имеет решения.')
            self.error_window.show()
            return
        values = [variable.varValue for variable in problem.variables()]
        self.end_value = []
        for i, my_value in enumerate(values):
            if i != len(values) - 1:
                self.end_value.append(round(my_value / values[len(values) - 1], 4))
        funk_numerator = 0
        funk_denominator = 0
        for x, price in enumerate(self.start_minimize_cost):
            funk_numerator += price * self.end_value[x]
        for x, price in enumerate(self.start_minimize_price):
            funk_denominator += price * self.end_value[x]
        self.result_funk = round(funk_numerator / funk_denominator, 4)
        self.result_funk = round(funk_numerator / funk_denominator, 4)
        self.stackedWidget.setCurrentIndex(1)
        self.result_func_UI.setText(str(self.result_funk))
        self.result_UI.setColumnCount(self.number_production)
        self.result_UI.setRowCount(1)
        for count, result in enumerate(self.end_value):
            header = 'X' + str(count + 1)
            self.result_UI.setHorizontalHeaderItem(count, QTableWidgetItem(header))
            self.result_UI.setItem(0, count, QTableWidgetItem(str(result)))
        self.result_UI.resizeColumnsToContents()
        self.result_UI.resizeRowsToContents()

    def select_file(self, value_file):
        vl = value_file.text()
        pathFile = 'saves/' + vl
        self.load_data_from_ui()
        file = open(pathFile, "wb")
        pickle.dump(self.number_production, file)
        pickle.dump(self.number_raw_material, file)
        pickle.dump(self.number_equipment, file)
        pickle.dump(self.number_worker, file)
        pickle.dump(self.number_assort_group, file)
        pickle.dump(self.integer_data, file)
        pickle.dump(self.start_stocks, file)
        pickle.dump(self.start_minimize_price, file)
        pickle.dump(self.start_minimize_cost, file)
        pickle.dump(self.start_limits_raw_materials, file)
        pickle.dump(self.start_equipment, file)
        pickle.dump(self.start_time_fond, file)
        pickle.dump(self.start_worker, file)
        pickle.dump(self.start_price_hour, file)
        pickle.dump(self.start_time_fond_worker, file)
        pickle.dump(self.start_groups, file)
        pickle.dump(self.start_min_number, file)
        pickle.dump(self.start_max_number, file)
        pickle.dump(self.fond_pay, file)
        pickle.dump(self.float_values, file)
        file.close()
        self.file_work_ui.close()

    def load_file(self, value_file):
        file = value_file.text()
        pathFile = 'saves/' + file
        file = open(pathFile, "rb")
        self.number_production = pickle.load(file)
        self.spinBox_1.setValue(self.number_production)
        self.number_raw_material = pickle.load(file)
        self.spinBox_2.setValue(self.number_raw_material)
        self.number_equipment = pickle.load(file)
        self.spinBox_3.setValue(self.number_equipment)
        self.number_worker = pickle.load(file)
        self.spinBox_4.setValue(self.number_worker)
        self.number_assort_group = pickle.load(file)
        self.spinBox_5.setValue(self.number_assort_group)
        self.integer_data = pickle.load(file)
        self.start_stocks = pickle.load(file)
        for x in range(self.number_raw_material):
            elem = QTableWidgetItem(str(self.start_stocks[x]))
            elem.setTextAlignment(QtCore.Qt.AlignCenter)
            self.raw_material.setItem(x, self.number_production, elem)
        self.start_minimize_price = pickle.load(file)
        for y in range(self.number_production):
            elem = QTableWidgetItem(str(self.start_minimize_price[y]))
            elem.setTextAlignment(QtCore.Qt.AlignCenter)
            self.minimize.setItem(1, y, elem)
        self.start_minimize_cost = pickle.load(file)
        for y in range(self.number_production):
            elem = QTableWidgetItem(str(self.start_minimize_cost[y]))
            elem.setTextAlignment(QtCore.Qt.AlignCenter)
            self.minimize.setItem(2, y, elem)
        self.start_limits_raw_materials = pickle.load(file)
        for x in range(self.number_raw_material):
            for y in range(self.number_production):
                elem = QTableWidgetItem(str(self.start_limits_raw_materials[x][y]))
                elem.setTextAlignment(QtCore.Qt.AlignCenter)
                self.raw_material.setItem(x, y, elem)
        self.start_equipment = pickle.load(file)
        for x in range(self.number_equipment):
            for y in range(self.number_production):
                elem = QTableWidgetItem(str(self.start_equipment[x][y]))
                elem.setTextAlignment(QtCore.Qt.AlignCenter)
                self.equipment_price.setItem(x, y, elem)
        self.start_time_fond = pickle.load(file)
        for x in range(self.number_equipment):
            elem = QTableWidgetItem(str(self.start_time_fond[x]))
            elem.setTextAlignment(QtCore.Qt.AlignCenter)
            self.equipment_price.setItem(x, self.number_production, elem)
        self.start_worker = pickle.load(file)
        for x in range(self.number_worker):
            for y in range(self.number_production):
                elem = QTableWidgetItem(str(self.start_worker[x][y]))
                elem.setTextAlignment(QtCore.Qt.AlignCenter)
                self.worker_price.setItem(x, y, elem)
        self.start_price_hour = pickle.load(file)
        for x in range(self.number_worker):
            elem = QTableWidgetItem(str(self.start_price_hour[x]))
            elem.setTextAlignment(QtCore.Qt.AlignCenter)
            self.worker_price.setItem(x, self.number_production, elem)
        self.start_time_fond_worker = pickle.load(file)
        for x in range(self.number_worker):
            elem = QTableWidgetItem(str(self.start_time_fond_worker[x]))
            elem.setTextAlignment(QtCore.Qt.AlignCenter)
            self.worker_price.setItem(x, self.number_production + 1, elem)
        self.start_groups = pickle.load(file)
        for x in range(self.number_assort_group):
            for y in range(self.number_production):
                check = QCheckBox()
                need_row = self.start_groups[x]
                if (y + 1) in need_row:
                    check.setChecked(True)
                cell_widget = QWidget()
                lay_out = QHBoxLayout(cell_widget)
                lay_out.addWidget(check)
                lay_out.setAlignment(QtCore.Qt.AlignCenter)
                lay_out.setContentsMargins(0, 0, 0, 0)
                cell_widget.setLayout(lay_out)
                self.assort_group.setCellWidget(x, y, cell_widget)
        self.start_min_number = pickle.load(file)
        for x in range(self.number_assort_group):
            elem = QTableWidgetItem(str(self.start_min_number[x]))
            elem.setTextAlignment(QtCore.Qt.AlignCenter)
            self.limits_assort_group.setItem(x, 0, elem)
        self.start_max_number = pickle.load(file)
        for x in range(self.number_assort_group):
            elem = QTableWidgetItem(str(self.start_max_number[x]))
            elem.setTextAlignment(QtCore.Qt.AlignCenter)
            self.limits_assort_group.setItem(x, 1, elem)
        self.fond_pay = pickle.load(file)
        self.fond.setText(str(self.fond_pay))
        self.float_values = pickle.load(file)
        if self.float_values:
            self.check_float.setChecked(True)
        file.close()
        self.load_check = True
        self.file_work_ui.close()

    def save(self):
        self.file_work_ui = SaveLoad()
        list_file = listdir(path='saves')
        self.file_work_ui.groupBox.setTitle("Сохранение")
        self.file_work_ui.listWidget.clear()
        for elem in list_file:
            self.file_work_ui.listWidget.addItem(QListWidgetItem(elem))
        self.file_work_ui.listWidget.itemDoubleClicked.connect(self.select_file)
        self.file_work_ui.show()

    def load(self):
        self.file_work_ui = SaveLoad()
        list_file = listdir(path='saves')
        self.file_work_ui.groupBox.setTitle("Загрузка")
        self.file_work_ui.listWidget.clear()
        for elem in list_file:
            self.file_work_ui.listWidget.addItem(QListWidgetItem(elem))
        self.file_work_ui.listWidget.itemDoubleClicked.connect(self.load_file)
        self.file_work_ui.show()

    @QtCore.pyqtSlot()
    def save_result_in_file(self):
        string = str(datetime.datetime.today().strftime("%m.%d.%Y")) + '__' + str(
            datetime.datetime.today().strftime("%H.%M.%S")) + '.pdf'
        writer = QPdfWriter(string)
        writer.setTitle('Результат работы программы')
        writer.setCreator('Агарков С. Е.')
        painter = QPainter()
        painter.begin(writer)
        pen = QtGui.QPen(QtGui.QColor(QtCore.Qt.blue), 5,
                         style=QtCore.Qt.DotLine)
        painter.setPen(pen)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawRect(0, 0, writer.width(), writer.height())
        color = QtGui.QColor(QtCore.Qt.black)
        painter.setPen(QtGui.QPen(color))
        painter.setBrush(QtGui.QBrush(color))
        font = QtGui.QFont("Verdana", pointSize=10)
        painter.setFont(font)
        painter.drawText(10, 10,
                         writer.width() - 20, 500, QtCore.Qt.AlignLeft,
                         ('Запасы сырья: ' + str(self.start_stocks)))
        painter.drawText(10, 210,
                         writer.width() - 20, 500, QtCore.Qt.AlignLeft,
                         ('Себестоимость: ' + str(self.start_minimize_cost)))
        painter.drawText(10, 410,
                         writer.width() - 20, 500, QtCore.Qt.AlignLeft,
                         ('Отптовая цена: ' + str(self.start_minimize_price)))
        painter.drawText(10, 610,
                         writer.width() - 20, 500, QtCore.Qt.AlignLeft,
                         ('Максимальные затраты материалов: ' + str(self.start_limits_raw_materials)))
        painter.drawText(10, 1010,
                         writer.width() - 20, 500, QtCore.Qt.AlignLeft,
                         ('Затраты времени оборудования: ' + str(self.start_equipment)))
        painter.drawText(10, 1210,
                         writer.width() - 20, 500, QtCore.Qt.AlignLeft,
                         ('Фонд времени оборудования: ' + str(self.start_time_fond)))
        painter.drawText(10, 1410,
                         writer.width() - 20, 500, QtCore.Qt.AlignLeft,
                         ('Затраты времени рабочих: ' + str(self.start_worker)))
        painter.drawText(10, 1610,
                         writer.width() - 20, 500, QtCore.Qt.AlignLeft,
                         ('Фонд времени рабочих: ' + str(self.start_time_fond_worker)))
        painter.drawText(10, 1810,
                         writer.width() - 20, 500, QtCore.Qt.AlignLeft,
                         ('Ассортиментные группы: ' + str(self.start_groups)))
        painter.drawText(10, 2010,
                         writer.width() - 20, 500, QtCore.Qt.AlignLeft,
                         ('Ограничения ассортиментных групп на минимум: ' + str(self.start_min_number)))
        painter.drawText(10, 2210,
                         writer.width() - 20, 500, QtCore.Qt.AlignLeft,
                         ('Ограничения ассортиментных групп на максимум: ' + str(self.start_max_number)))
        painter.drawText(10, 2410,
                         writer.width() - 20, 500, QtCore.Qt.AlignLeft,
                         ('Фонд ЗП: ' + str(self.fond_pay)))
        painter.drawText(10, 2610,
                         writer.width() - 20, 500, QtCore.Qt.AlignLeft,
                         ('Итоговые значения: ' + str(self.end_value)))
        painter.drawText(10, 2810,
                         writer.width() - 20, 500, QtCore.Qt.AlignLeft,
                         ('Значение функции: ' + str(self.result_funk)))
        painter.end()
        system(string)


if __name__ == '__main__':
    qapp = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(qapp.exec())
