import streamlit as st
import requests
import jieba
from collections import Counter

from bs4 import BeautifulSoup
from pyecharts import options as opts
from pyecharts.charts import WordCloud, Bar, Pie, Line, Radar, TreeMap, Funnel
import streamlit_echarts
from streamlit_echarts import st_pyecharts
from collections import Counter
import re


# Function to process text
def process_text(text):
    # Remove spaces, newlines, and punctuation
    text = text.replace(" ", "").replace("\n", "")
    # Tokenize the text using jieba
    words = jieba.cut(text)
    # Count word frequencies
    word_counts = Counter(words)
    # print(word_counts)
    return word_counts


# Function to draw different charts using pyecharts
def draw_chart(chart_type, word_counts):
    if chart_type == "柱状图":
        chart = (
            Bar()
            .add_xaxis(list(word_counts.keys()))
            .add_yaxis("词频", list(word_counts.values()))
            .set_global_opts(title_opts=opts.TitleOpts(title="柱状图"))
        )
    elif chart_type == "饼图":
        chart = (
            Pie()
            .add("", list(word_counts.items()))
            .set_global_opts(title_opts=opts.TitleOpts(title="饼图"))
        )
    elif chart_type == "折线图":
        chart = (
            Line()
            .add_xaxis(list(word_counts.keys()))
            .add_yaxis("Word Frequency", list(word_counts.values()))  # Provide a series name
            .set_global_opts(title_opts=opts.TitleOpts(title="折线图"))
        )

    elif chart_type == "雷达图":
        chart = (
            Radar()
            .add("", [list(word_counts.values())])  # Try different data formats if needed
            .add_schema(schema=[{"name": category} for category in word_counts.keys()])  # Add schema for categories
            .set_global_opts(title_opts=opts.TitleOpts(title="雷达图"))
        )

    elif chart_type == "漏斗图":
        chart = (
            Funnel()
            .add("", list(word_counts.items()))
            .set_global_opts(title_opts=opts.TitleOpts(title="漏斗图"))
        )
    elif chart_type == "词云图":
        chart = (
            WordCloud()
            .add("", list(word_counts.items()), word_size_range=[20, 100])
            .set_global_opts(title_opts=opts.TitleOpts(title="词云"))
        )

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

            # cleaned_text = re.sub(r'[^\u4e00-\u9fa5]', '', body_content)

            # Process text
            word_counts = process_text(cleaned_text)

            # Sidebar for selecting different charts
            st.sidebar.title("图型筛选")
            chart_type = st.sidebar.selectbox("选择图型:",
                                              ["柱状图", "饼图", "折线图", "雷达图", "词云图", "漏斗图", "其他"])
            chart = draw_chart(chart_type, word_counts)
            st_pyecharts(chart)

            # Filter low-frequency words
            st.subheader("交互过滤低频词")
            threshold = st.slider("选择阈值:", 1, 10, 2)
            filtered_word_counts = {word: count for word, count in word_counts.items() if count >= threshold}
            counter_obj = Counter(filtered_word_counts)
            st_pyecharts(draw_chart("图", filtered_word_counts))

            # Display top 20 words
            st.write("词频排名前20的词汇:")
            most_common_elements = dict(counter_obj.most_common(20))
            # st.write(dict(filtered_word_counts.most_common(20)))
            st.write(most_common_elements)
        else:
            st.error("无法从提供的URL获取内容")


if __name__ == "__main__":
    main()
