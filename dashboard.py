import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import os
sns.set(style='dark')

def create_daily_orders_df(df):
    daily_orders = df.resample(rule='D',on='order_date').agg({
        "order_id":"nunique",
        "total_price":"sum"
    })
    daily_orders = daily_orders.reset_index()
    daily_orders.rename(columns={
        "order_id":"order_count",
        "total_price":"revenue"
    },inplace=True)

    return daily_orders

def create_sum_order_items_df(df):
    sum_order_items = df.groupby('product_name').quantity_x.sum().sort_values(ascending=False).reset_index()
    return sum_order_items

def create_bygender_df(df):
    bygender = df.groupby(by='gender').customer_id.nunique().reset_index()
    bygender.rename(columns={
        'customer_id':'customer_count'
    },inplace=True)

    return bygender

def create_byage_df(df):
    byage = df.groupby(by='age_group').customer_id.nunique().reset_index()
    byage.rename(columns={
        'customer_id':'customer_count'
    },inplace=True)
    byage['age_group'] = pd.Categorical(byage['age_group'],categories=['Youth','Adults','Seniors'],ordered=True)

    return byage

def create_bystate_df(df):
    bystate = df.groupby(by='state').customer_id.nunique().reset_index()
    bystate.rename(columns={
        'customer_id':'customer_count'
    },inplace=True)

    return bystate

def create_rfm_df(df):
    rfm = df.groupby(by='customer_id',as_index=False).agg({
        'order_date':'max', # mengambil tanggal terakhir transaksi
        'order_id':'nunique',
        'total_price':'sum'
    })
    rfm.columns = ['customer_id','max_order_timestamp','frequency','monetary']

    rfm['max_order_timestamp'] = rfm['max_order_timestamp'].dt.date
    recent_date = df['order_date'].dt.date.max()
    rfm['recency'] = rfm['max_order_timestamp'].apply(lambda x: (recent_date - x).days)
    rfm.drop(columns='max_order_timestamp',axis=1,inplace=True)

    return rfm

file_path = os.path.join(os.path.dirname(__file__), 'all.csv')
all_df = pd.read_csv(file_path)

datetime_columns = ['order_date','delivery_date']
all_df.sort_values(by='order_date',inplace=True)
all_df.reset_index(inplace=True)

for col in datetime_columns:
    all_df[col] = pd.to_datetime(all_df[col])

min_date = all_df['order_date'].min()
max_date = all_df['order_date'].max()

with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    start_date,end_date = st.date_input(label="Rentang Waktu",min_value=min_date,max_value=max_date,value=(min_date,max_date))

# Convert start_date and end_date to datetime
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

main_df = all_df[(all_df['order_date'] >= start_date) & 
                 (all_df['order_date'] <= end_date)]

daily_orders = create_daily_orders_df(main_df)
sum_order_items = create_sum_order_items_df(main_df)
bygender = create_bygender_df(main_df)
byage = create_byage_df(main_df)
bystate = create_bystate_df(main_df)
rfm = create_rfm_df(main_df)

st.header('Dicoding Collection Dashboard :sparkles:')

st.subheader('Daily Orders')
col1, col2 = st.columns(2)

with col1:
    total_order = daily_orders['order_count'].sum()
    st.metric(label='Total Order', value=total_order)

with col2:
    total_revenue = format_currency(daily_orders['revenue'].sum(), 'AUD', locale='es_CO')
    st.metric(label='Total Revenue', value=total_revenue)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders['order_date'],
    daily_orders['order_count'],
    marker='o',
    linewidth=2,
    color='#90CAF9'
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

# Product Performance
st.subheader('Product Performance')

fig, ax = plt.subplots(figsize=(35, 15))

colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x='quantity_x', y='product_name', data=sum_order_items.head(), palette=colors, ax=ax)
ax.set_ylabel(None)
ax.set_xlabel('Quantity Sold')
ax.set_title('Top 5 Best Performing Products', loc='center', fontsize=50)
ax.tick_params(axis='y', labelsize=35)
ax.tick_params(axis='x', labelsize=30)

st.pyplot(fig)

bygender = main_df.groupby('gender').size().reset_index(name='count')
byage = main_df.groupby('age_group').size().reset_index(name='count')
bystate = main_df.groupby('state').size().reset_index(name='customer_count')

# Customer Demographics
st.subheader("Customer Demographics")

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(20, 10))

    sns.barplot(
        y="count", 
        x="gender",
        data=bygender.sort_values(by="count", ascending=False),
        palette=colors,
        ax=ax
    )
    ax.set_title("Number of Customer by Gender", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(20, 10))
    
    colors = ["#D3D3D3", "#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

    sns.barplot(
        y="count", 
        x="age_group",
        data=byage.sort_values(by="age_group", ascending=False),
        palette=colors,
        ax=ax
    )
    ax.set_title("Number of Customer by Age", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)

fig, ax = plt.subplots(figsize=(20, 10))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x="customer_count", 
    y="state",
    data=bystate.sort_values(by="customer_count", ascending=False),
    palette=colors,
    ax=ax
)
ax.set_title("Number of Customer by State", loc="center", fontsize=50)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='x', labelsize=35)
ax.tick_params(axis='y', labelsize=30)
st.pyplot(fig)

# Best Customer Based on RFM Parameters
st.subheader("Best Customer Based on RFM Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm['recency'].mean(), 1)
    st.metric(label='Average Recency', value=avg_recency)

with col2:
    avg_frequency = round(rfm['frequency'].mean(), 2)
    st.metric(label='Average Frequency', value=avg_frequency)

with col3:
    avg_monetary = format_currency(rfm['monetary'].mean(), 'AUD', locale='es_CO')
    st.metric(label='Average Monetary', value=avg_monetary)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(y="recency", x="customer_id", data=rfm.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)

sns.barplot(y="frequency", x="customer_id", data=rfm.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)

sns.barplot(y="monetary", x="customer_id", data=rfm.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_id", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35)

st.pyplot(fig)
