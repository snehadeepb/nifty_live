from nsepython import *
import seaborn as sns
import pandas as pd
import streamlit as st
from datetime import datetime
from time import gmtime, strftime
# from IPython.display import clear_output 
import matplotlib.pyplot as plt
from pytz import timezone 
from deta import Deta

def get_data():
    while True:
        try:
            data=nse_fno("NIFTY")
            last_prices=round(nse_quote_ltp("NIFTY"))
            break
        except:
            time.sleep(1)
    expiry=list(set(data['expiryDates']))
    expiry.sort(key = lambda date: datetime.strptime(date, '%d-%b-%Y'))
    if last_prices%100>50:
        x=(last_prices-last_prices%100+50)
        strike=[x-150,x-100,x-50,x,x+50,x+100,x+150]
    elif last_prices%100<=50:
        x=(last_prices-last_prices%100)
        strike=[x-150,x-100,x-50,x,x+50,x+100,x+150]
    d={'call IV':[],
        'call OI':[],
        '% change oi':[],
        'strike':[],
         '% change oi put':[],
        'put OI':[],
        'put IV':[],
         } 
    for i in data['stocks']:
        for nifty_strike in strike: 
            if i['metadata']['expiryDate']==expiry[0] and i['metadata']['optionType']=='Call' and i['metadata']['strikePrice']==nifty_strike:
                d['strike'].append(nifty_strike)
                d['call OI'].append(i['marketDeptOrderBook']['tradeInfo']['openInterest'])
                d['% change oi'].append(i['marketDeptOrderBook']['tradeInfo']['pchangeinOpenInterest'])
                d['call IV'].append(i['marketDeptOrderBook']['otherInfo']['impliedVolatility'])
            if i['metadata']['expiryDate']==expiry[0] and i['metadata']['optionType']=='Put' and i['metadata']['strikePrice']==nifty_strike:
                d['put OI'].append(i['marketDeptOrderBook']['tradeInfo']['openInterest'])
                d['% change oi put'].append(i['marketDeptOrderBook']['tradeInfo']['pchangeinOpenInterest'])
                d['put IV'].append(i['marketDeptOrderBook']['otherInfo']['impliedVolatility'])
    out=pd.json_normalize(d)
    out.fillna(0,inplace=True)
    try:
        out=out.explode(list(out.columns)).reset_index(drop=True)
    except:
        def pad_dict_list(dict_list, padel):
            lmax = 0
            for lname in dict_list.keys():
                lmax = max(lmax, len(dict_list[lname]))
            for lname in dict_list.keys():
                ll = len(dict_list[lname])
                if  ll < lmax:
                    dict_list[lname] += [padel] * (lmax - ll)
            return dict_list
        out = pad_dict_list(d, 0)
        out=pd.DataFrame(out)
        out.set_index(list(out.columns)).apply(pd.Series.explode).reset_index()
    
    x=out.astype(float).round(2)
    x.sort_values("strike", axis = 0, ascending = True,inplace = True)
    return x


def get_info(dataset):
    global all_day_data, today_date
    today_date =strftime("%d %b %Y", gmtime()),datetime.now(timezone("Asia/Kolkata")).strftime('%I.%M %p')
    df= pd.DataFrame(columns=[ 'pcr', 'cal_per','put_per'])
    value= dataset['put OI'].sum() - dataset['call OI'].sum()
    pcr= dataset['put OI'].sum()/dataset['call OI'].sum()
    cal_per= dataset['% change oi'].mean()
    put_per= dataset['% change oi put'].mean()
    # dirn=dataset['% change oi put']-dataset['% change oi']
    new_row={'time': today_date,'Diffn':round(value,2) ,'pcr':round(pcr,2), 'cal_per':round(cal_per,2), 'put_per':round(put_per,2)}
    df=pd.DataFrame(new_row,index=[0])
    putt,calll=abs(df['put_per'].tail(1).values),abs(df['cal_per'].tail(1).values)
    df['dirn']=putt-calll
    
    key ="d0svmmrabxg_cS1fKLgcAXt8JXhKM9YDyxeB9JcxnfA5"
    deta = Deta(key)
    db = deta.Base("LIVE_NIFTY")
    def insert_user(o_df):
        db.put(o_df)
    insert_user(new_row)
    key ="d0svmmrabxg_cS1fKLgcAXt8JXhKM9YDyxeB9JcxnfA5"
    deta = Deta(key)
    db = deta.Base("LIVE_NIFTY")
    today_date_fetching=strftime("%d %b %Y", gmtime())

    ml_data = db.fetch({"time?contains": today_date_fetching}) # gt greter then lt less then
    all_day_data=ml_data.items
    
    return df  


def ploting():
        try:
            global final
        except:
             df = pd.DataFrame(columns=['Diffn', 'pcr', 'cal_per','put_per'])
        dataset= get_data()
        main= get_info(dataset)
        main1=main[['Diffn', 'pcr', 'cal_per','put_per','time','dirn']]
        final=pd.concat([final,main1],ignore_index=True)
        
        return dataset,final

if __name__=='__main__':
    
    st.title('WELCOME BULLS CARTEL')
    st.header('WELCOME TO NIFTY 50')
    
    st.markdown(f"as at {today_date}")
    option= st.selectbox(
    'How would you like to be contacted?',
    ('5', '10', '15')) 
    st.write('You selected:', option)
    st.markdown('Important Information')
    st.markdown(""" CALL % INCREASE MEANS MARKET GOES DOWN  
             PUT % INCREASE MEANS MARKET GOES UP
             """)    
final = pd.DataFrame(columns=['Diffn', 'pcr', 'cal_per','put_per','time','dirn'])

while True:
    dataset,final=ploting()      
    p1=st.empty()
    p2=st.empty()
    p3=st.empty()
    p4=st.empty()
             # % change oi put
    p1.dataframe(dataset.style.highlight_max(['% change oi put','% change oi'],axis=0)) #Column hightlight 
    p2.dataframe(final.style.highlight_max(['cal_per','put_per'],axis=1)) # row highlight
    fig, ax = plt.subplots(figsize=(6, 2)) 
    ax.plot(final['time'],final['pcr'])
    ax.axhline(y=0, color='black', linestyle='solid') # 0 line graph
    fig.autofmt_xdate(rotation=70)
    p3.pyplot(fig)
    p4.dataframe(all_day_data)
    time.sleep(5*60) # how to the start again code check upper condition min * sec
    p1.empty() # then clean all data frame 
    p2.empty()
    p3.empty()
    p4.empty()
