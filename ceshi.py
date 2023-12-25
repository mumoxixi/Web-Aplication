import streamlit as st
import requests
import jieba
from collections import Counter

from bs4 import BeautifulSoup
from pyecharts import options as opts
from pyecharts.charts import WordCloud, Bar, Pie, Line, Radar, TreeMap, Funnel, Scatter
import streamlit_echarts
from streamlit_echarts import st_pyecharts
from collections import Counter
import re


# 用于处理文本的函数
def process_text(text):
    # Remove spaces, newlines, and punctuation
    text = text.replace(" ", "").replace("\n", "")
    # Tokenize the text using jieba
    words = jieba.cut(text)
    # Count word frequencies
    word_counts = Counter(words)
    # print(word_counts)
    return word_counts


# 使用pyecharts绘制不同图标的函数
def draw_chart(chart_type, word_counts):
    if chart_type == "折线图":
        chart = (
            Line().add_xaxis([word for word, count in word_counts.most_common(20)])
            .add_yaxis("词频", [count for word, count in word_counts.most_common(20)])
            .set_global_opts(title_opts=opts.TitleOpts(title="词频折线图"))

        )
        chart.render("line_chart.html")
        st.components.v1.html(open('line_chart.html', 'r', encoding='utf-8').read(), height=600 ,width=1000)
    elif chart_type == "饼图":
        chart = (
            Pie().add("", word_counts.most_common(20))
            # .set_global_opts(title_opts=opts.TitleOpts(title="词频饼状图"))
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        )

        chart.render("pie_chart.html")
        st.components.v1.html(open('pie_chart.html', 'r', encoding='utf-8').read(), height=600)

    elif chart_type == "条形图":
        chart = (
            Bar().add_xaxis([word for word, count in word_counts.most_common(20)])
            .add_yaxis("词频", [count for word, count in word_counts.most_common(20)])
            .set_global_opts(title_opts=opts.TitleOpts(title="词频条形图"))
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        )
        chart.render("bar_chart.html")
        st.components.v1.html(open('bar_chart.html', 'r', encoding='utf-8').read(), height=600 , width=1000)

    elif chart_type == "雷达图":
        words = [word for word, count in word_counts.most_common(20)]
        values = [count for word, count in word_counts.most_common(20)]
        chart = (
            Radar()
            .add_schema(schema=[
            opts.RadarIndicatorItem(name=word, max_=15) for word in words
        ])
            .add("中文字典雷达图", [values], areastyle_opts=opts.AreaStyleOpts(opacity=0.5))
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .render("radar_chart.html")
    )
        st.components.v1.html(open('radar_chart.html', 'r', encoding='utf-8').read(), height=600)

    elif chart_type == "散点图":
        chart = (
            Scatter()
            .add_xaxis([word for word, count in word_counts.most_common(20)])
            .add_yaxis("词频", [count for word, count in word_counts.most_common(20)])
            .set_global_opts(title_opts=opts.TitleOpts(title="词频散点图"))
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        )

        chart.render("scatter_chart.html")
        st.components.v1.html(open('scatter_chart.html', 'r', encoding='utf-8').read(), height=600, width=1000)

    elif chart_type == "词云图":
        chart = (
            WordCloud()
            .add("", list(word_counts.items()), word_size_range=[20, 100])
            .set_global_opts(title_opts=opts.TitleOpts(title="词云"))
            .render("wordcloud.html")
        )
        st.components.v1.html(open('wordcloud.html', 'r', encoding='utf-8').read(), height=600)
        # words = list(word_counts.keys())
        # values = list(word_counts.values())
        # chart = (
        #     WordCloud()
        #     .add("", zip(words, values), word_size_range=[20, 100], shape="circle")
        #     .set_global_opts(title_opts=opts.TitleOpts(title="词云图"))
        #     .render("wordcloud.html")
        # )
        # st.components.v1.html(open('wordcloud.html', 'r', encoding='utf-8').read(), height=600)

    # Add other chart types here...
    else:
        chart = (
            Bar()
            .add_xaxis(list(word_counts.keys()))
            .add_yaxis("词频", list(word_counts.values()))
            .set_global_opts(title_opts=opts.TitleOpts(title="默认图"))
        )
    return chart


# Streamlit app
def main():
    st.title("文本处理应用")

    # Get user input URL
    url = st.text_input("请输入文章URL:")

    if url:
        # Make HTTP request to get text content
        try:
            # 尝试建立连接或执行可能引发异常的代码
            response = requests.get(url)
            response.encoding = 'utf-8'
            response.raise_for_status()  # 抛出HTTP错误异常（如果有）

            # 处理成功的情况
            print('Connection successful!')
            print('Response:', response.text)

        except requests.exceptions.RequestException as e:
            # 捕获与连接相关的异常，并处理它们
            print('Error during connection:', e)

        except Exception as e:
            # 捕获其他异常（如果有），以便进行适当的处理
            print('An unexpected error occurred:', e)

        finally:
            # 无论是否发生异常，都可以在这里执行一些清理工作
            print('Execution completed.')

        if response.status_code == 200:
            # 使用BeautifulSoup解析网页
            response.encoding = response.apparent_encoding
            soup = BeautifulSoup(response.text, 'html.parser', from_encoding='utf-8')

            # 提取body标签中的内容
            # body_content = soup.find('body').get_text()
            text = soup.text
            # 3. 去除文本中的标点符号
            cleaned_text = re.sub(r'[^\w\s]', '', text)

            # Process text 流程文本
            word_counts = process_text(cleaned_text)

            # Sidebar for selecting different charts 用于选择不同图表的侧边栏
            st.sidebar.title("图型筛选")
            chart_type = st.sidebar.selectbox("选择图型:",
                                              ["折线图", "饼图", "条形图", "雷达图", "词云图", "散点图", "其他"])
            chart = draw_chart(chart_type, word_counts)
            # st_pyecharts(chart)

            # Filter low-frequency words 过滤低频词
            st.subheader("交互过滤低频词")
            threshold = st.slider("选择阈值:", 1, 10, 2)
            filtered_word_counts = {word: count for word, count in word_counts.items() if count >= threshold}
            counter_obj = Counter(filtered_word_counts)
            st_pyecharts(draw_chart("图", filtered_word_counts))

            # Display top 20 words 显示前20个单词
            st.write("词频排名前20的词汇:")
            most_common_elements = dict(counter_obj.most_common(20))
            # st.write(dict(filtered_word_counts.most_common(20)))
            st.write(most_common_elements)

        else:
            st.error("无法从提供的URL获取内容")


if __name__ == "__main__":
    main()
