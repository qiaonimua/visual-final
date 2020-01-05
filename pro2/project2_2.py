import json
import os
import time
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from pyecharts import options as opts
from pyecharts.charts import Bar, Grid, Line, Scatter, Geo, Map, Timeline, Page
from pyecharts.faker import Collector, Faker
from pyecharts.globals import ChartType
from flask import Flask, render_template, request


def read_data1():
    """
    read data
    :return: 
    """
    df = pd.read_csv("education_level.csv")
    ages = list(df.age.unique())

    # ages = ["15 - 19", "20 - 24"]

    def second(ele):
        return eval(ele.split("-")[0])

    ages.sort(key=second)

    total_data_male = []
    total_data_female = []
    for index, age in enumerate(ages):
        total_data_male.append([age])
        total_data_female.append([age])
        data_male = {}
        data_female = {}
        male_country = []
        female_country = []
        for i in range(len(df)):
            country = df.area.loc[i]
            # age = df.age.loc[i]
            education = df.educational_attainment.loc[i]
            gender = df.sex.loc[i]
            value = df.value.loc[i]
            if df.age.loc[i] == age:
                if gender == "male":
                    if country not in male_country:
                        data_male[country] = [0, 0, 0]
                        male_country.append(country)
                    if "first" in education:
                        data_male[country][0] = value
                    elif "second" in education:
                        data_male[country][1] = value
                    elif "third" in education:
                        data_male[country][2] = value
                else:
                    if country not in female_country:
                        data_female[country] = [0, 0, 0]
                        female_country.append(country)
                    if "first" in education:
                        data_female[country][0] = value
                    elif "second" in education:
                        data_female[country][1] = value
                    elif "third" in education:
                        data_female[country][2] = value
        total_data_male[index].append(data_male)
        total_data_female[index].append(data_female)
    return ages, total_data_male, total_data_female


def read_data2():
    """
    read data
    :return:
    """
    df = pd.read_csv("home_style.csv")
    df.fillna(0, inplace=True)
    types = list(df["type_of_household"].unique())
    countries = list(df["country"].unique())
    data_male = {}
    data_female = {}
    country_record = []
    for i in range(len(df)):
        country = df.country.loc[i]
        type_name = df.type_of_household[i]
        gender = df.sex.loc[i]
        index = types.index(type_name)
        if country not in country_record:
            country_record.append(country)
            data_male[country] = [0 for j in range(len(types))]
            data_female[country] = [0 for j in range(len(types))]
        if gender == "male":
            data_male[country][index] += 1
        else:
            data_female[country][index] += 1
    return types, data_male, data_female


def read_data3():
    """
    read data
    :return:
    """
    df = pd.read_csv("existence_of_laws_on_domestic_violence_data.csv")
    data = {}
    names = list(df["Measure Name"].unique())
    for name in names:
        data[name] = []
    for i in range(len(df)):
        name = df["Measure Name"].loc[i]
        data[name].append([df["Country"].loc[i], 1 if df["Measure Value"].loc[i] == "Yes" else 0])
    return names, data


def read_data4():
    df1 = pd.read_csv("48.csv")
    df2 = pd.read_csv("49.csv")
    countries1 = list(df1.Country)
    countries2 = list(df2.Country)
    values1 = list(df1.Value)
    values2 = list(df2.Value)
    return countries1, countries2, values1, values2


def bar_stack0(data, info) -> Bar:
    """堆叠数据，绘制task1第一部分"""
    new_data = [[], [], []]
    for key in data.keys():
        for i in range(3):
            new_data[i].append(data[key][i])
    c = (
        Bar(init_opts=opts.InitOpts(page_title="Luwei"))
            .add_xaxis(list(data.keys()))
            .add_yaxis("First level", new_data[0], stack="stack1")
            .add_yaxis("Second level", new_data[1], stack="stack1")
            .add_yaxis("Third level", new_data[2], stack="stack1")
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(title_opts=opts.TitleOpts(title=info),
                             xaxis_opts=opts.AxisOpts(type_="category", name="Country",
                                                      axislabel_opts=opts.LabelOpts(font_weight="bold", rotate=30,
                                                                                    font_size=12, margin=0,
                                                                                    interval=0)))

    )
    return c


def bar_gdp(data, index, info):
    """柱状图,绘制task1第二部分"""
    x_data = list(data.keys())
    y_data = []
    for i in x_data:
        y_data.append(data[i][index])
    c = (
        Bar(init_opts=opts.InitOpts(width="1800px", page_title="luwei"))
            .add_xaxis(x_data)
            .add_yaxis("home_style", y_data, category_gap=0.3, color="#675bba")
            .set_global_opts(title_opts=opts.TitleOpts(title=info),
                             xaxis_opts=opts.AxisOpts(type_="category",
                                                      axislabel_opts=opts.LabelOpts(rotate=30, interval=2, font_size=10,
                                                                                    font_weight="bold")),
                             toolbox_opts=opts.ToolboxOpts(), )
    )
    return c


def map_violence(data):
    """绘制task2第一部分"""
    name1, name2 = [], []
    for elem in data:
        if elem[1] == 1:
            name1.append(elem[0])
        else:
            name2.append(elem[0])
    value1 = [1 for i in range(len(name1))]
    value2 = [1 for i in range(len(name2))]
    c1 = (
        Map(init_opts=opts.InitOpts(page_title="Luwei"))

            .add("Violence Data(Yes)", [list(z) for z in zip(name1, value1)], "world", is_map_symbol_show=False)
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False, font_weight="bold", font_size=20))
            .set_global_opts(
            legend_opts=opts.LegendOpts(pos_right=True, pos_top=True),
            title_opts=opts.TitleOpts(title="laws on domestic violence data"),
            visualmap_opts=opts.VisualMapOpts(max_=1),
            # visualmap_opts=opts.VisualMapOpts(),
            toolbox_opts=opts.ToolboxOpts(),

        )
    )
    c2 = (
        Map(init_opts=opts.InitOpts(page_title="Luwei"))
            .add("Violence Data(No)", [list(z) for z in zip(name2, value2)], "world", is_map_symbol_show=False)
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False, font_weight="bold", font_size=20))
            .set_global_opts(
            legend_opts=opts.LegendOpts(pos_right=True, pos_top=True),
            title_opts=opts.TitleOpts(title="laws on domestic violence data"),
            # visualmap_opts=opts.VisualMapOpts(max_=1),
            visualmap_opts=opts.VisualMapOpts(),
            toolbox_opts=opts.ToolboxOpts(),

        )
    )
    return c1, c2


def map_value(data, info):
    """在地图上绘制value值"""
    new_data = list(zip(data[0], data[1]))
    print(new_data)
    c = (
        Map(init_opts=opts.InitOpts(page_title="Luwei"))
            .add("Value", new_data, "world", is_map_symbol_show=False)
            .set_series_opts(
            label_opts=opts.LabelOpts(is_show=False, ))
            .set_global_opts(
            visualmap_opts=opts.VisualMapOpts(),
            title_opts=opts.TitleOpts(title=info),
            toolbox_opts=opts.ToolboxOpts(),
        ))
    return c


# def geo_value(data):
#     new_data = list(zip(data[0], data[1]))
#     print(new_data)
#     new_data = [("河上", 100)]  # geo画图对于没有的地区无法绘图
#     c = (
#         Geo()
#             .add_schema(maptype="china")
#             .add(
#             "互联网普及率",
#             data_pair=new_data,
#             type_=ChartType.HEATMAP,
#         )
#             .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
#             .set_global_opts(
#             visualmap_opts=opts.VisualMapOpts(),
#             title_opts=opts.TitleOpts(title="2016中国分省互联网普及率热力图"),
#         )
#     )
#     return c


app = Flask(__name__)

regions_available, data3 = read_data3()
countries1, countries2, values1, values2 = read_data4()
df = pd.read_csv("existence_of_laws_on_domestic_violence_data.csv")


@app.route('/', methods=['GET'])
def hu_run_2019():
    data_str = df.to_html()
    return render_template('results2.html',
                           the_res=data_str,
                           the_select_region=regions_available)


@app.route('/hurun', methods=['POST'])
def hu_run_select() -> 'html':
    the_region = request.form["the_region_selected"]
    print(the_region)  # 检查用户输入
    data = data3[the_region]
    fig1, fig2 = map_violence(data)
    fig3 = map_value([countries1, values1], "48")
    fig4 = map_value([countries2, values2], "49")
    page = Page(layout=Page.SimplePageLayout)
    page.add(fig1, fig2, fig3, fig4)
    page.render("task.html")
    with open("task.html", encoding="utf8", mode="r") as f:
        plot_all = "".join(f.readlines())
    data_str = df.to_html()
    return render_template('results2.html',
                           the_plot_all=plot_all,
                           the_res=data_str,
                           the_select_region=regions_available,
                           )


if __name__ == '__main__':
    app.run(debug=True, port=8000)
