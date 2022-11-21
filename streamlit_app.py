import streamlit as st
import numpy as np
import pandas as pd
from typing import List
import pydeck as pdk
from PIL import Image
import matplotlib.pyplot as plt

def mission(dataset):
    def selectDataframe(dataset: str, selected_parameters: List[str]):
        entire_ds = pd.read_csv(dataset)  # read the entire dataset as a dataframe
        # print(entire_ds.columns) #to print the head of the dataframe

        selected_parameters.insert(0, "Latitude")
        selected_parameters.insert(1, "Longitude")
        selected_parameters.insert(2, "Time hh:mm:ss")

        try:
            partial_ds = entire_ds[selected_parameters]
            #print("The dataframe was successfully created!")
            #print(partial_ds.columns) #to print the head of the dataframe
            partial_ds=partial_ds.rename(columns={"Latitude": "lat", "Longitude": "lon"})
            return partial_ds, entire_ds
        except ValueError:
            print("Oops!  Some selected water parameters do not exist in this dataset. Try again...")


    parameters = [1,2,3,4]
    water_parameters = {1: "ODO mg/L",
                        2: "Temperature (c)",
                        3: "pH",
                        4: "Total Water Column (m)"}
                        # 5: "Salinity (ppt)",
                        # 6: "Turbid+ NTU",
                        # 7: "BGA-PC cells/mL"}
    selected_parameters = [water_parameters.get(key) for key in
                           parameters]
    # print("selected_parameters: ", selected_parameters)
    partial_ds, entire_ds = selectDataframe(dataset, selected_parameters)  # calling function selectDataframe
    # partial_ds = partial_ds_[partial_ds_["Salinity (ppt)"] > 10]
    # entire_ds = entire_ds_[entire_ds_["Salinity (ppt)"] > 10]


    st.subheader("Map")
    st.write("Hover over the markers to see more information.")
    zoom_lat = partial_ds['lat'].mean()
    zoom_long = partial_ds['lon'].mean()

    print("partial_ds: ", partial_ds.describe())
    st.pydeck_chart(pdk.Deck(
    #map_style https://docs.mapbox.com/api/maps/styles/
         map_style='mapbox://styles/mapbox/satellite-streets-v11',
         initial_view_state=pdk.ViewState(
             latitude=zoom_lat,
             longitude=zoom_long,
             zoom=18,
             pitch=50,
         ),
         layers=[
             pdk.Layer(
                 'ScatterplotLayer',
                 # data=partial_ds[['lat','lon']],
                 data=partial_ds,
                 get_position='[lon, lat]',
                 get_color='[26, 255, 0, 160]',
                 get_radius=0.25,
                 pickable=True, #to show tooltip
             ),
         ],
        tooltip={
            # "html": "Lat: {lat} <br/> Long:{lon}",
            # create 0s for the options when not selected
            "html": "Lat: {lat} <br/> Long:{lon} <br/> ODO(mg/L):{ODO mg/L} <br/>"
                    "Temp(C): {Temperature (c)} <br/> pH: {pH} <br/> TWC(m): {Total Water Column (m)} <br/>",
            "style": {
                "backgroundColor": "steelblue",
                "color": "white"
                }
            }
     ))

    st.header("Plots")

    def generate_plots(plot_par):
        x = entire_ds["Time hh:mm:ss"]
        y_column = partial_ds[plot_par]
        fig, ax = plt.subplots(figsize=(7, 3))
        plt.title(plot_par)
        ax.plot(x, y_column)
        ax.set_ylim(y_column.min(), y_column.max())
        ax.set_xlabel("Time")
        ax.set_ylabel(plot_par)
        st.pyplot(fig)

    def generate_plot_opt(plot_par):
        # st.line_chart(partial_ds[plot_par])
        import plotly.express as px
        course_fig = px.line(entire_ds, x="Time hh:mm:ss", y=plot_par,
                            title=plot_par)
        # course_fig.update_traces(marker_color='red')
        course_fig.update_layout(
            font=dict(
                size=20,
                color="RebeccaPurple"),
            title_font_color="orange",
            title_font_size=20
        )
        st.plotly_chart(course_fig, use_container_width=True)

    def generate_plot_natively(plot_par):
        # entire_ds["Time hh:mm:ss"]
        # partial_ds[plot_par]
        # entire_ds["Time hh:mm:ss"][0]
        # st.text(type(entire_ds["Time hh:mm:ss"][0]))
        df=pd.DataFrame({"Time": entire_ds["Time hh:mm:ss"],
                      plot_par: partial_ds[plot_par]})
        # df=df.set_index("time")
        # st.line_chart(df)
        import altair as alt
        chart = alt.Chart(df).mark_line().encode(
            x=alt.X('Time', axis=alt.Axis(labelOverlap="greedy",grid=False)),
            y=alt.Y(plot_par)
        )
        st.altair_chart(chart, use_container_width=True)

        # st.altair_chart(pd.DataFrame({"index":entire_ds["Time hh:mm:ss"],
        #                               plot_par:partial_ds[plot_par]}))

    plot_parameter = st.selectbox("Pick one", ["ODO mg/L","Temperature (c)", "pH", "Total Water Column (m)"])
    st.markdown("**Dataset collected on:**")
    entire_ds["Date"][0]
    if plot_parameter:
        with st.spinner('⌛⌛ Generating plot for desired parameter... '):
            #generate_plots(plot_parameter)
            generate_plot_opt(plot_parameter)
            st.success('Plot was successful!')



    st.subheader("Summary Table")
    options = st.multiselect(
        'Select Desired Parameters',
        ["ODO mg/L","Temperature (c)", "pH", "Total Water Column (m)"])

    # st.write('You selected:', options[0])

    partial_ds[['lat', 'lon'] + options]

    # if the column does not exist, create one row with 0
    n_options = list(set(selected_parameters) - set(options))
    # print("n_options: ", n_options)

    # min_turb = partial_ds[["Turbid+ NTU"]].min()
    # partial_ds[["Turbid+ NTU"]]=partial_ds[["Turbid+ NTU"]]-min_turb

    st.header("Descriptive Statistics")
    st.dataframe(partial_ds[["Total Water Column (m)", "Temperature (c)", "pH", "ODO mg/L"]].describe())

    # st.subheader("Water Quality Parameters' Definitions")
    # definitions = st.checkbox("Click here for definitions on water quality parameters")
    # if definitions:
    #     st.json({"Total Water Column (m)": "measure of depth from the surface to the bottom of the ocean.",
    #              "Temperature (ºC)": "physical property that expresses how hot or cold (average thermal energy) the water is.",
    #              "pH": "measure of how acidic or basic the water is, ranging from 0 to 14, with 7 being neutral. < 7 indicates acidity, whereas > 7 indicates a base.",
    #              "ODO (mg/L)": "concentration of molecular oxygen (02) dissolved in water."
    #              })

    st.header("Images")
    photo1, photo2, photo3 = st.columns(3)
    with photo1:
        image1 = Image.open('3_robot_1.jpg')
        st.image(image1, caption="YSI Ecomapper, Clearpath Heron, and SeaRobotics autonomous vehicles in Biscaybe Bay, FL.")
    with photo2:
        image2 = Image.open('3_robot_2.jpg')
        st.image(image2, caption="YSI Ecomapper, Clearpath Heron, and SeaRobotics autonomous vehicles in Biscaybe Bay, FL.")
        # st.image(image3, caption="YSI Ecomapper, Clearpath Heron, and SeaRobotics autonomous vehicles in Biscaybe Bay, FL.")
    with photo3:
        image4 = Image.open('3_robot_4.png')
        st.image(image4, caption="Network of autonomous marine vehicles, buoys, and aerial drones for real-time environmental monitoring.")

    st.header("Media")
    # video_file = open('Gregory_Mongabay2.mp4', 'rb')
    # video_bytes = video_file.read()
    # st.video(video_bytes)
    media1, media2 = st.columns(2)
    with media1:
        st.markdown("**Mongabay Series: Oceans - \"Building back Miami\'s Biscayne Bay: Do natural solutions hold hope?\" by Marlowe Starling on July 14, 2021**")
        st.video("https://www.youtube.com/watch?v=j82pP18wFe8&ab_channel=Mongabay")
        st.write("Source: [link](https://news.mongabay.com/2021/07/building-back-miamis-biscayne-bay-do-natural-solutions-hold-hope/)")
    with media2:
        st.markdown("**Local10 News - \"Saving Biscayne Bay: Researchers worry about risk of another fish kill this summer\" by Louis Aguirre on April 2, 2021**")
        st.video("https://www.youtube.com/watch?v=qOFmkouoJXM&ab_channel=GregoryMuradReis")
        st.write("Source: [link](https://www.local10.com/news/local/2021/04/02/saving-biscayne-bay-researchers-worry-about-risk-of-another-fish-kill-this-summer/)")

if __name__ == '__main__':
    st.set_page_config(
        page_title="FIU Marine Robotics",
        page_icon="🐠",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://crestcache.fiu.edu/',
            'Report a bug': "https://www.gregoryreis.com",
            'About': "# This is a header. This is an *extremely* cool app!"}
    )
    # DATA BY LOCATION
    # |-> BBC
    # |--> Data by date
    # |---> 1 - September 18th 2020
    bbc_sep_2020_1 = "Logs/BBC/1 - Biscayne Bay - September 18th 2020/20200918_105724_Mission1_09_11_IVER2-218.csv"
    bbc_sep_2020_2 = "Logs/BBC/1 - Biscayne Bay - September 18th 2020/20200918_105852_TrianglePathMission_IVER2-218.csv"
    bbc_sep_2020_3 = "Logs/BBC/1 - Biscayne Bay - September 18th 2020/20200918_110002_TrianglePathMission_IVER2-218.csv"
    bbc_sep_2020_4 = "Logs/BBC/1 - Biscayne Bay - September 18th 2020/20200918_115659_PleaseWork_IVER2-218.csv"
    bbc_sep_2020_5 = "Logs/BBC/1 - Biscayne Bay - September 18th 2020/20200918_120605_PleaseWorkSRP_IVER2-218.csv"
    bbc_sep_2020_6 = "Logs/BBC/1 - Biscayne Bay - September 18th 2020/ManualLog_11_05_09_92.csv"
    bbc_sep_2020_7 = "Logs/BBC/1 - Biscayne Bay - September 18th 2020/ManualLog_12_19_47_14.csv"
    # |---> 2 - October 4th 2020
    bbc_oct_2020_1 = "Logs/BBC/2 - Biscayne Bay - October 4th 2020/20201004_171844_TestForLittleRiver_IVER2-218.csv"
    bbc_oct_2020_2 = "Logs/BBC/2 - Biscayne Bay - October 4th 2020/20201004_180324_LittleRiverOct4_IVER2-218.csv"
    bbc_oct_2020_3 = "Logs/BBC/2 - Biscayne Bay - October 4th 2020/ManualLog_17_00_45_64.csv"
    # |---> 3 - January 30th 2021
    bbc_jan_2021_1 = "Logs/BBC/3 - Biscayne Bay - January 30th 2021/20210130_124101_jan302021_bbc_IVER2-218.csv"
    bbc_jan_2021_2 = "Logs/BBC/3 - Biscayne Bay - January 30th 2021/20210130_130339_jan302021_bbc_IVER2-218.csv"
    bbc_jan_2021_3 = "Logs/BBC/3 - Biscayne Bay - January 30th 2021/20210130_131335_jan302021_bbc_IVER2-218.csv"
    bbc_jan_2021_4 = "Logs/BBC/3 - Biscayne Bay - January 30th 2021/20210130_135713_jan302021_bbc_IVER2-218.csv"
    bbc_jan_2021_5 = "Logs/BBC/3 - Biscayne Bay - January 30th 2021/20210130_140634_jan302021_bbc_IVER2-218.csv"
    bbc_jan_2021_6 = "Logs/BBC/3 - Biscayne Bay - January 30th 2021/20210130_143547_jan302021_bbc_IVER2-218.csv"
    # |---> 4 - February 13th 2021
    bbc_feb_2021_1 = "Logs/BBC/4 - Biscayne Bay - February 13th 2021/20210213_150135_feb132021_bbc_IVER2-218.csv"
    bbc_feb_2021_2 = "Logs/BBC/4 - Biscayne Bay - February 13th 2021/20210213_155452_feb132021_b_bbc_IVER2-218.csv"
    # |---> 5 - March 16th 2021
    bbc_mar_2021_1 = "Logs/BBC/5 - Biscayne Bay - March 16th 2021/20210316_112824_onthespot_mar16_IVER2-218.csv"
    # |---> 6 - June 9th 2021
    bbc_jun_2021_1 = "Logs/BBC/6 - Biscayne Bay - June 9th 2021/20210609_105413_mongabay2_IVER2-218.csv"
    bbc_jun_2021_2 = "Logs/BBC/6 - Biscayne Bay - June 9th 2021/20210609_110304_mongabay2_IVER2-218.csv"
    bbc_jun_2021_3 = "Logs/BBC/6 - Biscayne Bay - June 9th 2021/20210609_112348_mongabay_IVER2-218.csv"
    # |---> 7 - September 2nd 2021
    bbc_sep_2021_1 = "Logs/BBC/7 - Biscayne Bay - September 2nd 2021/sep2_2021_bbc_mission_1.csv"
    bbc_sep_2021_2 = "Logs/BBC/7 - Biscayne Bay - September 2nd 2021/sep2_2021_bbc_mission_2.csv"
    bbc_sep_2021_test = "Logs/BBC/7 - Biscayne Bay - September 2nd 2021/sep2_2021_bbc_test.csv"
    # |---> 8 - October 21st 2021
    bbc_oct_2021_1 = "Logs/BBC/8 - Biscayne Bay - October 21st 2021/20211021_dataset1.csv"
    bbc_oct_2021_2 = "Logs/BBC/8 - Biscayne Bay - October 21st 2021/20211021_dataset2.csv"
    bbc_oct_2021_3 = "Logs/BBC/8 - Biscayne Bay - October 21st 2021/20211021_dataset3.csv"
    # |---> 9 - December 16th 2021
    bbc_dec_2021 = "Logs/BBC/9 - Biscayne Bay - December 16th 2021/20211216_dataset.csv"
    # |---> 10 - February 4th 2022
    bbc_feb_2022 = "Logs/BBC/10 - Biscayne Bay - February 4th 2022/20220204_dataset.csv"
    # |---> 11 - August 28th 2022
    bbc_aug_2022_1 = "Logs/BBC/11 - Biscayne Bay - August 28th 2022/08-28-22-mission1.csv"
    bbc_aug_2022_2 = "Logs/BBC/11 - Biscayne Bay - August 28th 2022/08-28-22-mission2.csv"
    bbc_aug_2022_3 = "Logs/BBC/11 - Biscayne Bay - August 28th 2022/08-28-22-mission3.csv"
    # |---> 12 - November 16th 2022
    bbc_nov_2022_1 = "Logs/BBC/12 - Biscayne Bay - November 16th 2022/11-16-22-mission1.csv"
    bbc_nov_2022_2 = "Logs/BBC/12 - Biscayne Bay - November 16th 2022/11-16-22-mission2.csv"

    # |-> LITTLE RIVER
    # |--> Data by date
    # |---> October 2020
    lr_oct_2020_1 = "Logs/LittleRiver/ManualLog_17_00_45_64.csv" #oct3
    lr_oct_2020_2 = "Logs/LittleRiver/20201004_171844_TestForLittleRiver_IVER2-218.csv"
    lr_oct_2020_3 = "Logs/LittleRiver/20201004_180324_LittleRiverOct4_IVER2-218.csv"

    st.title("FIU's Interdisciplinary Initiative for Autonomous Systems in Environmental Research")
    st.header("Saving Biscayne Bay ")

    st.write("This project aims at developing algorithms to effectively and efficiently collect water data using "
             "autonomous underwater and surface robots, and then analyze and develop visualization tools for the data collected in"
             " Biscayne Bay, FL. This effort is motivated by the environmental issues in the bay area in the last months."
             "\nPlease select a mission in the top left menu to visualize the dataset.")
    st.sidebar.header("Datasets")
    loc_option = st.sidebar.selectbox("Select a Location:",
                                      ("Biscayne Bay", "Little River"))

    if loc_option == "Biscayne Bay":
        ds_data = st.sidebar.selectbox("Select a Date:", options=["November 16th 2022","August 28th 2022","February 4th 2022",
                                                                  "December 16th 2021","October 21st 2021",
                                                                  "September 2nd 2021", "June 9th 2021",
                                                                  "March 16th 2021", "February 13th 2021",
                                                                  "January 30th 2021", "October 4th 2020",
                                                                  "September 18th 2020"])
        if ds_data:
            if ds_data == "September 18th 2020":
                ds_option = st.sidebar.selectbox("Select a Dataset:",options=["sep_2020_1", "sep_2020_2", "sep_2020_3",
                                                                     "sep_2020_4", "sep_2020_5","sep_2020_6",
                                                                     "sep_2020_7"])
            elif ds_data == "October 4th 2020":
                ds_option = st.sidebar.selectbox("Select a Dataset:", options=["oct_2020_1", "oct_2020_2", "oct_2020_3"])
            elif ds_data == "January 30th 2021":
                ds_option = st.sidebar.selectbox("Select a Dataset:", options=["jan_2021_1", "jan_2021_2", "jan_2021_3",
                                                                      "jan_2021_4", "jan_2021_5", "jan_2021_6"])
            elif ds_data == "February 13th 2021":
                ds_option = st.sidebar.selectbox("Select a Dataset:", options=["feb_2021_1", "feb_2021_2"])
            elif ds_data == "March 16th 2021":
                ds_option = st.sidebar.selectbox("Select a Dataset:", options=["mar_2021_1"])
            elif ds_data == "June 9th 2021":
                ds_option = st.sidebar.selectbox("Select a Dataset:", options=["jun_2021_1", "jun_2021_2", "jun_2021_3"])
            elif ds_data == "September 2nd 2021":
                ds_option = st.sidebar.selectbox("Select a Dataset:", options=["sep_2021_1", "sep_2021_2", "sep_2021_test"])
            elif ds_data == "October 21st 2021":
                ds_option = st.sidebar.selectbox("Select a Dataset:", options=["oct_2021_1","oct_2021_2","oct_2021_3"])
            elif ds_data == "December 16th 2021":
                ds_option = st.sidebar.selectbox("Select a Dataset:", options=["dec_2021"])
            elif ds_data == "February 4th 2022":
                ds_option = st.sidebar.selectbox("Select a Dataset:", options=["feb_2022"])
            elif ds_data == "August 28th 2022":
                ds_option = st.sidebar.selectbox("Select a Dataset:", options=["aug_2022_3","aug_2022_2","aug_2022_1"])
            elif ds_data == "November 16th 2022":
                ds_option = st.sidebar.selectbox("Select a Dataset:", options=["bbc_nov_2022_1","bbc_nov_2022_2"])
            if ds_option:
                # get the value of a variable given its name in a string
                var = locals()['bbc_' + ds_option]
                mission(var)
    elif loc_option == "Little River":
        ds_data = st.sidebar.selectbox("Select a Date:", options=["October 4th 2020", "October 3rd 2020"])
        if ds_data:
            if ds_data == "October 3rd 2020":
                ds_option = st.sidebar.selectbox("Select a Dataset:", options=["oct_2020_1"])
            elif ds_data == "October 4th 2020":
                ds_option = st.sidebar.selectbox("Select a Dataset:", options=["oct_2020_3", "oct_2020_2"])
            if ds_option:
                # get the value of a variable given its name in a string
                var = locals()['lr_' + ds_option]
                mission(var)
    st.sidebar.subheader("Contact Us")
    st.sidebar.markdown("**Gregory Murad Reis, PhD**")
    st.sidebar.write("Website: [link](https://www.gregoryreis.com)")
    st.sidebar.write("+1(305)348-7852")
    # mission(ds_option, lr_lat, lr_long)



