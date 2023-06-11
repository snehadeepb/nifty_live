from nsepython import *      #nsepython==0.0.972
import seaborn as sns
import pandas as pd     #1.5.2
import numpy as np
import streamlit as st   #1.22.0
from datetime import datetime    #5.0
from datetime import timedelta
import datetime
import pytz
from time import gmtime, strftime
# from IPython.display import clear_output 
import matplotlib.pyplot as plt
from pytz import timezone   #2023.3
from deta import Deta       #1.1.0
# from st_aggrid import AgGrid
import warnings
warnings.filterwarnings("ignore")
from pandas_datareader import data as pdr #0.10.0
import yfinance as yf  #0.2.18
import plotly.express as px
from statsmodels.tsa.arima.model import ARIMA

def get_data():
    a=None
    while a==None:
      try:
        a=(nse_fno("BANKNIFTY"))
        break
      except:
        time.sleep(40) 
    
#     a=(nse_fno("BANKNIFTY"))
    yf.pdr_override()
    nse_df = pdr.get_data_yahoo("^NSEBANK", period='1d', interval='5m')
    nse_df.index=[str(i).split('+')[0] for i in nse_df.index]

    global live_open1,last_prices,live_high,live_low,strike,live_time
    
#     json_string = json.dumps(nse_df)
#     json_value=json.loads(json_string)
#     nse_df=json_value

    live_data =nse_df.tail(1)
    live_time=nse_df.index[-1]
    live_open1=live_data['Open'][0].astype(int).round()
    live_high =live_data['High'][0].astype(int).round()
    live_low=live_data['Low'][0].astype(int).round()
    last_prices=live_data['Close'][0].astype(int).round()
   
    
#     print(open1,high, low , last_prices)
#     print(live_data)
    
#     price=(nse_quote_meta("BANKNIFTY","latest","Fut"))
    
#     open1=price['openPrice']
#     last_prices=round(price['lastPrice'])
#     high=price['highPrice']
#     low=price['lowPrice']
# #     print(open1,high,low,last_prices)
    
    exp=list(set(a['expiryDates']))
    exp.sort(key = lambda date: datetime.datetime.strptime(date, '%d-%b-%Y')) 
    if last_prices%100>50:
        x=(last_prices-last_prices%100+100)
        strike=[x-200,x-100,x,x+100,x+200]
    elif last_prices%100<50:
        x=(last_prices-last_prices%100)
        strike=[x-200,x-100,x,x+100,x+200]
    d={'call change op':[],
        'call vwap':[],
        '% change op':[],
        'strike':[],
        'put change op':[],
        'put vwap':[],
        '% change op put':[]
        }
    print("a")
#     print(a)
    for i in a['stocks']:
        for sp in strike: 
            if i['metadata']['expiryDate']==exp[0] and i['metadata']['optionType']=='Call' and i['metadata']['strikePrice']==sp:
                d['strike'].append(sp)
                d['call change op'].append(i['marketDeptOrderBook']['tradeInfo']['changeinOpenInterest'])
                d['% change op'].append(i['marketDeptOrderBook']['tradeInfo']['pchangeinOpenInterest'])
                d['call vwap'].append(i['marketDeptOrderBook']['tradeInfo']['vmap'])

            elif i['metadata']['expiryDate']==exp[0] and i['metadata']['optionType']=='Put' and i['metadata']['strikePrice']==sp:
                d['put change op'].append(i['marketDeptOrderBook']['tradeInfo']['changeinOpenInterest'])
                d['% change op put'].append(i['marketDeptOrderBook']['tradeInfo']['pchangeinOpenInterest'])
                d['put vwap'].append(i['marketDeptOrderBook']['tradeInfo']['vmap'])

    out=pd.json_normalize(d)
    
    out=out.explode(list(out.columns)).reset_index(drop = True)
    out.fillna(0,inplace=True)
    x=out.astype(float).round(2)
    x.sort_values("strike", axis = 0, ascending = True,inplace = True)
    return x
    
    
def get_info(dataset):
#     df= pd.DataFrame(columns=['value', 'pcr', 'cal_per','put_per'])
    value= dataset['put change op'].sum() - dataset['call change op'].sum()
    pcr= dataset['put change op'].sum()/dataset['call change op'].sum()
    cal_per= dataset['% change op'].mean()      #datetime.now(timezone("Asia/Kolkata")).strftime('%I.%M %p') time shoude change
    put_per= dataset['% change op put'].mean()  #datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S') 
    new_row={'time':live_time ,'value':value, 'pcr':round(pcr,2), 'cal_per':round(cal_per,2), 'put_per':round(put_per,2),'open': round(live_open1),'high':round(live_high),'low':round(live_low),'close':round(last_prices)}
#     df = df.append(new_row,ignore_index=True, verify_integrity=False, sort=None)
    pcr_dataset=pd.DataFrame(new_row,index=[0])
#     deta_key="d0iqnepq4nn_BgRSHUYswKQEwYxUJEFnFgH4FTfwm8EH"
#     deta = Deta(deta_key)
#     db = deta.Base("bullcartal1")
#     def insert_user(row):
#          return db.put(row)
#     insert_user(new_row)
    deta_key="d0mbmawwue1_vDAYaDS1qJR7ZWinqFrgXHg7BRusgoMY"
    deta = Deta(deta_key)
    db = deta.Base("raj")
    def insert_user(o_df):
        db.put(o_df)
    insert_user(new_row)

    return pcr_dataset 

def ploting():
        try:
            global final
        except:
             df = pd.DataFrame(columns=['value', 'pcr', 'cal_per','put_per'])
        dataset= get_data()
        main= get_info(dataset)
        main1=main[['value', 'pcr', 'cal_per','put_per','time']]
#         final =final.append(main1,ignore_index=True, verify_integrity=False, sort=None)
        final=pd.concat([final,main1],ignore_index=True)
        
        return dataset,final
def forecasting():
    deta_key="d0mbmawwue1_vDAYaDS1qJR7ZWinqFrgXHg7BRusgoMY"
    deta = Deta(deta_key)
    db = deta.Base("raj")
    ml_data=db.fetch(query=None, limit=None, last=None)
    ml_data=ml_data.items
    df=ml_data
    df=pd.DataFrame(df)
    df=df.drop(['put','key'],axis=1)
    df =df.set_index('time' )
    model=ARIMA(df['close'],order=(1,3,2))
    model_fit = model.fit()
    future = model_fit.forecast(11)
    future=np.round(future.values,2)
    fig = px.line(future, text=future)
    fig.update_layout(xaxis_title='Forecasting',title='Line plot banknifty forecast',yaxis_title='banknifty',)
    arima_fig=fig
    return arima_fig

    
global co,start_time,end_time,today,weekday,current_time
final = pd.DataFrame(columns=['value', 'pcr', 'cal_per','put_per','time'])
co=0
start_time = datetime.time(9, 13)  # Start time at 9:00 AM
end_time = datetime.time(15, 30)  # End time at 6:00 PM
today = datetime.date.today()
weekday = today.weekday() #saturday 5, 6 sunday
current_time =datetime.datetime.now(timezone("Asia/Kolkata")).strftime("%H:%M:%S")

if __name__=='__main__':
    
    st.title('WELCOME BULLS CARTEL')
#     current_date_web =strftime("%d %b %Y", gmtime()),datetime.now(timezone("Asia/Kolkata")).strftime('%I.%M %p')
    st.markdown(f"as at {today,current_time}")
    option= st.selectbox(
    'How would you like to be contacted?',
    ('5', '10', '15')) 
    st.write('You selected:', option)
    st.header('Important Information')
    st.markdown(""" CALL % INCREASE MEANS MARKET GOES DOWN  
             PUT % INCREASE MEANS MARKET GOES UP
             """)    
    st.title('banknifty forecast ')
    result=st.button('Click here', key=co,type= "primary" )
    co+=1
    st.write(result)
    while True:
        if str(start_time) <= current_time <= str(end_time) and weekday not in (5,6):
            
            dataset,final=ploting()
            p1=st.empty()
            p2=st.empty()
            p3=st.empty()
            p4=st.empty()
            p1.dataframe(dataset.style.highlight_max(['% change op put','% change op'],axis=0)) #Column hightlight 
            p2.write(final[:100])
            fig, ax = plt.subplots(figsize=(6, 2)) 
            ax.plot(final['time'],final['pcr'])
            ax.axhline(y=0, color='black', linestyle='solid') # 0 line graph
            fig.autofmt_xdate(rotation=70)
            p3.pyplot(fig)

            if result:
                st.write(':smile:')
                p4.write(forecasting())

    #         p4.write(forecasting())
            time.sleep(5*60) # how to the start again code check upper condition min * sec
            p1.empty() # then clean all data frame 
            p2.empty()
            p3.empty()
            p4.empty()
        else:
            now = datetime.datetime.now()
            # print(now)
            target_time = datetime.datetime(now.year, now.month, now.day, 9, 15, 0) + datetime.timedelta(days=1)
            # print(target_time)
            wait_seconds = (target_time - now).total_seconds()
            # print(wait_seconds)
            st.markdown('Today, the stock market is closed. We kindly request you to join us tomorrow at 9:15 am when trading resumes. Thank you for your understanding.')
            time.sleep(wait_seconds)
