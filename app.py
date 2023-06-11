from nsepython import *
import seaborn as sns
import pandas as pd
import streamlit as st
from datetime import datetime
from time import gmtime, strftime
from IPython.display import clear_output 
import matplotlib.pyplot as plt
from pytz import timezone 


def get_data():
    while True:
        try:
            data=nse_fno("NIFTY")
        # data
            last_prices=round(nse_quote_ltp("NIFTY"))
        # print(last_prices)
            break
        except:
            time.sleep(10)
#     data=nse_fno("NIFTY")
#     last_prices=round(nse_quote_ltp("NIFTY"))

    data['stocks']
    expiry=list(set(data['expiryDates']))
    expiry.sort(key = lambda date: datetime.strptime(date, '%d-%b-%Y'))
    if last_prices%100>50:
        x=(last_prices-last_prices%100+50)
        strike=[x-150,x-100,x-50,x,x+50,x+100,x+150]
    elif last_prices%100<=50:
        x=(last_prices-last_prices%100)
        strike=[x-150,x-100,x-50,x,x+50,x+100,x+150]
    d={'call OI':[],
        'call IV':[],
        '% change oi':[],
        'strike':[],
        'put OI':[],
        'put IV':[],
        '% change oi put':[] ,} 
    for i in data['stocks']:
        for nifty_strike in strike: 
            if i['metadata']['expiryDate']==expiry[0] and i['metadata']['optionType']=='Call' and i['metadata']['strikePrice']==nifty_strike:
                d['strike'].append(nifty_strike)
                d['call OI'].append(i['marketDeptOrderBook']['tradeInfo']['openInterest'])
                d['% change oi'].append(i['marketDeptOrderBook']['tradeInfo']['pchangeinOpenInterest'])
                d['call IV'].append(i['marketDeptOrderBook']['otherInfo']['impliedVolatility'])
            elif i['metadata']['expiryDate']==expiry[0] and i['metadata']['optionType']=='Put' and i['metadata']['strikePrice']==nifty_strike:
                d['put OI'].append(i['marketDeptOrderBook']['tradeInfo']['openInterest'])
                d['% change oi put'].append(i['marketDeptOrderBook']['tradeInfo']['pchangeinOpenInterest'])
                d['put IV'].append(i['marketDeptOrderBook']['otherInfo']['impliedVolatility'])
    out=pd.json_normalize(d)
    out=out.explode(list(out.columns)).reset_index(drop = True)
    out.fillna(0,inplace=True)
    x=out.astype(float).round(2)
    x.sort_values("strike", axis = 0, ascending = True,inplace = True)
    return x
# print(get_data())
# dataset=get_data()
def get_info(dataset):
    df= pd.DataFrame(columns=[ 'pcr', 'cal_per','put_per'])
    value= dataset['put OI'].sum() - dataset['call OI'].sum()
    pcr= dataset['put OI'].sum()/dataset['call OI'].sum()
    cal_per= dataset['% change oi'].mean()
    put_per= dataset['% change oi put'].mean()
    new_row={'time':datetime.now(timezone("Asia/Kolkata")).strftime('%I.%M %p'),'Diffn':round(value,2) ,'pcr':round(pcr,2), 'cal_per':round(cal_per,2), 'put_per':round(put_per,2)}
    df = df.append(new_row,ignore_index=True, verify_integrity=False, sort=None)
    return df  


def ploting():
        try:
            global final
        except:
             df = pd.DataFrame(columns=['Diffn', 'pcr', 'cal_per','put_per'])
        dataset= get_data()
        main= get_info(dataset)
        main1=main[['Diffn', 'pcr', 'cal_per','put_per','time']]
#         final =final.append(main1,ignore_index=True, verify_integrity=False, sort=None)
        final=pd.concat([final,main1],ignore_index=True)
        
        return dataset,final

if __name__=='__main__':
    
    st.title('WELCOME BULLS CARTEL')
    today_date =strftime("%d %b %Y", gmtime()),datetime.now(timezone("Asia/Kolkata")).strftime('%I.%M %p')
    st.markdown(f"as at {today_date}")
    option= st.selectbox(
    'How would you like to be contacted?',
    ('5', '10', '15')) 
    st.write('You selected:', option)
    st.header('Important Information')
    st.markdown(""" CALL % INCREASE MEANS MARKET GOES DOWN  
             PUT % INCREASE MEANS MARKET GOES UP
             """)    
final = pd.DataFrame(columns=['Diffn', 'pcr', 'cal_per','put_per','time'])

while True:
            dataset,final=ploting()      
            p1=st.empty()
            p2=st.empty()
            p3=st.empty()
                     # % change oi put
            p1.dataframe(dataset.style.highlight_max(['% change oi put','% change oi'],axis=0)) #Column hightlight 
            p2.dataframe(final.style.highlight_max(['cal_per','put_per'],axis=1)) # row highlight
            fig, ax = plt.subplots(figsize=(6, 2)) 
            ax.plot(final['time'],final['pcr'])
            ax.axhline(y=0, color='black', linestyle='solid') # 0 line graph
            fig.autofmt_xdate(rotation=70)
            p3.pyplot(fig)
            time.sleep(5*60) # how to the start again code check upper condition min * sec
            p1.empty() # then clean all data frame 
            p2.empty()
            p3.empty()
