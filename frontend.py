from flask import import Flask, request, render_template
import sys
from app import app

#application
app= Flask(__name__)
app.config.from_envvar('FlASK_SETTINGS', silent = True) #yolo config file goes here 




#comment
@app.route('/', methods=['POST'])
def get_data(argv): 
    sys.argv[1] #the html file
    if request.method =='POST':
       #do soemthing
        return str
    return render_template('layout.html')

f __name__ == '__main__':
    app.run(debug=True)
