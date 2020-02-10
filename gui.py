import sys
import matplotlib
matplotlib.use('Qt5Agg')
import engine
from PyQt5 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("GraphPlan Visualization by Almog Dubin")

        self._construct_menu()

        sc = MplCanvas(self, width=5, height=4, dpi=100)
        sc.axes.plot([0,1,2,3,4], [10,1,20,3,40])

        # Create toolbar, passing canvas as first parament, parent (self, the MainWindow) as second.
        toolbar = NavigationToolbar(sc, self)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(sc)

        # Create a placeholder widget to hold our toolbar and canvas.
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.show()

    def _construct_menu(self):
        # File menu
        self.file_menu = QtWidgets.QMenu('&File', self)
        self.file_menu.addAction('&Load Domain', self.file_load_domain)
        self.file_menu.addAction('&Load problem', self.file_load_problem)

        self.file_menu.addAction('&Quit', self.file_quit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        # Action menu
        self.menuBar().addSeparator()
        self.action_menu = QtWidgets.QMenu('&Action', self)
        self.action_menu.addAction('&Expand level', self.action_expand_level,
                                   QtCore.Qt.CTRL + QtCore.Qt.Key_E)
        self.action_menu.addAction('&Solve', self.action_solve,
                                   QtCore.Qt.CTRL + QtCore.Qt.Key_S)
        self.action_menu.addAction('&Reset', self.action_reset_graph,
                                   QtCore.Qt.CTRL + QtCore.Qt.Key_R)
        self.menuBar().addMenu(self.action_menu)

        # View menu
        self.menuBar().addSeparator()
        self.view_menu = QtWidgets.QMenu('&View', self)
        self.view_menu.addAction('&Show mutexes', self.view_mutexes,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_M)
        self.menuBar().addMenu(self.view_menu)

        # Help menu
        self.menuBar().addSeparator()
        self.help_menu = QtWidgets.QMenu('&Help', self)
        self.menuBar().addMenu(self.help_menu)

        self.help_menu.addAction('&About', self.about)
    def closeEvent(self, ce):
        self.file_quit()

    def file_quit(self):
        self.close()

    def file_load_domain(self):
        # TODO this
        self._load_file()
        pass

    def file_load_problem(self):
        # TODO this
        self._load_file()
        pass

    def _load_file(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()",
                                                             "", "pddl plan files (*.pddl)", options=options)
        if not file_path.endswith(".pddl"):
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('file is not a .pddl format!')
        return file_path

    def about(self):
        # TODO this
        QtWidgets.QMessageBox.about(self, "About", "e")

    def action_expand_level(self):
        # TODO this
        pass

    def action_solve(self):
        # TODO this
        pass

    def action_reset_graph(self):
        # TODO this
        pass

    def view_mutexes(self):
        # TODO this
        pass

    def show_no_ops(self):
        # TODO this
        pass

app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
app.exec_()