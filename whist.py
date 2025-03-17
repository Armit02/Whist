from PyQt5.QtWidgets import *
from pathlib import Path
from PyQt5.QtGui import QFont, QIntValidator
from PyQt5.QtCore import Qt
import json
import sys
import numpy as np

placeholder_settings = {
    "Armit Family": {
        "rounds": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16],
        "card number": [1,2,3,4,5,6,7,7,7,7,6,5,4,3,2,1],
        "trumps": ["c","h","s","d","c","h","s","n","m","d","c","h","s","d","c","h"],
        "points": 5
    },
    "Armit Family 2": {
        "rounds": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16],
        "card number": [1,2,3,4,5,6,7,7,7,7,6,5,4,3,2,1],
        "trumps": ["c","h","s","d","c","h","s","n","m","d","c","h","s","d","c","h"],
        "points": 5
    }
}


class bootupWindow(QWidget):
    def getSettings(self):
        with open("whist_settings.json","r") as file:
            all_rules = json.load(file)
        return all_rules
    
    def __init__(self, app):
        super().__init__()
        self.setWindowTitle("Nomination Whist Scoresheet Wizard")
        self.mainLayout = QVBoxLayout()
        self.setMaximumSize(750,400)
        self.app = app
        
        # HEADER AND TITLE REGION
        title_widget = QWidget()
        title_container = QVBoxLayout()
        title_widget.setFixedSize(750,100)

        title_label = QLabel("Nomination Whist Interactive Scoresheet Setup",alignment=Qt.AlignmentFlag.AlignHCenter)
        title_label.setFont(QFont('monospace',16))

        subtitle_label = QLabel("Enter the Settings of your game to get started!",alignment=Qt.AlignmentFlag.AlignHCenter)
        subtitle_label.setFont(QFont('monospace',12))

        title_container.addWidget(title_label)
        title_container.addWidget(subtitle_label)
        title_container.setSpacing(0)

        title_widget.setLayout(title_container)
        self.mainLayout.addWidget(title_widget)

        # INPUT REGION
        input_container = QHBoxLayout()

        self.player_number_input = QLineEdit()
        self.player_number_input.setMaximumWidth(150)
        self.player_number_input.setPlaceholderText("Enter number of players here...")
        self.player_number_input.setValidator(QIntValidator(2,12))
        
        settings_container = QHBoxLayout()
        settings_container.addStretch()
        settings_container.addWidget(QLabel("Choose Settings Loutout: "))
        self.settings = QComboBox()
        self.all_rules = self.getSettings()
        self.settings.addItems(option for option in self.all_rules)
        settings_container.addWidget(self.settings)

        input_container.addWidget(self.player_number_input)
        input_container.addLayout(settings_container)
        settings_container.addStretch()

        self.proceed_button = QPushButton("Create Scoresheet")
        self.proceed_button.clicked.connect(self.createScoresheet)

        self.mainLayout.addLayout(input_container)
        self.mainLayout.addWidget(self.proceed_button)

        self.errorLabel = QLabel("")
        self.mainLayout.addWidget(self.errorLabel)
        self.setLayout(self.mainLayout)
    
    def createScoresheet(self):
        # try:
            print("Clicked!")
            try:
                num_players = int(self.player_number_input.text())
            except ValueError:
                pass
            print(f"Players: {num_players}, {type(num_players)}")
            ruleset = self.all_rules[self.settings.currentText()]
            print(ruleset)
            self.errorLabel.setText("")
            self.scoresheetWindow = mainWindow(ruleset, num_players)
            self.scoresheetWindow.show()
            self.close()
        # except ValueError:
        #     self.errorLabel.setText("Please ensure all information is filled out!")

class mainWindow(QMainWindow):
    def __init__(self, ruleset, num_players):
        super().__init__()
        self.num_players = num_players
        self.ruleset = ruleset
        self.init_ui()

    def getScore(self):
        row = 0
        col = 0
        col_region = 0
        # Rows mimick the table structure
        score_grid = np.zeros((len(self.ruleset['rounds']),2*self.num_players))
        for entry in self.inputs:
            next_entry = entry.text()
            # Switch empty for 0 
            if next_entry == '':
                # Set to 9 since you cannot feasibly achieve that score of tricks
                next_entry = 9
            score_grid[row,col] = next_entry
            if col == (1 + col_region):
                if row == len(self.ruleset['rounds'])-1:
                    col_region = col_region + 2
                    row = 0
                    col = col_region
                else:
                    col = col_region
                    row = row + 1
            else:
                col = col + 1 
        earned_vector = []
        row_start = 0
        for player in range(0,self.num_players*2,2):
            for row in score_grid:
                row = row[player:player+2]
                if 9 not in row:
                    if row[0] == row[1]:
                        if row[1] != 9:
                            score = self.ruleset['points'] + row[1]
                    else:
                        score = row[1]
                else:
                    score = 0
                earned_vector.append(score)
        print(earned_vector)
        total = 0
        calibration = -1
        for i in range(len(earned_vector)):
            if i > (len(self.ruleset['rounds'])+calibration):
                total = 0
                calibration = calibration + len(self.ruleset['rounds'])
            self.outputs[i].setText(str(earned_vector[i]))
            total = total + earned_vector[i]
            self.totals[i].setText(str(total))
            
                
    def init_ui(self):
        # Set up main page
        self.setWindowTitle("Nomination Whist Scoresheet")
        mainWidget = QWidget()
        mainLayout = QVBoxLayout()
        mainLayout.addStretch()
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)
        
        # HEADER AND TITLE REGION
        title_container_widget = QWidget()
        title_container = QVBoxLayout()

        title_label = QLabel("Nomination Whist Interactive Scoresheet",alignment=Qt.AlignmentFlag.AlignHCenter)
        title_label.setFont(QFont('monospace',16))
        title_container.addWidget(title_label)

        title_container_widget.setLayout(title_container)
        title_container_widget.setMaximumHeight(50)
        mainLayout.addWidget(title_container_widget)

        bodyWidget = QWidget()
        bodyLayout = QHBoxLayout()
        # Add Trumps Column
        self.inputs = []
        self.outputs = []
        self.totals = []
        for i in range(self.num_players):
            # Create a score widget
            scoreWidget = QWidget()
            scoreLayout = QGridLayout()
            # First column
            scoreLayout.addWidget(QLabel(f"Player: {i+1}",alignment=Qt.AlignmentFlag.AlignHCenter),0,0)
            # if i == 0:
            scoreLayout.addWidget(QLabel(f"|Round|"), 1, 0)
            for j in range(len(self.ruleset["rounds"])):
                scoreLayout.addWidget(QLabel(f"Cards {self.ruleset['card number'][j]}\nTrumps: {self.ruleset['trumps'][j]}"), j+2, 0)
            # Second Column
            scoreLayout.addWidget(QLabel("|Num Tricks|"), 1, 1)
            for j in range(len(self.ruleset['rounds'])):
                for k in range(4):
                    if k <= 1:
                        line = QLineEdit()
                        line.setValidator(QIntValidator(0,7))
                        scoreLayout.addWidget(line,j+2,k+1)
                        self.inputs.append(line)
                    else:
                        out = QLabel("")
                        scoreLayout.addWidget(out,j+2,k+1)
                        if k == 3:
                            self.totals.append(out)
                        else:
                            self.outputs.append(out)
            # Third Column
            scoreLayout.addWidget(QLabel("|Tricks taken|"), 1, 2)
            # Fourth Column 
            scoreLayout.addWidget(QLabel("|Round Score|"), 1, 3)
            # Fifth Column
            scoreLayout.addWidget(QLabel("|Total Score|"), 1, 4)
            scoreWidget.setLayout(scoreLayout)
            scoreWidget.setFixedHeight(700)
            bodyLayout.addWidget(scoreWidget)
        bodyWidget.setLayout(bodyLayout)
        bodyWidget.setMaximumHeight(750)
        mainLayout.addWidget(bodyWidget)
        test_button = QPushButton("Evaluate Scores")
        test_button.clicked.connect(self.getScore)
        mainLayout.addWidget(test_button)
        mainLayout.addStretch()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(Path('whistStyle.qss').read_text())
    window = bootupWindow(app)
    window.show()
    sys.exit(app.exec())