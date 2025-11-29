Steps to execute the code

1. Install Python (if not installed)
Make sure Python 3.7 or later is installed.
bash:
python --version (to check python version)

2. Set Up a Virtual Environment
bash:
python -m venv commute_env
source commute_env/bin/activate     # On Windows use: commute_env\Scripts\activate

3. Install Required Libraries
Use pip to install the dependencies:
bash:
pip install streamlit pandas folium scikit-learn geopy streamlit-folium requests

4. Save the Code to a Python File
Create a file named sustainable_commute_planner.py and paste the code into it.

5. Run the Streamlit App
In your terminal or command prompt, navigate to the folder where your .py file is and run:
streamlit run sustainable_commute_planner.py

6. Use the Web Interface
After running the above command, your default web browser will open with a URL like:

http://localhost:8501

There, you can:

Enter your home and work locations (place names or landmarks)
Select your commute preferences (biking, walking, carpool)
Submit the form to see recommended commute options, environmental impact, and route map.