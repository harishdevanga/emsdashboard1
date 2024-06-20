import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')


st.set_page_config(page_title="EMS DASHBOARD!!!", page_icon=":bar_chart:",layout="wide")
st.title(":bar_chart: EMS DASHBOARD")
fl = st.file_uploader(":file_folder: Upload a file", type=(["csv", "txt", "xlsx","xls"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_excel(filename)
else:
    #os.chdir(r"D:\python\working_folder\emsdashboard")
    df = pd.read_excel("EMSdashboard2.xlsx")


col1, col2 = st.columns((2))
df["Build Date"] = pd.to_datetime(df["Build Date"])


#Getting min and max date
startDate = pd.to_datetime(df["Build Date"]).min()
endDate = pd.to_datetime(df["Build Date"]).max()


with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))




with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))




df = df[(df["Build Date"] >= date1) & (df["Build Date"] <= date2)].copy()


st.sidebar.header("Choose your filter: ")


# Create for Customer
customer = st.sidebar.multiselect("Pick your Customer", df["Customer"].unique())
if not customer:
    df2 = df.copy()
else:
    df2 = df[df["Customer"].isin(customer)]


# Create for Project
project = st.sidebar.multiselect("Pick your Project", df["Project"].unique())
if not project:
    df3 = df2.copy()
else:
    df3 = df2[df2["Project"].isin(project)]


# Create for Stage
#stage = st.sidebar.multiselect("Pick your Stage", df["Stage"].unique())
#if not stage:
#   df4 = df3.copy()
#else:
#    df4 = df3[df3["Stage"].isin(stage)]'''


# Create for Process
stage = st.sidebar.multiselect("Pick the Stage",df["Stage"].unique())


# Filter the data based on Customer, Project & Stage


if not customer and not project and not stage:
    filtered_df = df
elif not customer and not project:
    filtered_df = df[df["Stage"].isin(stage)]
elif not project and not stage:
    filtered_df = df[df["Customer"].isin(customer)]
elif project and stage:
    filtered_df = df3[df["Project"].isin(project) & df3["Stage"].isin(stage)]
elif customer and stage:
    filtered_df = df3[df["Customer"].isin(customer) & df3["Process"].isin(stage)]
elif customer and project:
    filtered_df = df3[df["Customer"].isin(customer) & df3["Project"].isin(project)]
elif stage:
    filtered_df = df3[df3["Stage"].isin(stage)]
else:
    filtered_df = df3[df3["Customer"].isin(customer) & df3["Project"].isin(project) & df3["Stage"].isin(stage)]


with col1:
    st.subheader("Project Wise Qty Tested")
    fig = px.bar(filtered_df, x = "Project", y = "FPY Qty Tested", text = ['{:,.2f}'.format(x)
                for x in filtered_df ["FPY Qty Tested"]], template="seaborn")
    st.plotly_chart(fig,use_container_width=True, height = 200)


with col2:
    st.subheader("Project wise FPY")
    fig = px.pie(filtered_df, values = "First Pass Yield", names = "Customer", hole = 0.5)
    fig.update_traces(text = filtered_df["Customer"], textposition = "outside")
    st.plotly_chart(fig,use_container_width=True)


cl1, cl2 = st.columns((2))
with cl1:
    with st.expander("Project_ViewData"):
        st.write(filtered_df.style.background_gradient(cmap="Blues"))
        csv = filtered_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Project.csv", mime = "text/csv",
                           help = 'Click here to download data as CSV file')


with cl2:
    with st.expander("Project FPY_ViewData"):
        st.write(filtered_df.style.background_gradient(cmap="Blues"))
        csv = filtered_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Project FPY.csv", mime = "text/csv",
                           help = 'Click here to download data as CSV file')
       
#Time series analysis
filtered_df["month_year"] = filtered_df["Build Date"].dt.to_period("M")
st.subheader("Time Series Analysis")




linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Defects"].sum()).reset_index()
fig2 = px.line(linechart, x = "month_year", y = "Defects", labels={"Defects":"Numbers"},height=500, width=1000, template="gridon")
st.plotly_chart(fig2,use_container_width=True)




with st.expander("View Data of TimeSeries:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data', data= csv, file_name= "TimeSeries.csv", mime='text/csv')


#Create a pieChart for Final Yield & Defects Count wise sales
chart1, chart2 = st.columns((2))
with chart1:
    st.subheader("Customer wise Final Yield")
    fig = px.pie(filtered_df, values= "Final Yield", names= "Customer", template= "plotly_dark")
    fig.update_traces(text = filtered_df["Customer"], textposition = "inside")
    st.plotly_chart(fig, use_container_width=True)


with chart2:
    st.subheader("Project wise Defects")
    fig = px.pie(filtered_df, values= "Defects", names= "Project", template= "plotly_dark")
    fig.update_traces(text = filtered_df["Project"], textposition = "inside")
    st.plotly_chart(fig, use_container_width=True)


# Create a tree based on Region, Category, Sub-Category
st.subheader("Hierarchical view of Defects using TreeMap")
fig3 = px.treemap(filtered_df, path= ["Customer","Project","Stage"], values="Defects",
                  hover_data=["Stage"], color="Process")
fig3.update_layout(width = 800, height = 650)
st.plotly_chart(fig3,use_container_width=True)
