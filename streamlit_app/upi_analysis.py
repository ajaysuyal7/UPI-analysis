import streamlit as st
import pandas as pd
import plotly.express as px
from login import login


@st.cache_data
def load_data():
    return pd.read_csv("upi_transactions_2024.csv")

filtered_df = load_data()
st.session_state.df = filtered_df

def human_format(num):
    if num >= 1_000_000:
        return f"{num/1_000_000:.2f}M"
    elif num >= 1_000:
        return f"{num/1_000:.2f}K"
    else:
        return str(num)



#--loging page
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    
if not st.session_state.logged_in:
    login()
    st.stop()
else:
    with st.sidebar:
        st.markdown(f"👤 Logged in as: **{st.session_state.get('username', 'User')}**")
        if st.button("Logout"):
            st.session_state.clear()
            st.success("Logged out. Please reload to log in again.")
            st.stop()

    
    st.title("UPI Transactions Analysis")

    st.markdown("## 📊 UPI Transactions Overview")

    filtered_df['timestamp'] = pd.to_datetime(filtered_df['timestamp'])
    filtered_df['month'] = filtered_df['timestamp'].dt.month_name()


    # KPI calculations

    st.sidebar.header(" Filter")

    merchant_filter = st.sidebar.multiselect("Merchant category",options= filtered_df["merchant_category"].dropna().unique())
    device_filter = st.sidebar.multiselect("Device Type",options= filtered_df["device_type"].dropna().unique())
    transactionfilter = st.sidebar.multiselect("transaction type",options= filtered_df["transaction type"].dropna().unique())
    sender_filter = st.sidebar.multiselect("Sender Bank",options= filtered_df["sender_bank"].dropna().unique())
    month_filter= st.sidebar.multiselect("Month",options= filtered_df["month"].dropna().unique())
    weekend_filter= st.sidebar.multiselect("Weekend(1)/Weekday(0)",options= filtered_df["is_weekend"].dropna().unique())


    filtered_df=filtered_df.copy()

    with st.expander("Filters", expanded=False):
        if merchant_filter:
            filtered_df = filtered_df[filtered_df["merchant_category"].isin(merchant_filter)]
        if device_filter:
            filtered_df = filtered_df[filtered_df["device_type"].isin(device_filter)]
        if transactionfilter:
            filtered_df = filtered_df[filtered_df["transaction type"].isin(transactionfilter)]
        if sender_filter:
            filtered_df = filtered_df[filtered_df["sender_bank"].isin(sender_filter)]
        if month_filter:
            filtered_df = filtered_df[filtered_df["month"].isin(month_filter)]
        if weekend_filter:
            filtered_df = filtered_df[filtered_df["is_weekend"].isin(weekend_filter)]
        
    tab1,tab2= st.tabs(["Upi transaction overview","upi fraud Analysis"])

    with tab1:
        if filtered_df.empty:
            st.warning("No data available for the selected filters. Please adjust your filter criteria.")
        else:
            st.title("UPI Transactions Overview")
            total_transactions = filtered_df.shape[0]
            total_amount= filtered_df['amount (INR)'].sum()
            Avg_amount = filtered_df['amount (INR)'].mean()
            total_successful_transaction = filtered_df[filtered_df['transaction_status'] == 'SUCCESS'].shape[0]
            total_failed_transaction = filtered_df[filtered_df['transaction_status'] =='FAILED'].shape[0]

            # Display KPIs in columns
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Total Transactions", human_format(total_transactions))
            col2.metric("Total Amount (INR)", human_format(total_amount))
            col3.metric("Avg. Transaction Amount (INR)", f"{Avg_amount:.2f}")
            col4.metric("Successful Transactions", human_format(total_successful_transaction))
            col5.metric("Failed Transactions", human_format(total_failed_transaction))

            # Time series plot for transactions over time
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### Transactions Over Time")
                transactions_over_time = filtered_df.groupby('month').size().reset_index(name='count')
                fig = px.line(transactions_over_time, x='month', y='count', markers=True,title='Transactions Over Time')
                fig.update_layout(xaxis_title='Month', yaxis_title='Number of Transactions')
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.markdown("### Transaction Amount Over Time")
                amount_over_time = filtered_df.groupby('month')['amount (INR)'].sum().reset_index()
                fig = px.bar(amount_over_time, x='month', y='amount (INR)', title='Transaction Amount Over Time')
                fig.update_layout(xaxis_title='Month', yaxis_title='Total Amount (INR)')
                st.plotly_chart(fig, use_container_width=True)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### Transactions by time of day")
                transactions_over_time = filtered_df.groupby('hour_of_day').size().reset_index(name='count')
                fig = px.line(transactions_over_time, x='hour_of_day', y='count',markers=True, title='Transactions by time of day')
                fig.update_layout(xaxis_title='Hour of Day', yaxis_title='Number of Transactions')
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.markdown("### Transaction by sender age group")
                transaction_by_age=filtered_df.groupby('sender_age_group').size().reset_index(name='count')
                fig = px.bar(transaction_by_age, x='sender_age_group', y='count', title='Transaction by sender age group')
                fig.update_layout(xaxis_title='Sender Age Group', yaxis_title='Number of Transactions')
                st.plotly_chart(fig, use_container_width=True)


            transactions_by_sender = filtered_df['sender_state'].value_counts().reset_index()
            # Create treemap
            fig = px.treemap(
                transactions_by_sender,
                path=['sender_state'],values='count',title='Transactions by Sender State'
            )
            fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
            if filtered_df.empty:
                st.warning('No data avaliable for the selected filter')
            else:
                st.title('Upi Frsud transaction overview')

                total_fraud_transaction=filtered_df[filtered_df['fraud_flag']==1].shape[0]
                total_fraud_transaction_amount=filtered_df[filtered_df['fraud_flag']==1]['amount (INR)'].sum()
                total_fraud_transaction_percent=(total_fraud_transaction/total_transactions)*100
                total_successful_transaction_amount=filtered_df[filtered_df['transaction_status']=='SUCCESS']['amount (INR)'].sum()
                fraud_transaction_percent_amount=(total_fraud_transaction_amount/total_amount)*100
            
                # Display KPi's

                col1, col2, col3= st.columns(3)
                col4, col5 = st.columns(2)

                col1.metric("Total Fraud Transactions", human_format(total_fraud_transaction))
                col2.metric("Total Fraud Amount (INR)", human_format(total_fraud_transaction_amount))
                col3.metric("Fraud Transactions (%)", f"{total_fraud_transaction_percent:.2f}%")
                col4.metric("Successful Transaction Amount (INR)", human_format(total_successful_transaction_amount))
                col5.metric("Fraud Amount (%)", f"{fraud_transaction_percent_amount:.2f}%")

                col1, col2 = st.columns(2)

                with col1:
                    fraud_over_time = filtered_df[filtered_df['fraud_flag'] == 1].groupby('hour_of_day').size().reset_index(name='count')
                    fig = px.line(fraud_over_time, x='hour_of_day', y='count', markers=True, title='Fraud Transactions Over Time')
                    fig.update_layout(xaxis_title='Hour', yaxis_title='Number of Fraud Transactions')
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    fraud_transaction_success_status = filtered_df[filtered_df['fraud_flag'] == 1]['transaction_status'].value_counts().reset_index()
                    fig = px.pie(fraud_transaction_success_status, names='transaction_status', values='count', title='Fraud Transactions by Status')
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig, use_container_width=True)

                fraud_transaction_by_time=filtered_df[filtered_df['fraud_flag']==1].groupby('hour_of_day').size().reset_index(name='count')
                fig = px.treemap(
                    fraud_transaction_by_time,
                    path=['hour_of_day'],values='count',title='fraud transactions by time'
                )
                fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))
                st.plotly_chart(fig, use_container_width=True)
