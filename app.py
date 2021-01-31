import os
import streamlit as st
import pandas as pd
from typing import List
import pydeck as pdk


def mission(dataset):
    parameters = [1, 2, 3, 4, 5, 6, 7]
    water_parameters = {1: "Total Water Column (m)",
                        2: "Temperature (c)",
                        3: "pH",
                        4: "ODO mg/L",
                        5: "Salinity (ppt)",
                        6: "Turbid+ NTU",
                        7: "BGA-PC cells/mL"}
    selected_parameters = [water_parameters.get(key) for key in
                           parameters]

    def selectDataframe(dataset: str, selected_parameters: List[str]):
        entire_ds = pd.read_csv(dataset,delimiter=';')  # read the entire dataset as a dataframe
        # print(entire_ds.columns) #to print the head of the dataframe
        mission_date=entire_ds.at[2,'Date']

        selected_parameters.insert(0, "Latitude")
        selected_parameters.insert(1, "Longitude")
        selected_parameters.insert(2, "Time hh:mm:ss")

        try:
            partial_ds = entire_ds[selected_parameters]
            print("The dataframe was successfully created!")
            print(partial_ds.columns)  # to print the head of the dataframe
            partial_ds = partial_ds.rename(columns={"Latitude": "lat", "Longitude": "lon"})
            return partial_ds,mission_date
        except ValueError:
            print("Oops!  Some selected water parameters do not exist in this dataset. Try again...")

    partial_ds = selectDataframe(dataset, selected_parameters)[0]  # calling function selectDataframe
    min_turb = partial_ds[["Turbid+ NTU"]].min()
    partial_ds[["Turbid+ NTU"]] = partial_ds[["Turbid+ NTU"]] - min_turb

    st.title('Biscayne Bay Missions')

    st.header("Data Collection - "+selectDataframe(dataset, selected_parameters)[1])

    st.subheader("Summary Table")
    options = st.multiselect(
        'Select Desired Parameters',
        ["Total Water Column (m)", "Temperature (c)", "pH", "ODO mg/L", "Salinity (ppt)", "Turbid+ NTU",
         "BGA-PC cells/mL"])

    # st.write('You selected:', options[0])

    partial_ds[['lat', 'lon'] + options]

    see_stats = st.checkbox('Click here for descriptive statistics')
    if see_stats:
        st.subheader("Descriptive Statistics Table")
        st.dataframe(partial_ds[["Total Water Column (m)", "Temperature (c)", "pH", "ODO mg/L", "Salinity (ppt)",
                                 "Turbid+ NTU", "BGA-PC cells/mL"]].describe())

    st.subheader("Map")
    # st.map(partial_ds[['lat','lon']])

    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/streets-v11',
        # map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
            latitude=25.91275783,
            longitude=-80.13782367,
            zoom=16,
            pitch=50,
        ),
        layers=[
            # pdk.Layer(
            #    'HexagonLayer',
            #    data=partial_ds[['lat','lon']],
            #    get_position='[lon, lat]',
            #    radius=10,
            #    elevation_scale=4,
            #    elevation_range=[0, 1000],
            #    pickable=True,
            #    extruded=True,
            # ),
            pdk.Layer(
                'ScatterplotLayer',
                data=partial_ds[['lat', 'lon']],
                get_position='[lon, lat]',
                get_color='[200, 30, 0, 160]',
                get_radius=1,
            ),
        ],
    ))

if __name__ == '__main__':
    path = "/Users/gregorymuradreis/Desktop/Log_Files_BBC_Jan_30_2021"
    lst=[]
    lst_path=[]
    for file in os.listdir(path):
        filename = os.fsdecode(file)
        if filename.endswith(".csv") or filename.endswith(".log"):
            print(os.path.join(path, filename))
            lst.append(filename)
            lst_path.append(os.path.join(path, filename))
        else:
            continue

    option = st.sidebar.selectbox("Select the Date/Location",
                                  tuple(lst))
    import csv

    temp_log = 'Logs2021/temp_log.csv'
    with open("/Users/gregorymuradreis/Desktop/Log_Files_BBC_Jan_30_2021/"+option, 'r') as logfile, open(temp_log, 'w') as csvfile:
        reader = csv.reader(logfile, delimiter=';')
        writer = csv.writer(csvfile, delimiter=';', )
        writer.writerows(reader)


    mission(temp_log)