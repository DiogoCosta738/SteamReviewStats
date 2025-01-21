import matplotlib.pyplot as plt
import numpy as np
import datetime
import pandas as pd
import plotly
import plotly.graph_objects as go

def plot_stack(title, categories, groups, texts):
    # Create a Plotly Figure
    fig = go.Figure()

    idx = 0
    for group in groups:
    # Add traces for each group
        fig.add_trace(go.Bar(
            x=categories,
            y=group,
            text=[v for v in texts[idx]],  # Hover label
            hoverinfo='x+y+text',  # Tooltip format
            customdata = texts,
        ))
        idx += 1

    # Configure the layout for stacking bars
    fig.update_layout(
        barmode='stack',  # Stack the bars
        title=title,
        xaxis_title='Categories',
        yaxis_title='Values',
        legend_title='Groups',
    )

    fig.show()

def plot_bar(title, xx, data, texts):
    # Create a Plotly Figure
    fig = go.Figure()

    # Add traces for each group
    fig.add_trace(go.Bar(
        x=xx,
        y=data,
        text=texts,  # Hover label
        hoverinfo='x+y+text',  # Tooltip format
    ))

    # Configure the layout for stacking bars
    fig.update_layout(
        title=title,
        xaxis_title='Categories',
        yaxis_title='Values',
        legend_title='Groups',
    )

    fig.show()

def get_date_index(date, min_year):
    return (date.year - min_year) * 12 + (date.month - 1)

def get_index_date(index, min_year):
    year = index // 12
    month = index % 12 + 1
    return datetime.date(year = year + min_year, month = month, day = 1)

def sort_by_date(reviews):
    min_year = 99999
    max_year = 0
    for review in reviews:
        min_year = min(min_year, review["date"].year)
        max_year = max(max_year, review["date"].year)

    date_buckets = []
    for y in range(min_year, max_year + 1):
        for m in range(1, 12 + 1):
            date_buckets.append([])

    for review in reviews:
        y = review["date"].year
        m = review["date"].month
        index = get_date_index(review["date"], min_year)
        date_buckets[index].append(review)

    return date_buckets, min_year

def plot_wordcount_by_month(reviews):
    buckets, min_year = sort_by_date(reviews)

    categories = []

    max_reviews = 0
    for i in range(len(buckets)):
        date = get_index_date(i, min_year)
        categories.append(date.strftime("%b %Y"))
        max_reviews = max(max_reviews, len(buckets[i]))

    groups = [[0] * max_reviews for i in range(len(buckets))]
    print(len(groups))
    print(len(groups[0]))
    for i in range(len(buckets)):
        for j in range(len(buckets[i])):
            groups[i][j] = len(buckets[i][j]["text"])

    groups = []
    texts = []
    for j in range(max_reviews):
        groups.append([])
        texts.append([])
        for i in range(len(buckets)):
            if len(buckets[i]) > j:
                review = buckets[i][j]
                review_text = buckets[i][j]["text"]
                groups[j].append(len(review_text))
                texts[j].append(review["store-page"])
            else:
                groups[j].append(0)
                texts[j].append("")

    plot_stack("Review wordcount, by time of writing", categories, groups, texts)

def plot_helpful_by_month(reviews):
    buckets, min_year = sort_by_date(reviews)

    categories = []

    max_reviews = 0
    for i in range(len(buckets)):
        date = get_index_date(i, min_year)
        categories.append(date.strftime("%b %Y"))
        max_reviews = max(max_reviews, len(buckets[i]))

    groups = [[0] * max_reviews for i in range(len(buckets))]
    print(len(groups))
    print(len(groups[0]))
    for i in range(len(buckets)):
        for j in range(len(buckets[i])):
            groups[i][j] = len(buckets[i][j]["text"])

    groups = []
    texts = []
    for j in range(max_reviews):
        groups.append([])
        texts.append([])
        for i in range(len(buckets)):
            if len(buckets[i]) > j:
                review = buckets[i][j]
                groups[j].append(buckets[i][j]["helpful"])
                texts[j].append(review["store-page"])
            else:
                groups[j].append(0)
                texts[j].append("")

    plot_stack("Review helpful votes, by time of writing", categories, groups, texts)

def plot_by_helpful(reviews):
    max_helpful = 0
    for review in reviews:
        max_helpful = max(max_helpful, review["helpful"])

    xx = [i for i in range(max_helpful + 1)]
    data = [0 for i in range(max_helpful + 1)]
    texts = []
    for review in reviews:
        helpful_count = review["helpful"]
        data[helpful_count] += 1
        texts.append(review["store-page"])

    plot_bar("Number of reviews by 'helpful' vote count", xx, data, texts)
    return

def plot_by_wordcount(reviews):
    max_wordcount = 0
    for review in reviews:
        max_wordcount = max(max_wordcount, len(review["text"]))

    scale = 100
    xx = [i * scale  for i in range(max_wordcount // scale + 1)]
    data = [0 for i in range(max_wordcount // scale + 1)]
    texts = []
    for review in reviews:
        wordcount_idx = (len(review["text"]) // scale)
        data[wordcount_idx] += 1
        texts.append(review["store-page"])

    plot_bar("Number of reviews by wordcount", xx, data, texts)
    return