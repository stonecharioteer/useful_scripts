#!/usr/bin/env python3
# vim encoding=utf-8
"""
    Custom PyQt4 class for the FileExplorerWidget.
    Thus is going to be a wrapper around either QTreeView or QTreeWidget,
    and it will list out a folder's entire directory in an easy to traverse 
    fashion.
    Ideally it should do this:
        * Show folder heirarchy.
        * Show folder/file details:
            - name
            - file size / size of folder(if possible)
            - file owner
            - file modification time
            - file creation time (If possible)
            - file rights (needed>)
            - Number of sub-entities. (NA for files, file and subfolder count for folders.)
        * Allow addition of columns with entries for each item.
            - Users might want to add details like some specific file mask
        * Have a checkable mode, where folders and/or files can be checked.
            - Appropriately, needs to be able to return the checked paths list.
        * Have a way to show only specific file formats.
            - Need this as a filtering algorithm.
        * Have a way to set color for a specific row.
        * Permit sorting by column.

    Threading ideas:
    I need to write a method that quickly traverses a folder structure, 
    using multiprocessing and writes to a cached file, perhaps.
    

    NEW ALGORITHM:

    First, just show all files/folders in the first level of the heirarchy.
    On clicking any item in the tree, if it is a folder, 
    get the dataframe for the first level of that folder,
    and concatenate it with the existing df.
    Display again.
"""

import os
import sys
import shutil
import subprocess
import datetime

from PyQt4 import QtCore
from PyQt4 import QtGui

import pandas as pd

if os.name == "posix":
    path_to_modules = os.path.normpath("//project/las_india/scripts/development/gkncodebase")
else:
    path_to_modules = os.path.normpath(r"\\caeroot\project\las_india\scripts\development\gkncodebase")
    
if os.path.exists(path_to_modules):
    sys.path.append(path_to_modules)
else:
    raise Exception("Modules are inaccessible! {} doesn't exist!".format(path_to_modules))

from algorithms.PathMethods import list_all_files_in_folder
from lasmethods.LASMethods import parse_LAS_results_xml

class FolderLoader(QtCore.QThread):
    send_dataframe = QtCore.pyqtSignal(pd.DataFrame, list)
    send_message = QtCore.pyqtSignal(str)
    def __init__(self):
        super(FolderLoader, self).__init__()
        self.mutex = QtCore.QMutex()
        self.condition = QtCore.QWaitCondition()
        if not self.isRunning():
            self.start(QtCore.QThread.HighPriority)

    def run(self):
        while True:
            self.allow_run = False
            if self.allow_run:
                pass


    def __del__(self):
        self.mutex.lock()
        self.condition.wakeOne()
        self.mutex.unlock()
        self.wait()
    
    def get_file_dataframe(self, start_path): 
        import time
        output_matrix = []
        column_names = [
                        "Parent Folder", "Path",
                        "Name", 
                        "Area Description", 
                        "Configuration", 
                        "Results",
                        "Modification Time",
                        "Owner"
                        ]
        last_sending_time = datetime.datetime.now()
        counter = 0
        results_paths = []
        for root, directories, filenames in os.walk(start_path):
            file_paths = [os.path.join(root, f) for f in filenames]
            folders = [os.path.join(root, d) for d in directories]
            folder_contents = file_paths + folders
            for file_path in folder_contents:
                file_name = os.path.basename(file_path)
                if file_name == "results.xml":
                    results_paths.append(root)
                row = {}
                parent_folder = os.path.split(file_path)[0]
                row["Parent Folder"] = parent_folder
                row["Path"] = file_path
                row["Name"] = os.path.basename(file_path)
                row["Area Description"] = "-"
                row["Configuration"] = "-"
                has_results = False
                results_file = None
                for result_path in results_paths:
                    if file_path.startswith(os.path.join(os.path.abspath(result_path),"")):
                        has_results = True
                        results_file = os.path.join(result_path,"results.xml")
                        break
                row["Results"] = "Y" if has_results else "N"
                if has_results:
                    results_dict = parse_LAS_results_xml(results_file)
                    config = str(results_dict["Configuration"])
                    release_state = str(results_dict["Release State"])
                    row["Configuration"] = config + " - " + release_state
                    containing_folder_name = os.path.basename(parent_folder)
                    area_descript = results_dict["Area Dict"].get(containing_folder_name)
                    if area_descript is not None:
                        row["Area Description"] = area_descript

                mtime, owner = get_file_details(file_path)
                row["Modification Time"] = mtime
                row["Owner"] = owner
                output_matrix.append(row)
                now = datetime.datetime.now()
                time_since_last_sending = (now - last_sending_time).total_seconds()
                counter += 1
                
                if time_since_last_sending > 220 or counter == 1:
                    df = pd.DataFrame(output_matrix, columns=column_names)
                    print(file_path)
                    last_sending_time = now
                    self.send_dataframe.emit(df, results_paths)
                    QtGui.QApplication.processEvents()
        self.send_dataframe.emit(df, results_paths)
        print("Done")

def get_file_dataframe(file_list, start_path):
    """
        This method lists all files in the search path
        Need to implement a threaded, or possibly a
        multiprocessing version of this
        as it will be really slow.
        TODO:
            Right now, this takes forever to open because it builds a 
            list of all files and folders. Instead, it would be better 
            to show only 1 level of folders and show more on request.
        Also:
        The dataframe needs additional columns.
            1. Area Name
            2. LAS Run Done? Does the results.xml file exist in the base path?
            3. 
    """
    import time
    #d = start_path
    #print("Listing all files in {}.".format(start_path))
    #file_list = list_all_files_in_folder(start_path, check_subfolders=True)
    #print("{} files found in {}.".format(len(file_list), start_path))

    output_matrix = []
    results_paths = [os.path.dirname(x) for x in file_list if os.path.basename(x) == "results.xml"]
    column_names = [
                    "Parent Folder", "Path",
                    "Name", 
                    "Area Description", 
                    "Configuration", 
                    "Results",
                    "Modification Time",
                    "Owner"
                    ]

    for file_path in file_list:
        row = {}
        parent_folder = os.path.split(file_path)[0]
        row["Parent Folder"] = parent_folder
        row["Path"] = file_path
        row["Name"] = os.path.basename(file_path)
        row["Area Description"] = "-"
        row["Configuration"] = "-"
        has_results = False
        results_file = None
        for result_path in results_paths:
            if file_path.startswith(os.path.join(os.path.abspath(result_path),"")):
                has_results = True
                results_file = os.path.join(result_path,"results.xml")
                break
        row["Results"] = "Y" if has_results else "N"
        if has_results:
            results_dict = parse_LAS_results_xml(results_file)
            config = str(results_dict["Configuration"]) + " - " + str(results_dict["Release State"])
            row["Configuration"] = config
            containing_folder_name = os.path.basename(parent_folder)
            area_descript = results_dict["Area Dict"].get(containing_folder_name)
            if area_descript is not None:
                row["Area Description"] = area_descript

        mtime, owner = get_file_details(file_path)
        row["Modification Time"] = mtime
        row["Owner"] = owner
        output_matrix.append(row)
    return pd.DataFrame(output_matrix, columns=column_names), results_paths


def get_file_details(file_path):
    import time
    import os
    if os.name == "posix":
        import pwd
        #Linux only.
        owner = pwd.getpwuid(os.stat(file_path).st_uid)
        owner_string = "{} - {}".format(owner[0], owner[-3])
    else:
        from commonoperations.WindowsMethods import get_file_owner
        owner_string = get_file_owner(file_path)
    mtime = time.ctime(os.path.getmtime(file_path))
    return mtime, owner_string


class FileExplorerWidget(QtGui.QTreeWidget):
    def __init__(self, start_path):
        super(FileExplorerWidget, self).__init__()
        self.file_df = None
        self.start_path = start_path
        self.load_path(start_path)
        self.create_ui()
        self.map_events()
        self.visualize()
        #self.file_loader = FolderLoader()
        #self.file_loader.send_dataframe.connect(self.show_df)
        #self.file_loader.get_file_dataframe(start_path)

    def show_df(self, df, results_paths):
        self.file_df = df
        self.results_paths = results_paths
        self.create_ui()

    def create_ui(self):
        if self.file_df is not None:
            self.show_tree(self.file_df)
        else:
            print("Nothing to display!")
        
    
    def visualize(self):
        self.show()
    
    def load_path(self, file_path):
        """Needs to get the df for 1 level in this path."""
        file_list = [os.path.join(file_path, x) for x in os.listdir(file_path)]
        final_file_list = file_list.copy()
        for item in file_list:
            if os.path.isdir(item):
                final_file_list += [os.path.join(item, x) for x in os.listdir(item)]
        file_list = [x for x in final_file_list.copy()]# if os.path.isfile(x)]
        file_df, self.results_paths = get_file_dataframe(file_list, self.start_path)
        if self.file_df is not None:
            self.file_df = pd.concat([self.file_df, file_df])
        else:
            self.file_df = file_df
        self.file_df = self.file_df.drop_duplicates()
        #if os.path.isdir(file_path):
        #    print("Loading {}.".format(file_path))
        #    self.start_path = file_path
        #    self.file_df, self.results_paths = get_file_dataframe(file_path)
        #    self.create_ui()
    
    def show_tree(self, tree_dataframe):
        self.clear()
        columns = [
                    "Path/Name",
                    "Area Description",
                    "Configuration", 
                    "Results.xml Generated?",
                    "Modification Time", 
                    "Owner"]

        self.setColumnCount(len(columns))
        self.setHeaderLabels(columns)
        self.setItemsExpandable(True)
        self.ancestor_dict = {}
        #Logic:
        #For each item, find the parent.
        for index, row in tree_dataframe.iterrows():
            parent_folder = row["Parent Folder"]
            has_results = row["Results"]
            file_path = row["Path"]

            parent_widget = self.get_parent_widget(parent_folder, file_path)
            
            values = [
                        row["Name"], 
                        row["Area Description"], 
                        row["Configuration"], 
                        row["Results"],
                        row["Modification Time"], 
                        row["Owner"]
                    ]

            item = QtGui.QTreeWidgetItem(parent_widget,values )
            item.setTextAlignment(1, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.expandItem(parent_widget)
        self.resizeColumnToContents(0)
        self.resizeColumnToContents(1)
        self.setSortingEnabled(True)
        self.expandAll()
    
    def get_parent_widget(self, parent_folder_path, file_path=None):
        if file_path is None:
            file_path = parent_folder_path
        parent_widget = self.ancestor_dict.get(parent_folder_path)

        if parent_widget is None:
            filtered_df = self.file_df[self.file_df["Path"] == file_path]
            result_count = filtered_df.shape[0]
            if result_count >0:
                area = list(filtered_df["Area Description"])[0]
                config = list(filtered_df["Configuration"])[0]
                mtime = list(filtered_df["Modification Time"])[0]
                owner = list(filtered_df["Owner"])[0]
                has_results = list(filtered_df["Results"])[0]
            else:
                area = "-"
                config = "-"
                mtime, owner = get_file_details(file_path)
                has_results = "-"

            values = [
                        os.path.basename(parent_folder_path),
                        area, config, has_results,
                        mtime,
                        owner
                        ]
            if parent_folder_path != self.start_path:
                grandparent_folder = os.path.split(parent_folder_path)[0]
                grandparent_widget = self.get_parent_widget(grandparent_folder)
                parent_widget = QtGui.QTreeWidgetItem(grandparent_widget, values)
            else:
                values[0] = parent_folder_path
                values[3] = "-"
                parent_widget = QtGui.QTreeWidgetItem(self, values)
            parent_widget.setTextAlignment(1, QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
            self.ancestor_dict[parent_folder_path] = parent_widget
            return parent_widget
        else:
           return parent_widget
        #I need to loop through the existing structure, make parents
        #and grandparents depending upon the structure.        

    def map_events(self):
        self.itemClicked.connect(self.changeSelection)
    
    def get_selected_item(self):
        i = self.selectedItems()
        item = i[0]
        path = []
        while item is not None:
            path.append(str(item.text(0)))
            item = item.parent()
        text = os.path.join(*reversed(path))
        return text
       
    def changeSelection(self):
        self.resizeColumnToContents(0)
        selected_item = self.get_selected_item()
        if os.path.isdir(selected_item):
            self.load_path(selected_item)
        self.show_tree(self.file_df)
        print(selected_item)

if __name__ == "__main__":
    app = QtGui.QApplication([])
    if os.name == "posix":
        base_path = os.path.normpath("/project")
    else:
        base_path = os.path.normpath(r"\\caeroot\project")
    start = os.path.join(
                        base_path, "las_india", 
                        "test", "cumfat_validation", 
                        "7.1", "reference_data", 
                        "mech_synthetic"
                        )
    start = os.path.join(
                        base_path,"nobackup",
                        "las_india","cluster","jobs")
    #start = os.path.abspath(os.path.join(os.getcwd(),"..",".."))
    test = FileExplorerWidget(start)
    test.show()
    test.setWindowTitle("File Explorer Widget Test")
    sys.exit(app.exec_())
