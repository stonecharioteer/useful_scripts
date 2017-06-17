"""

CNSViewerWidget Class.
---

This class allows users to embed a PyQt Widget that can render a CNS file.
"""
import sys
import os


from PyQt4.QtGui import (QApplication, QComboBox, QLineEdit, 
                    QTextEdit, QWidget, QVBoxLayout, QLabel,
                    QHBoxLayout, QGridLayout, QPushButton, QCheckBox,
                    QSpinBox, QPlainTextEdit, QTabWidget)

from PyQt4.QtCore import QObjectCleanupHandler
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QObject, pyqtSignal


if os.name == "nt":
    sys.path.append(r"P:\Shared_VAI\vinay_keerthi\checked_out\gknlib")
else:
    sys.path.append("/project/Shared_VAI/vinay_keerthi/checked_out/gknlib/")

from gknlib.cns import read_cns, CNS
from gknlib.interfaces import DataFrameWidget
try:
    from gknlib.interfaces import QIPythonWidget
except:
    from gknlib.interfaces.dataframenotebookwidget import QIPythonWidget


try:
    from gknlib.interfaces import LNTextEdit
except:
    from gknlib.interfaces.lntextedit import LNTextEdit


class CNSFilterOpsWidget(QWidget):
    """Widget used to build the commands."""
    #Instantiate signals here.
    add_signal = pyqtSignal()
    def __init__(self, columns, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.columns = ["NodeID","time"] + list(columns)
        self.render_ui()
        self.reset()
        self.map_events()

    def map_events(self):
        self.add_row_button.clicked.connect(self.add)
        self.ops_clear_button.clicked.connect(self.reset)
        self.ops_combobox.currentIndexChanged.connect(self.change_tooltips)

    def change_tooltips(self):
        selected_op = str(self.ops_combobox.currentText()).lower()
        tool_tip = ""
        if selected_op == "filter by":
            tool_tip = (
                    "<b>Filter Syntax: </b><br>"
                    "<p>Type in the criteria you'd like to use for filtering.</p>"
                    "<ul>"
                    "<li>Filter by a list: <b>1,3,2,23</b>, or </li>"
                    "<li>Filter by a range: <b>1:10</b>, or</li>"
                    "<li>Filter by a combination of both: <b>1:10,15:18</b></li>"
                    "<li>Filter by a criteria: <b>>1000</b>"
                    "</ul>"
                    "<p><i>To use specific constants, or functions, invoke the column names and the functions like so:</i></p>"
                    "<ul>"
                    "<li><b>sxx.max()</b></li>"
                    "<li><b>syy.min()</b></li>"
                    "<li><b>syy.min()</b></li>"
                    "</ul>"
                    )
        elif selected_op =="sort by":
            #TODO: Is this necessary?
            tool_tip = (
                    "<b>Sorting Syntax</b>:<br><br>"
                    "Specify what columns you'd like to sort by.<br><br>"
                    "<b>Accepted values</b>:<ul><li><b>sxx</b> to sort "
                    "by one column or</li>"
                    "<li><b>sxx,syy</b> to sort by sxx and then syy, or</li>"
                    "<li><b>sxx,temp,syy</b>.</li></ul><br>"
                    "<i>Space between each object is not necessary.</i>"
                    )
            tool_tip = "<b>Sorting Syntax</b>:<br><br>If you'd like the values to be sorted in Ascending order, leave blank. Else, type <b>False</b>."
        elif selected_op == "operate on":
            tool_tip = ("Operation Syntax: ")

        elif selected_op == ("plot"):
            tool_tip = ("Plotting Syntax: ")

        self.command_lineedit.setToolTip(tool_tip)

    def add(self):
        self.add_signal.emit()

    def render_ui(self):
        self.label = QLabel("Operation:")
        self.column_combobox = QComboBox()

        for column in self.columns:
            self.column_combobox.addItem(column)
        self.ops_combobox = QComboBox()
        for item in ["filter by","sort by","operate on", "plot"]:
            self.ops_combobox.addItem(item)

        self.command_lineedit = QLineEdit()

        self.ops_combobox.setToolTip("Select what you want to do.")
        self.column_combobox.setToolTip("Select what column you want to perform the operation on.")
        self.command_lineedit.setToolTip((
                                "Type the criteria. "
                                "Check the program for help. "
                                "For finding rows where all "
                                "values in column <b>a</b> is greater "
                                "than 10, type <b>a</b>>10")
            )

        self.add_row_button = QPushButton("+")
        self.add_row_button.setToolTip(("Click to send the current "
                    "action to the final instructions."))
        self.ops_clear_button = QPushButton("Clear")
        self.inplace_checkbox = QCheckBox("Modify Inplace")
        # self.backup_current_checkbox = QCheckBox("Backup Current")
        self.widget_layout = QGridLayout()
        #Add Ops widgets first.
        #Add button
        self.widget_layout.addWidget(self.label,0,0)
        self.widget_layout.addWidget(self.ops_combobox,0,1)
        self.widget_layout.addWidget(self.column_combobox,0,2)
        self.widget_layout.addWidget(self.command_lineedit,0,3,1,2)
        self.widget_layout.addWidget(self.inplace_checkbox,1,0,1,1)
        # self.widget_layout.addWidget(self.backup_current_checkbox,1,1,1,1)
        self.widget_layout.addWidget(self.add_row_button,1,2,1,1,Qt.AlignRight)
        self.widget_layout.addWidget(self.ops_clear_button,1,3,1,1,Qt.AlignLeft)
        self.setLayout(self.widget_layout)
    
    def reset(self):
        self.ops_combobox.setCurrentIndex(-1)
        self.column_combobox.setCurrentIndex(-1)
        self.command_lineedit.setText("")
    
    def get_command_string(self):
        #Check column
        command = None
        comment = None
        column_name = str(self.column_combobox.currentText())
        op_name = str(self.ops_combobox.currentText()).lower()
        
        command_string = str(self.command_lineedit.text()).lower()
        
        inplace = self.inplace_checkbox.isChecked()

        if (op_name != "") and (column_name != ""):
            comment = " #Operation: {} Column: {} Arguments: {}".format(op_name, column_name, command_string if command_string != "" else "-")
            if op_name == "filter by" and (command_string != ""):
                if column_name in ["NodeID","time"]:
                    #use get_subset
                    command = "self.df = self.df.get_subset({})"
                    if column_name == "NodeID":
                        command=command.format("nodes='{}'".format(command_string))
                    else:
                        command=command.format("timepoints='{}'".format(command_string))
                else:
                    #use loc
                    command = "self.df = self.df.loc[{}{}].copy()".format(column_name,command_string)
            
            elif op_name == "sort by":
                if column_name in ["NodeID","time"]:
                    #How to sort this way? #It's sorted by default, right?
                    command = "self.df = self.df.sort_index(by=('{}''))".format(column_name)
                else:
                    if command_string == "":
                        command = "self.df = self.df.sort(columns=['{}']')".format(column_name)
                    else:
                        command = "self.df = self.df.sort(columns=['{}'], ascending=False)".format(column_name)

            elif op_name == "operate on"and (command_string != ""):
                if column_name in self.columns[2:]:
                    command = "{}={}".format(column_name, command_string)
                else:
                    #Can't operate on Node ID and time, right?
                    comment += "\n#Unable to perform above operation as NodeID/time cannot be modified yet."
            elif op_name == "plot":
                if column_name in self.columns[2:]:
                    if (command_string == ""):
                        command = "from matplotlib import pyplot as plt\n{}.plot()\nplt.show()".format(column_name)
                    else:
                        pass
            else:
                print("Invalid input.")
                pass

        # backup_current = self.backup_current_checkbox.isChecked()
        # if backup_current:
        #     command = "self.orig_df = self.df\n{}".format(command)

        if command is not None:
            df_columns = self.columns[2:]
            if op_name != "sort by":
                for column in df_columns:
                    command = command.replace(column,"self.df.{}".format(column))
            command += comment
        return command
    
class CNSViewerWidget(QWidget):
    def __init__(self, path_to_df=None, df=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #Apply QThreading to this step for larger cns files.
        if df is None:
            self.df = read_cns(path_to_df)
        else:
            self.df = df
        self.orig_df = self.df.copy() #Make copy.
        # self.df.reset_index(inplace=True)
        self.max_rows = 10
        self.render_ui()
        self.map_events()
        self.refresh()
        self.jupyter_notebook_widget.pushVariables({"df":self.df, "orig_df":self.orig_df, "viewer":self.df_widget, "refresh":self.refresh, "display":self.display})
    
    def display(self, obj):
        try:
            html = obj._repr_html_()
        except:
            html = str(obj)
        self.df_widget.setHtml(html)

    def render_ui(self):
        """Builds the UI"""
        self.tab_widget = QTabWidget()
        
        #Filter Ops tab
        self.filter_ops_widget = CNSFilterOpsWidget(columns=self.df.columns)
        commands_widget = QWidget()
        self.command_label = QLabel("Command:")
        self.command_text_area = LNTextEdit()
        self.command_text_area.edit.setReadOnly(True)
        self.command_show_button = QPushButton("Apply")
        self.command_editable_checkbox = QCheckBox("Editable")
        self.command_editable_checkbox.setChecked(False)
        commands_widget_layout = QGridLayout()
        commands_widget_layout.addWidget(self.filter_ops_widget,0,0,2,2,Qt.AlignTop)
        commands_widget_layout.addWidget(self.command_label,2,0,1,1,Qt.AlignLeft | Qt.AlignTop)
        commands_widget_layout.addWidget(self.command_text_area,3,0,2,2, Qt.AlignTop)
        commands_widget_layout.addWidget(self.command_editable_checkbox,5,0,1,0,Qt.AlignLeft)
        commands_widget_layout.addWidget(self.command_show_button,5,1,1,1,Qt.AlignRight)
        commands_widget.setLayout(commands_widget_layout)
        
        # self.tab_widget.addTab(self.filter_ops_widget, "n00b Mode")

        #Commands Tab
        self.tab_widget.addTab(commands_widget, "Raw Commands")
        
        ipython_filter_widget = QWidget()
        self.jupyter_notebook_widget = QIPythonWidget()
        ipython_filter_widget_layout = QVBoxLayout()
        ipython_filter_widget_layout.addWidget(self.jupyter_notebook_widget)
        ipython_filter_widget.setLayout(ipython_filter_widget_layout)
        self.tab_widget.addTab(ipython_filter_widget, "Jupyter Mode")
        
        self.view_combobox = QComboBox()
        modes = ["Show First","Show Last", "All", "Describe","Filtered"]
        for mode in modes: 
            self.view_combobox.addItem(mode)

        self.max_rows_spinbox = QSpinBox()
        #Map the change event to refresh the dataframe.
        self.max_rows_spinbox.setMinimum(0)
        self.max_rows_spinbox.setMaximum(self.df.shape[0])
        self.max_rows_spinbox.setValue(self.max_rows)
        self.max_rows_spinbox.setSuffix(" rows")
        
        self.refresh_button = QPushButton("Refresh")

        self.df_widget = QTextEdit()
        self.df_widget.setReadOnly(True)
        
        self.save_button = QPushButton("Save File")

        df_layout = QGridLayout()
        df_layout.addWidget(self.view_combobox,0,0)
        df_layout.addWidget(self.max_rows_spinbox,0,1)
        df_layout.addWidget(self.refresh_button,0,2)
        df_layout.addWidget(self.df_widget,1,0,4,10)

        layout = QGridLayout()
        layout.addWidget(self.tab_widget,0,0,3,1, Qt.AlignLeft | Qt.AlignTop)
        layout.addLayout(df_layout,0,1,7,7)
        layout.addWidget(self.save_button,3,0,1,1,Qt.AlignLeft)
        self.setLayout(layout)


    def map_events(self):
        self.refresh_button.clicked.connect(self.refresh)
        self.view_combobox.currentIndexChanged.connect(self.toggle_max_rows)
        self.command_show_button.clicked.connect(self.exec_command)
        self.filter_ops_widget.add_signal.connect(self.add_filter_op)
        self.command_editable_checkbox.stateChanged.connect(self.toggle_command_area)

    def toggle_command_area(self):
        self.command_text_area.edit.setReadOnly(not(self.command_editable_checkbox.isChecked()))

    def add_filter_op(self):
        command = self.filter_ops_widget.get_command_string()
        existing_commands = str(self.command_text_area.edit.toPlainText()).strip()
        if existing_commands!="":
            command = "\n{}".format(command)
        self.command_text_area.edit.appendPlainText(command)
        self.filter_ops_widget.reset()

    def exec_command(self):
        #Reset df to original.
        self.df = self.orig_df.copy()
        command = str(self.command_text_area.getText())
        try:
            exec(command)
        except Exception as e:
            print("Failed to execute!")
            print(repr(e))
        self.view_combobox.setCurrentIndex(4)
        self.refresh()

    def toggle_max_rows(self):
        mode = str(self.view_combobox.currentText()).lower()
        if mode in ["show first", "show last"]:
            self.max_rows_spinbox.setEnabled(True)
        else:
            self.max_rows_spinbox.setEnabled(False)

    def refresh(self):
        mode = str(self.view_combobox.currentText()).lower()
        if mode == "show first":
            self.max_rows = self.max_rows_spinbox.value()
            self.df_widget.setHtml(self.df.head(n=self.max_rows)._repr_html_())
        elif mode == "show last":
            self.max_rows = self.max_rows_spinbox.value()
            self.df_widget.setHtml(self.df.tail(n=self.max_rows)._repr_html_())
        elif mode == "describe":
            self.df_widget.setHtml(self.df.describe()._repr_html_())
        elif mode == "filtered":
            self.df_widget.setHtml(self.df._repr_html_())
        else:
            self.df_widget.setHtml(self.df._repr_html_())

if __name__ == "__main__":
    import sys
    _app = QApplication(sys.argv)
    try:
        app = CNSViewerWidget(sys.argv[1])
    except:
        from gknlib.cns import generate_random_cns
        app = CNSViewerWidget(df=generate_random_cns())
    app.setWindowTitle("CNSViewerWidget Demo")
    app.show()
    _app.exec_()