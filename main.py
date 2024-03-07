import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import os
import time
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QListWidget, QLineEdit, QAbstractItemView, QCheckBox, QTableWidgetItem, QTableWidget, QHBoxLayout, QLabel
from PySide6.QtCore import QSettings, Qt, QObject, Signal
import sys
sys.argv += ['-platform', 'windows:darkmode=2']

# Make directory for saved data if it doesn't exist
if not os.path.exists("Saved_Data"):
    os.mkdir("Saved_Data")

def plot_data(files, subplot_mode, save_images, save_html, show_plots, scaling_high, titles=[]):
  path = "D:\\GCDC\\"
  subplot_titles = []
  subplots = []

  for i, f in enumerate(files):
    # Read the csv file into a pandas DataFrame.
    df = pd.read_csv(f, skiprows=6, skipfooter=1, names=['Time', 'X', 'Y', 'Z'], engine='python')
    
    if scaling_high:
      scaling = 256000
    else:
      scaling = 64000
    
    # Convert the values to G's
    df['X'] = df['X'] / scaling
    df['Y'] = df['Y'] / scaling
    df['Z'] = df['Z'] / scaling

    # Adjust the data to be centered around 0
    df['X'] = df['X'] - df['X'].mean()
    df['Y'] = df['Y'] - df['Y'].mean()
    df['Z'] = df['Z'] - df['Z'].mean()

    # elapsed since EPOCH in float
    timestamp = os.path.getmtime(f)
    
    # Converting the time in seconds to a timestamp
    timestamp = time.ctime(timestamp)

    if subplot_mode:
      if i > 0:
        subplots.append((go.Scatter(x=df['Time'], y=df['X'], name='X', line=dict(color='#636EFA'), legendgroup='X', mode='lines', showlegend=False, hovertemplate="Time=%{x}<br>Force=%{y}"), go.Scatter(x=df['Time'], y=df['Y'], name='Y', mode='lines', showlegend=False, line=dict(color='#EF553B'), legendgroup='Y', hovertemplate="Time=%{x}<br>Force=%{y}"), go.Scatter(x=df['Time'], y=df['Z'], name='Z', mode='lines', showlegend=False, line=dict(color='#00CC96'), legendgroup='Z', hovertemplate="Time=%{x}<br>Force=%{y}")))
      else:
        subplots.append((go.Scatter(x=df['Time'], y=df['X'], name='X', line=dict(color='#636EFA'), legendgroup='X', mode='lines', hovertemplate="Time=%{x}<br>Force=%{y}"), go.Scatter(x=df['Time'], y=df['Y'], name='Y', mode='lines', line=dict(color='#EF553B'), legendgroup='Y', hovertemplate="Time=%{x}<br>Force=%{y}"), go.Scatter(x=df['Time'], y=df['Z'], name='Z', mode='lines', line=dict(color='#00CC96'), legendgroup='Z', hovertemplate="Time=%{x}<br>Force=%{y}")))
      if f.replace(path, '') in titles:
        subplot_titles.append(f"{titles[f.replace(path, '')]} - {timestamp}")
      else:
        subplot_titles.append(f"{f.replace(path, '')} - {timestamp}")
    
    if plot_data:
      fig = go.Figure()
      fig.add_trace(go.Scatter(x=df['Time'], y=df['X'], name='X', mode='lines', line=dict(color='#636EFA'), hovertemplate="Time=%{x}<br>Force=%{y}"))
      fig.add_trace(go.Scatter(x=df['Time'], y=df['Y'], name='Y', mode='lines', line=dict(color='#EF553B'), hovertemplate="Time=%{x}<br>Force=%{y}"))
      fig.add_trace(go.Scatter(x=df['Time'], y=df['Z'], name='Z', mode='lines', line=dict(color='#00CC96'), hovertemplate="Time=%{x}<br>Force=%{y}"))

      fig.add_hline(y=.15, row=i+1, col=1)
      fig.add_hline(y=-.15, row=i+1, col=1)

      fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1))
      
      fig.update_xaxes(title_text="Time (s)")
      fig.update_yaxes(title_text="Force (G)", range=[-.3, .3])

      if f.replace(path, '') in titles:
        fig.update_layout(title=f"{titles[f.replace(path, '')]} - {timestamp}")
      else:
        fig.update_layout(title=f"{f.replace(path, '')} - {timestamp}")
      
      fig.update_legends()

      if save_images:
        fig.write_image(f"Saved_Data/{titles[f.replace(path, '')]}.png", width=1920, height=1080)
      if save_html:
        fig.write_html(f"Saved_Data/{titles[f.replace(path, '')]}.html")
      if show_plots:
        fig.show()

  if subplot_mode:
    subplot_fig = make_subplots(rows=len(files), cols=1, subplot_titles=subplot_titles, vertical_spacing = 0.05)

    for i, fig in enumerate(subplots):
      for trace in fig:
        subplot_fig.append_trace(trace, row=i+1, col=1)
      subplot_fig.add_hline(y=.15, row=i+1, col=1)
      subplot_fig.add_hline(y=-.15, row=i+1, col=1)
      subplot_fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1))
      
    subplot_fig.update_yaxes(range=[-.16, .16])
    
    if save_images:
      subplot_fig.write_image(f"Saved_Data/subplot.png", width=1920, height=1080)
    if save_html:
      subplot_fig.write_html(f"Saved_Data/subplot.html")
    if show_plots:
      subplot_fig.show()

class SettingsManager(QObject):
  settings_loaded = Signal()

  def load_settings(self, main_window=None):
    try:
      main_window.titles = main_window.settings.value("titles")
      main_window.path = main_window.settings.value("path", "D:\\GCDC\\")
      main_window.path_input.setText(main_window.path)
      self.settings_loaded.emit()
    except:
      pass


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stop Data Analysis")

        self.titles = {}
        
        self.path = ''
        self.settings = QSettings("PM Development", "Stop Data Analysis")

        self.setGeometry(100, 100, 400, 900)

        self.button_layout = QHBoxLayout()
        self.path_layout = QHBoxLayout()

        self.selection_list = QListWidget()
        self.selection_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.add_button = QPushButton("Add To List")
        self.add_button.clicked.connect(self.add_to_list)
        self.path_input = QLineEdit()
        self.path_label = QLabel("Path")
        self.remove_button = QPushButton("Remove From List")
        self.remove_button.clicked.connect(self.remove_from_list)
        self.plot_data_button = QPushButton("Plot Data")
        self.plot_data_button.clicked.connect(self.plot_data)
        self.get_files_button = QPushButton("Get Files")
        self.file_table = QTableWidget()
        self.file_table.setColumnCount(2)
        self.file_table.setHorizontalHeaderLabels(["File", "Title"])

        self.file_table.horizontalHeader().setStretchLastSection(True)

        self.plot_checkbox = QCheckBox("Plot Separately")
        self.plot_checkbox.setChecked(True)
        self.html_checkbox = QCheckBox("Save HTML")
        self.image_checkbox = QCheckBox("Save Images")
        self.subplot_checkbox = QCheckBox("Plot All Together")

        self.layout = QVBoxLayout()
        self.button_layout.addWidget(self.add_button)
        self.button_layout.addWidget(self.remove_button)

        self.path_layout.addWidget(self.path_label)
        self.path_layout.addWidget(self.path_input)

        self.layout.addWidget(self.file_table)
        self.layout.addLayout(self.path_layout)
        self.layout.addWidget(self.get_files_button)
        self.layout.addLayout(self.button_layout)
        self.layout.addWidget(self.selection_list)
        self.layout.addWidget(self.plot_checkbox)
        self.layout.addWidget(self.html_checkbox)
        self.layout.addWidget(self.image_checkbox)
        self.layout.addWidget(self.subplot_checkbox)
        self.layout.addWidget(self.plot_data_button)

        self.get_files_button.clicked.connect(self.get_files)
        self.widget = QWidget()
        self.setCentralWidget(self.widget)
        self.widget.setLayout(self.layout)
        self.csv_files = []
        self.settings_manager = SettingsManager()
        self.settings_manager.settings_loaded.connect(self.get_files)
        self.settings_manager.load_settings(self)


    def add_to_list(self):
      selection = self.file_table.selectionModel().selectedRows()
      self.selection_list.clear()

      files = []

      for index in selection:
        file = self.file_table.item(index.row(), 0).text()
        files.append(file)

      self.selection_list.addItems(files)
      

    def save_titles(self):
      titles_ = {}
      for row in range(self.file_table.rowCount()):
        file = self.file_table.item(row, 0).text()
        title = self.file_table.item(row, 1).text()
        titles_[file] = title
        self.titles = titles_

      self.settings.setValue("titles", self.titles)


    def remove_from_list(self):
        selection = self.selection_list.selectedItems()
        for item in selection:
            self.selection_list.takeItem(self.selection_list.row(item))

      
    def plot_data(self):
        plot = self.plot_checkbox.isChecked()
        html = self.html_checkbox.isChecked()
        image = self.image_checkbox.isChecked()
        subplot = self.subplot_checkbox.isChecked()

        selected_files = [f"{self.path_input.text()}{self.selection_list.item(i).text()}" for i in range(self.selection_list.count())]

        self.save_titles()

        # Process the file prompt input
        plot_data(selected_files, subplot, image, html, plot, True, self.titles)


    def get_files(self):
      self.csv_files = []
      try:
        for file in os.listdir(self.path_input.text()):
          if file.endswith(".csv") or file.endswith(".CSV"):
            self.csv_files.append(file)

        self.file_table.clear()

        row_count = 0

        for file in self.csv_files:
          self.file_table.insertRow(row_count)
          self.file_table.setItem(row_count, 0, QTableWidgetItem(file))
          if file in self.titles:
            self.file_table.setItem(row_count, 1, QTableWidgetItem(self.titles[file].replace(self.path_input.text(), '')))
          else:
            self.file_table.setItem(row_count, 1, QTableWidgetItem(file))
        
        self.file_table.horizontalHeader().setStretchLastSection(True)
        self.file_table.resizeColumnsToContents()
        for row in range(self.file_table.rowCount()):
          item = self.file_table.item(row, 1)
          item.setFlags(item.flags() | Qt.ItemIsEditable)
        
        self.file_table.setHorizontalHeaderLabels(["File", "Title"])
        
        self.settings.setValue("path", self.path_input.text())
      except:
        print("Error getting files")

if __name__ == "__main__":
  app = QApplication(sys.argv)
  app.setStyle('Fusion')
  window = MainWindow()
  window.show()
  app.exec()

