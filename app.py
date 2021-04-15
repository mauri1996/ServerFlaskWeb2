# -*- coding: utf-8 -*-
"""
Created on Wed Apr 14 21:21:11 2021

@author: Mauricio C
"""

from flask import Flask

app= Flask(__name__)

@app.route('/')
def index():
    return "<h1>Hola papu</h1>"


if __name__ == '__main__':
    app.run(port=5000)
