#!/usr/env python3

def getColor(color_name):
    color_dict = {
                    "white": "#ffffff",
                    "blue": "#2196f3",
                    "red": "#f44336",
                    "light blue": "#03a9f4",
                    "green": "#4caf50",
                    "yellow": "#ffeb3b",
                    "orange": "#ff9800",
                    "grey": "#9e9e9e",
                    "black": "#000000",
                    "brown": "#795548",
                    "cyan": "#00bcd4",
                    "purple": "#9c27b0"
            }

    return color_dict.get(color_name.lower(), "#ffffff")
